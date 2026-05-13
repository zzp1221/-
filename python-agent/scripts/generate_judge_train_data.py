"""
Step 1: Generate 50 labeled samples for judge model fine-tuning.
Sources knowledge points from 986 wiki pages, creates 3 answer variants each,
and labels them using the current LLM evaluator.

Usage:
  python scripts/generate_judge_train_data.py          # 50 samples (default)
  python scripts/generate_judge_train_data.py --N 500  # 500 samples
  python scripts/generate_judge_train_data.py --inspect # inspect 5 samples only
"""
import asyncio, json, random, sys, os, uuid
from collections import defaultdict
from typing import Any

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import psycopg2

from src.ai_modules.llms.judge_subjective_evaluator import (
    OpenAICompatibleSubjectiveJudgeEvaluator,
)
from src.ai_modules.models.practice import PracticeQuestion, SubjectiveJudgeEvaluation

# ── Config ──
OUTPUT = os.path.join(os.path.dirname(__file__), "..", "judge_train_data.json")
SAMPLE_N = 50
DB = {
    "host": "localhost", "port": 5432, "dbname": "zhixue",
    "user": "postgres", "password": "123456",
}


# ── Knowledge extraction ──

def extract_knowledge_points() -> list[dict]:
    """Extract facts from wiki pages as {'stem','answer','course','chapter','heading'}."""
    conn = psycopg2.connect(**DB)
    cur = conn.cursor()
    cur.execute("""
        SELECT title, frontmatter_json->>'course' AS course,
               frontmatter_json->>'chapter' AS chapter,
               markdown_content
        FROM rag.wiki_page
        WHERE is_active = true AND markdown_content IS NOT NULL
        ORDER BY random()
    """)
    points: list[dict] = []
    for title, course, chapter, content in cur.fetchall():
        sections = _split_sections(content)
        for heading, body in sections:
            if not any(kw in heading for kw in [
                "核心定义", "关键结论", "易错点", "定义",
                "关键机制", "核心要点", "算法原理"
            ]):
                continue
            for sent in body.replace("\n", "").split("。"):
                sent = sent.strip() + "。"
                if not (80 <= len(sent) <= 700):
                    continue
                # Skip bullet-point or list-format answers
                if sent.lstrip().startswith(("-", "*", "•", "1.", "2.")):
                    continue
                stem = _make_stem(course or title, chapter or heading, heading, sent)
                points.append({
                    "course": course or title,
                    "chapter": chapter or heading,
                    "heading": heading,
                    "stem": stem,
                    "answer": sent,
                })
    conn.close()
    return points


def _split_sections(md: str) -> list[tuple[str, str]]:
    """Split markdown by ## headings. Returns [(heading, body), ...]."""
    sections = []
    lines = md.split("\n")
    current_heading = ""
    current_body: list[str] = []
    for line in lines:
        if line.startswith("## "):
            if current_heading:
                sections.append((current_heading, "\n".join(current_body)))
            current_heading = line[3:].strip()
            current_body = []
        else:
            current_body.append(line)
    if current_heading:
        sections.append((current_heading, "\n".join(current_body)))
    return sections


def _make_stem(course: str, chapter: str, heading: str, answer: str) -> str:
    """Create a natural question stem from the knowledge point context."""
    first_sent = answer.split("。")[0][:120]
    key_term = first_sent.lstrip("0123456789. *-•")
    if "定义" in heading or "核心" in heading:
        return f"请解释{key_term[:60]}的含义，并举例说明其应用场景。（{course} - {chapter}）"
    elif "结论" in heading or "关键" in heading:
        return f"关于{key_term[:60]}，请总结其核心要点并说明为什么这个结论重要。（{course} - {chapter}）"
    elif "易错" in heading:
        return f"在学习{key_term[:60]}时常见的误区是什么？请指出错误理解并给出正确解释。（{course} - {chapter}）"
    elif "算法" in heading or "机制" in heading:
        return f"请描述{key_term[:60]}的核心流程或工作原理。（{course} - {chapter}）"
    else:
        return f"请解释{key_term[:60]}的概念并举例说明。（{course} - {chapter}）"


# ── Answer variant generation ──

def make_answer_variants(answer: str) -> list[dict]:
    """
    Generate 3 student answer variants:
      - type=correct: paraphrase, keep meaning intact
      - type=partial: keep core concept but omit key detail/edge case
      - type=wrong: flip or confuse a core relationship
    """
    variants = []

    # ── correct ──
    variants.append({
        "type": "correct",
        "text": _paraphrase_correct(answer),
    })

    # ── partial ──
    variants.append({
        "type": "partial",
        "text": _make_partial(answer),
    })

    # ── wrong ──
    variants.append({
        "type": "wrong",
        "text": _make_wrong(answer),
    })

    return variants


