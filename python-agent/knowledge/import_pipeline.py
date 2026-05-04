"""
Shared import pipeline: upload to MinIO, insert into PostgreSQL, vectorize via DashScope.
"""
import sys, os, uuid, json, time
from io import BytesIO
import psycopg2
from minio import Minio
from dashscope import MultiModalEmbedding
from settings_helper import configure_dashscope_api_key

RUNTIME_CONFIG = configure_dashscope_api_key()


DB_CONFIG = RUNTIME_CONFIG.postgres.model_dump()
MINIO_CONFIG = RUNTIME_CONFIG.minio.model_dump(exclude={"bucket"})
BUCKET = RUNTIME_CONFIG.minio.bucket


def connect_db():
    return psycopg2.connect(**DB_CONFIG)


def connect_minio():
    return Minio(MINIO_CONFIG["endpoint"], access_key=MINIO_CONFIG["access_key"],
                 secret_key=MINIO_CONFIG["secret_key"], secure=MINIO_CONFIG["secure"])


def ensure_bucket(client, bucket):
    if not client.bucket_exists(bucket):
        client.make_bucket(bucket)


def upload_file(client, bucket, resource):
    sn = resource["title"].replace("/", "-").replace(" ", "_")
    uid = uuid.uuid4().hex[:8]
    object_key = f"resources/{uid}_{sn}.md"
    content_bytes = resource["content"].encode("utf-8")
    data = BytesIO(content_bytes)
    client.put_object(bucket, object_key, data, len(content_bytes), content_type="text/markdown")
    return object_key, len(content_bytes)


def gen_embeddings(texts, dim=RUNTIME_CONFIG.embedding_dimension):
    inp = [{"text": t} for t in texts]
    resp = MultiModalEmbedding.call(model=RUNTIME_CONFIG.embedding_model_name, input=inp, dimension=dim, output_type="dense")
    if resp.status_code != 200:
        raise RuntimeError(f"Embedding API error: {resp.code} {resp.message}")
    return [e["embedding"] for e in sorted(resp.output.get("embeddings", []), key=lambda x: x.get("index", 0))]


def emb_str(vec):
    return "[" + ",".join(str(v) for v in vec) + "]"


def run_import(resources, label="batch"):
    """Main import pipeline: upload -> insert -> vectorize."""
    dry = "--dry-run" in sys.argv
    print(f"[{label}] {len(resources)} resources")
    if dry:
        for r in resources:
            print(f"  [{r['type']:8s}] {r['title']}")
        return

    minio_client = connect_minio()
    ensure_bucket(minio_client, BUCKET)
    conn = connect_db()

    try:
        with conn:
            with conn.cursor() as cur:
                # Step 0: Filter out existing titles
                cur.execute("SELECT title FROM app.learning_resource")
                existing_titles = {row[0] for row in cur.fetchall()}
                before = len(resources)
                resources = [r for r in resources if r["title"] not in existing_titles]
                skipped = before - len(resources)
                if skipped:
                    print(f"  [{label}] Skipped {skipped} duplicates, {len(resources)} remaining")

                # Step 1: Upload to MinIO
                object_ids = {}
                for r in resources:
                    object_key, size = upload_file(minio_client, BUCKET, r)
                    oid = str(uuid.uuid4())
                    cur.execute(
                        "INSERT INTO storage.resource_object (id,provider,bucket_name,object_key,file_name,mime_type,size_bytes,access_mode,storage_url) "
                        "VALUES (%s,'RUSTFS',%s,%s,%s,'text/markdown',%s,'PRESIGNED',%s)",
                        (oid, BUCKET, object_key, f"{r['title'].replace('/','-')}.md", size, f"minio://{BUCKET}/{object_key}"))
                    object_ids[r["title"]] = oid
                print(f"  [{label}] Uploaded {len(resources)} to MinIO")

                # Step 2: Insert learning_resource and resource_document
                resource_ids = {}
                doc_ids = {}
                for r in resources:
                    lid = str(uuid.uuid4())
                    cur.execute(
                        "INSERT INTO app.learning_resource (id,title,domain,resource_type,difficulty_level,source_kind,access_scope,summary_text,tags,metadata_json,storage_object_id,status) "
                        "VALUES (%s,%s,'COMPUTER_SCIENCE',%s::app.resource_type,%s::app.difficulty_level,'IMPORTED'::app.source_kind,'GLOBAL'::app.access_scope,%s,%s,%s,%s,'ACTIVE')",
                        (lid, r["title"], r["type"], r["difficulty"], r["description"],
                         json.dumps(r["tags"], ensure_ascii=False),
                         json.dumps({"course": r["course"], "chapter": r["chapter"], "source_url": r["source_url"]}, ensure_ascii=False),
                         object_ids.get(r["title"])))
                    resource_ids[r["title"]] = lid

                for r in resources:
                    rd = str(uuid.uuid4())
                    cur.execute(
                        "INSERT INTO rag.resource_document (id,resource_id,title,domain,resource_type,difficulty_level,source_kind,source_ref,summary_text,access_scope,metadata_json) "
                        "VALUES (%s,%s,%s,'COMPUTER_SCIENCE',%s::app.resource_type,%s::app.difficulty_level,'IMPORTED'::app.source_kind,%s,%s,'GLOBAL'::app.access_scope,%s)",
                        (rd, resource_ids[r["title"]], r["title"], r["type"], r["difficulty"],
                         r["source_url"], r["description"],
                         json.dumps({"course": r["course"], "chapter": r["chapter"]}, ensure_ascii=False)))
                    doc_ids[r["title"]] = rd
                print(f"  [{label}] Created {len(resources)} DB entries")

                # Step 3: Vectorize in batches of 5
                descriptions = [r["description"] for r in resources]
                failed = 0
                for batch_start in range(0, len(resources), 5):
                    batch_resources = resources[batch_start:batch_start + 5]
                    batch_descs = descriptions[batch_start:batch_start + 5]
                    try:
                        embs = gen_embeddings(batch_descs)
                    except Exception as e:
                        print(f"  [{label}] Batch [{batch_start+1}] error: {e}, retrying one-by-one...")
                        embs = []
                        for d in batch_descs:
                            try:
                                embs.extend(gen_embeddings([d]))
                            except Exception:
                                embs.append(None)
                                failed += 1
                            time.sleep(0.5)
                    for j, r in enumerate(batch_resources):
                        ev = embs[j] if j < len(embs) and embs[j] is not None else None
                        if ev is None:
                            continue
                        cur.execute(
                            "INSERT INTO rag.resource_chunk (document_id,resource_id,chunk_no,content,embedding,token_count,domain,resource_type,difficulty_level,access_scope,quality_score,metadata_json) "
                            "VALUES (%s,%s,1,%s,%s,%s,'COMPUTER_SCIENCE',%s::app.resource_type,%s::app.difficulty_level,'GLOBAL'::app.access_scope,0.90,%s)",
                            (doc_ids[r["title"]], resource_ids[r["title"]], r["description"],
                             emb_str(ev), int(len(r["description"]) / 1.5), r["type"], r["difficulty"],
                             json.dumps({"course": r["course"], "chapter": r["chapter"]}, ensure_ascii=False)))
                    print(f"  [{label}] Vectorized [{min(batch_start + 5, len(resources))}/{len(resources)}]")
                    time.sleep(0.3)
                if failed:
                    print(f"  [{label}] Warning: {failed} embedding failures")
    finally:
        conn.close()
    print(f"  [{label}] Done. {len(resources)} resources imported.")