def _paraphrase_correct(answer: str) -> str:
    """Keep meaning but restructure into natural paraphrase. Distinct from ground truth."""
    clean = answer.lstrip("- *•0123456789. ")
    # Find a natural break point (。or ，) in the middle of the text
    mid = len(clean) // 2
    break_at = clean.find("，", mid - 20)
    if break_at == -1:
        break_at = clean.find("。", mid - 20)
    if break_at > 0:
        # Front-load: put the second half first, then connect back
        second = clean[break_at + 1:].lstrip("，。 ")
        first = clean[:break_at].rstrip("，。 ")
        return f"简单来说，{second}，这主要是因为{first}"
    # Fallback: structural reorder
    return f"我的理解是：{clean}"


def _make_partial(answer: str) -> str:
    """Keep core concept but omit an important qualification. Cuts at sentence boundary."""
    # Strategy: find a clause after a delimiter and drop it
    for delim in ["，但", "，同时", "。同时", "。此外", "，然而", "，并且",
                  "，因此", "，所以", "。另外", "，尽管"]:
        idx = answer.find(delim)
        if idx > 40:
            return _clean_end(answer[:idx]) + "。"
    # Fallback: truncate at last full sentence boundary before 2/3 of text
    two_thirds = len(answer) * 2 // 3
    # Find last 。before two_thirds
    last_period = answer.rfind("。", 0, two_thirds)
    if last_period > 40:
        return answer[:last_period + 1]
    # Absolute fallback
    return answer[:len(answer) * 2 // 3].rsplit("。", 1)[0] + "。"


def _clean_end(s: str) -> str:
    """Remove trailing punctuation fragments from a string."""
    return s.rstrip("，。、；： ") + "。" if not s.endswith("。") else s


def _make_wrong(answer: str) -> str:
    """Flip a core relationship to create a wrong but plausible answer."""
    flip_pairs = [
        ("避免", "检测"), ("检测", "避免"),
        ("同步", "异步"), ("异步", "同步"),
        ("阻塞", "非阻塞"), ("非阻塞", "阻塞"),
        ("静态", "动态"), ("动态", "静态"),
        ("递增", "递减"), ("递减", "递增"),
        ("增加", "减少"), ("减少", "增加"),
        ("O(1)", "O(n)"), ("O(n)", "O(1)"),
        ("O(log n)", "O(n)"), ("O(n²)", "O(n)"),
        ("内核态", "用户态"), ("用户态", "内核态"),
        ("主键", "外键"), ("B+树", "B树"),
        ("只读", "读写"), ("共享锁", "排他锁"),
        ("串行化", "读提交"), ("乐观锁", "悲观锁"),
        ("最终一致性", "强一致性"), ("强一致性", "最终一致性"),
        ("水平切分", "垂直切分"), ("关系型", "非关系型"),
        ("TCP", "UDP"), ("面向连接", "无连接"),
        ("先序", "后序"), ("深度优先", "广度优先"),
        ("最大堆", "最小堆"), ("头插", "尾插"),
    ]
    result = answer
    for old, new in flip_pairs:
        if old in result:
            return result.replace(old, new, 1)
    # Fallback: replace the last sentence with a contradictory claim
    sentences = result.rstrip("。").split("。")
    if len(sentences) >= 2:
        # Keep the first half, replace the second half
        keep = sentences[:len(sentences) // 2]
        # Make up a wrong conclusion that references the topic
        wrong_end = "因此它的主要优点是简单易实现，不需要考虑并发控制"
        return "。".join(keep) + "。" + wrong_end + "。"
    # Last resort: negate a keyword anywhere
    if "必须" in result:
        return result.replace("必须", "不一定需要", 1)
    if "需要" in result:
        return result.replace("需要", "不需要", 1)
    return result[:len(result) // 2] + "……实际上这个说法是错误的。"


# ── Sampling ──

def stratified_sample(points: list[dict], n: int) -> list[dict]:
    """Sample n points with course diversity."""
    by_course = defaultdict(list)
    for p in points:
        by_course[p["course"]].append(p)

    # Sort courses by count, take proportionally
    courses = sorted(by_course.keys(), key=lambda c: len(by_course[c]), reverse=True)
    per_course = max(1, n // len(courses))
    selected = []
    for course in courses:
        pool = by_course[course][:50]  # cap pool size per course
        k = min(per_course, len(pool))
        selected.extend(random.sample(pool, k))
    # Fill remaining from largest pools
    if len(selected) < n:
        extra = [p for p in points if p not in selected]
        selected.extend(random.sample(extra, min(n - len(selected), len(extra))))
    return selected[:n]


# ── Labeling ──

async def label_sample(evaluator, pt: dict, variant: dict) -> dict:
    """Label one (knowledge_point, student_answer) pair."""
    q = PracticeQuestion(
        questionId=str(uuid.uuid4()),
        questionType="SHORT_ANSWER",
        stem=pt["stem"],
        answer=pt["answer"],
        knowledgeTags=[pt["course"], pt["chapter"]],
        difficultyLevel="INTERMEDIATE",
        explanation=f"来自 {pt['course']} - {pt['chapter']}，属于{pt['heading']}。",
    )
    eval_result: SubjectiveJudgeEvaluation = await evaluator.evaluate(
        question=q,
        learner_answer=variant["text"],
    )
    return {
        "stem": pt["stem"],
        "answer": pt["answer"],
        "course": pt["course"],
        "chapter": pt["chapter"],
        "heading": pt["heading"],
        "learner_answer": variant["text"],
        "variant_type": variant["type"],
        "label": {
            "score": eval_result.score,
            "isCorrect": eval_result.is_correct,
            "reason": eval_result.reason,
            "feedback": eval_result.feedback,
            "confidenceLevel": eval_result.confidence_level,
        },
    }


# ── Inspection ──

def inspect_samples(dataset: list[dict], n: int = 5):
    """Pretty-print samples for human review."""
    for i, d in enumerate(dataset[:n]):
        print(f"\n{'─' * 60}")
        print(f"Sample {i+1}  [{d['variant_type']}]")
        print(f"  Course: {d['course']}  |  Chapter: {d['chapter']}")
        print(f"  STEM:\n    {d['stem'][:120]}...")
        print(f"  ANSWER (ground truth):\n    {d['answer'][:200]}...")
        print(f"  LEARNER:\n    {d['learner_answer'][:200]}...")
        label = d["label"]
        print(f"  LABEL: score={label['score']:.1f}  "
              f"isCorrect={label['isCorrect']}  "
              f"confidence={label['confidenceLevel']}")
        print(f"  REASON: {label['reason'][:120]}")
        print(f"  FEEDBACK: {label['feedback'][:120]}")


# ── Main ──

async def main():
    n = SAMPLE_N
    inspect_only = "--inspect" in sys.argv
    for i, arg in enumerate(sys.argv):
        if arg == "--N" and i + 1 < len(sys.argv):
            n = int(sys.argv[i + 1])

    print(f"{'═' * 60}")
    print(f"Judge Training Data Generator")
    print(f"Target: {n} samples | Model: Qwen3-0.6B SFT + GRPO")
    print(f"{'═' * 60}")

    # 1. Extract knowledge points
    print("\n[1/4] Extracting knowledge points from wiki...")
    points = extract_knowledge_points()
    print(f"  Total candidates: {len(points)}")

    # 2. Sample
    sampled = stratified_sample(points, n)
    print(f"  Sampled: {len(sampled)}")

    # 3. Generate variants
    print("\n[2/4] Generating answer variants...")
    all_samples = []
    for pt in sampled:
        variants = make_answer_variants(pt["answer"])
        for v in variants:
            all_samples.append((pt, v))

    print(f"  {len(sampled)} points × 3 variants = {len(all_samples)} total")

    if inspect_only:
        # Just show 5 raw samples without labeling
        inspected = []
        for pt in sampled[:5]:
            variants = make_answer_variants(pt["answer"])
            for v in variants:
                inspected.append({
                    "stem": pt["stem"],
                    "answer": pt["answer"],
                    "course": pt["course"],
                    "chapter": pt["chapter"],
                    "heading": pt["heading"],
                    "learner_answer": v["text"],
                    "variant_type": v["type"],
                    "label": {"score": 0, "isCorrect": False, "reason": "TBD",
                              "feedback": "TBD", "confidenceLevel": "LOW"},
                })
        inspect_samples(inspected, 15)
        print("\n[INSPECT MODE] Check variant quality above. Rerun without --inspect to label.")
        return

    # 4. Label with DeepSeek evaluator (separate from runtime config)
    print("\n[3/4] Labeling with DeepSeek evaluator...")
    from src.ai_modules.llms.openai_compatible import OpenAICompatibleClient
    evaluator = OpenAICompatibleSubjectiveJudgeEvaluator()
    # Override client with DeepSeek API — does NOT touch runtime settings
    evaluator.client = OpenAICompatibleClient(
        api_key="sk-b51b4ee0cfe841dc98910a3b9c8bd6f6",
        base_url="https://api.deepseek.com/v1",
        model_name="deepseek-chat",
    )
    dataset = []
    for i, (pt, variant) in enumerate(all_samples):
        try:
            sample = await label_sample(evaluator, pt, variant)
            dataset.append(sample)
        except Exception as e:
            print(f"  [{i+1}/{len(all_samples)}] ERROR: {e}")
            continue
        if (i + 1) % 15 == 0:
            print(f"  [{i+1}/{len(all_samples)}] done")
            # Pause to avoid rate limit
            await asyncio.sleep(0.5)

    print(f"  Labeled: {len(dataset)} / {len(all_samples)}")

    # 5. Save
    print(f"\n[4/4] Saving to {OUTPUT}...")
    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(dataset, f, ensure_ascii=False, indent=2)

    print(f"\nDone. {len(dataset)} samples saved.")
    print(f"\nNext steps:")
    print(f"  1. Inspect: python scripts/generate_judge_train_data.py --inspect")
    print(f"  2. Increase: python scripts/generate_judge_train_data.py --N 500")
    print(f"  3. Train SFT → GRPO → GGUF")


if __name__ == "__main__":
    asyncio.run(main())
