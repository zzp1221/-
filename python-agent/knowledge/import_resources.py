"""
Import learning resources (videos, reference docs, cheat sheets) into:
  - MinIO (small metadata JSON files)
  - storage.resource_object (object metadata)
  - app.learning_resource (main resource table)
  - rag.resource_document + rag.resource_chunk (vectorized descriptions)

Usage: python import_resources.py [--dry-run]
"""
import sys
import os
import uuid
import json
import time
import hashlib
from datetime import datetime, timezone
from io import BytesIO

import psycopg2
from minio import Minio
from dashscope import MultiModalEmbedding
from settings_helper import configure_dashscope_api_key

RUNTIME_CONFIG = configure_dashscope_api_key()


# 鈹€鈹€ Config 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€
DB_CONFIG = RUNTIME_CONFIG.postgres.model_dump()

MINIO_CONFIG = RUNTIME_CONFIG.minio.model_dump(exclude={"bucket"})
MINIO_BUCKET = RUNTIME_CONFIG.minio.bucket

DIMENSION = RUNTIME_CONFIG.embedding_dimension
BATCH_SIZE = 5
API_DELAY = 0.3


# 鈹€鈹€ Resource Definitions 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€
def build_resources() -> list[dict]:
    """Define the learning resources to import."""
    resources = []

    # === Video Resources (9 existing + 6 new) ===
    videos = [
        # Existing 9
        {
            "title": "鎿嶄綔绯荤粺-杩涚▼鍚屾涓嶱V鎿嶄綔锛堣棰戯級",
            "resource_type": "VIDEO",
            "difficulty": "INTERMEDIATE",
            "tags": ["鎿嶄綔绯荤粺", "杩涚▼鍚屾", "PV鎿嶄綔", "淇″彿閲?, "瑙嗛"],
            "summary": "娣卞叆璁茶В鎿嶄綔绯荤粺涓殑杩涚▼鍚屾鏈哄埗锛岄噸鐐瑰墫鏋怭V鎿嶄綔鍜屼俊鍙烽噺鐨勫師鐞嗐€佷娇鐢ㄥ満鏅互鍙婄粡鍏稿悓姝ラ棶棰橈紙鐢熶骇鑰?娑堣垂鑰呫€佽鑰?鍐欒€呫€佸摬瀛﹀灏遍锛夈€傞€氳繃瀹為檯浠ｇ爜婕旂ず甯姪鐞嗚В鎶借薄鐨勫悓姝ユ蹇点€?,
            "url": "https://www.bilibili.com/video/BV1YE411D7nH",
            "platform": "bilibili",
            "author": "鐜嬮亾璁＄畻鏈烘暀鑲?,
            "duration": "52:00",
        },
        {
            "title": "鏁版嵁搴?鍒嗗竷寮忎簨鍔″師鐞嗭紙瑙嗛锛?,
            "resource_type": "VIDEO",
            "difficulty": "ADVANCED",
            "tags": ["鏁版嵁搴?, "鍒嗗竷寮忎簨鍔?, "2PC", "3PC", "CAP", "瑙嗛"],
            "summary": "鍏ㄩ潰浠嬬粛鍒嗗竷寮忎簨鍔＄殑鏍稿績鍘熺悊锛屽寘鎷袱闃舵鎻愪氦锛?PC锛夈€佷笁闃舵鎻愪氦锛?PC锛夈€丆AP瀹氱悊涓嶣ASE鐞嗚鐨勫叧绯伙紝浠ュ強NewSQL鏁版嵁搴撳浣曡В鍐冲垎甯冨紡浜嬪姟闂銆?,
            "url": "https://www.bilibili.com/video/BV1Vt4y1S7jW",
            "platform": "bilibili",
            "author": "灏氱璋?,
            "duration": "45:30",
        },
        {
            "title": "鏁版嵁缁撴瀯-绾㈤粦鏍戝師鐞嗕笌瀹炵幇锛堣棰戯級",
            "resource_type": "VIDEO",
            "difficulty": "ADVANCED",
            "tags": ["鏁版嵁缁撴瀯", "绾㈤粦鏍?, "骞宠　浜屽弶鏍?, "浜屽弶鏌ユ壘鏍?, "瑙嗛"],
            "summary": "浠?-3-4鏍戝嚭鍙戞帹瀵肩孩榛戞爲鐨?鏉℃€ц川锛岃缁嗚瑙ｆ彃鍏ョ殑3绉嶄慨澶嶅満鏅紙鍙斿彅绾?榛戙€丩L/RR/LR/RL鏃嬭浆锛夊拰鍒犻櫎淇銆傚姣擜VL鏍戝垎鏋愮孩榛戞爲閫傚悎棰戠箒鎻掑叆鍒犻櫎鍦烘櫙鐨勫師鍥犮€?,
            "url": "https://www.bilibili.com/video/BV1uZ4y1P7ji",
            "platform": "bilibili",
            "author": "浠ｇ爜闅忔兂褰?,
            "duration": "55:00",
        },
        {
            "title": "绋嬪簭璁捐-Rust鎵€鏈夋潈涓庡€熺敤绯荤粺锛堣棰戯級",
            "resource_type": "VIDEO",
            "difficulty": "ADVANCED",
            "tags": ["Rust", "鎵€鏈夋潈", "鍊熺敤", "鐢熷懡鍛ㄦ湡", "鏅鸿兘鎸囬拡", "瑙嗛"],
            "summary": "Rust鏈€鏍稿績鐨勬墍鏈夋潈銆佸€熺敤銆佺敓鍛藉懆鏈熸蹇碉紝鐢ㄥ浘瑙ｅ拰瀵规瘮鐨勬柟寮忚娓呮銆傚姣擟/C++鎵嬪姩鍐呭瓨绠＄悊鍜孞ava/Go鐨凣C锛岀悊瑙ust闆舵垚鏈娊璞＄殑RAII+缂栬瘧鏈熷€熺敤妫€鏌ョ殑璁捐鍔ㄦ満銆?,
            "url": "https://www.bilibili.com/video/BV1hp4y1k7SV",
            "platform": "bilibili",
            "author": "Rust涓枃绀惧尯",
            "duration": "50:30",
        },
        {
            "title": "绠楁硶-鍔ㄦ€佽鍒掍粠鍏ラ棬鍒扮簿閫氾紙瑙嗛锛?,
            "resource_type": "VIDEO",
            "difficulty": "ADVANCED",
            "tags": ["绠楁硶", "鍔ㄦ€佽鍒?, "DP", "鏈€浼樺瓙缁撴瀯", "閲嶅彔瀛愰棶棰?, "瑙嗛"],
            "summary": "浠庢枑娉㈤偅濂戞暟鍒楃殑閫掑綊浼樺寲寮€濮嬶紝閫愭璁茶ВDP鍥涘ぇ姝ラ锛氱‘瀹氱姸鎬佸畾涔夈€佸啓鍑虹姸鎬佽浆绉绘柟绋嬨€佸垵濮嬪寲杈圭晫鏉′欢銆佺‘瀹氶亶鍘嗛『搴忋€傝鐩?1鑳屽寘銆丩CS銆丩IS銆佺紪杈戣窛绂荤瓑缁忓吀渚嬮銆?,
            "url": "https://www.bilibili.com/video/BV1X741127ZM",
            "platform": "bilibili",
            "author": "MIT OpenCourseWare",
            "duration": "60:00",
        },
        {
            "title": "缂栬瘧鍘熺悊-LL(1)涓嶭R(1)璇硶鍒嗘瀽锛堣棰戯級",
            "resource_type": "VIDEO",
            "difficulty": "ADVANCED",
            "tags": ["缂栬瘧鍘熺悊", "璇硶鍒嗘瀽", "LL(1)", "LR(1)", "First闆?, "Follow闆?, "瑙嗛"],
            "summary": "缂栬瘧鍘熺悊鏍稿績锛氳嚜涓婅€屼笅LL(1)鍜岃嚜涓嬭€屼笂LR(1)璇硶鍒嗘瀽鏂规硶銆傛兜鐩栨秷闄ゅ乏閫掑綊銆佹彁鍙栧乏鍏洜瀛愩€丗irst/Follow闆嗘瀯閫犮€丩R(1)椤圭洰闆嗘棌銆丩ALR(1)鍘嬬缉绛夊叧閿妧鏈€?,
            "url": "https://www.bilibili.com/video/BV1KW411j7GV",
            "platform": "bilibili",
            "author": "鍝堝伐澶ф垬寰疯嚕",
            "duration": "65:00",
        },
        {
            "title": "璁＄畻鏈虹粍鎴愬師鐞?CPU娴佹按绾胯璁★紙瑙嗛锛?,
            "resource_type": "VIDEO",
            "difficulty": "ADVANCED",
            "tags": ["璁＄畻鏈虹粍鎴愬師鐞?, "CPU", "娴佹按绾?, "鎸囦护闆?, "鍐掗櫓", "瑙嗛"],
            "summary": "璁茶ВCPU娴佹按绾跨殑5绾ц璁★紙IF/ID/EX/MEM/WB锛夛紝娣卞叆鍒嗘瀽缁撴瀯鍐掗櫓銆佹暟鎹啋闄┿€佹帶鍒跺啋闄╀笁绉嶆祦姘寸嚎鍐茬獊鍙婂叾瑙ｅ喅鏂规锛氬墠鎺ㄣ€佹梺璺€佸垎鏀娴嬨€佹祦姘寸嚎鏆傚仠銆?,
            "url": "https://www.bilibili.com/video/BV1t4411e7LH",
            "platform": "bilibili",
            "author": "鐜嬮亾璁＄畻鏈烘暀鑲?,
            "duration": "48:20",
        },
        {
            "title": "璁＄畻鏈虹綉缁?TCP鎷ュ鎺у埗璇﹁В锛堣棰戯級",
            "resource_type": "VIDEO",
            "difficulty": "INTERMEDIATE",
            "tags": ["璁＄畻鏈虹綉缁?, "TCP", "鎷ュ鎺у埗", "鎱㈠惎鍔?, "鎷ュ閬垮厤", "蹇噸浼?, "瑙嗛"],
            "summary": "TCP鎷ュ鎺у埗鐨勫畬鏁存紨鍖栵細Tahoe鈫扲eno鈫扤ewReno鈫扖UBIC鈫払BR銆傜敤鐘舵€佹満鍥剧ず鎱㈠惎鍔ㄣ€佹嫢濉為伩鍏嶃€佸揩閲嶄紶銆佸揩鎭㈠鍥涗釜闃舵鐨勫姩鎬佸垏鎹紝瀵规瘮鍚勭増鏈涓㈠寘鍜屽欢杩熺殑鍝嶅簲绛栫暐銆?,
            "url": "https://www.bilibili.com/video/BV1Hx411m7RH",
            "platform": "bilibili",
            "author": "婀栫澶ф暀涔﹀尃",
            "duration": "38:15",
        },
        {
            "title": "杞欢宸ョ▼-璁捐妯″紡绮捐锛堣棰戯級",
            "resource_type": "VIDEO",
            "difficulty": "INTERMEDIATE",
            "tags": ["璁捐妯″紡", "GoF", "鍗曚緥", "宸ュ巶", "瑙傚療鑰?, "绛栫暐", "瑙嗛"],
            "summary": "灏氱璋疯璁℃ā寮忓叏瑙ｏ紝瑕嗙洊GoF 23绉嶈璁℃ā寮忓畬鏁磋瑙ｃ€傛瘡绉嶆ā寮忓寘鍚姩鏈恒€佺被鍥剧粨鏋勩€佷唬鐮佸疄鐜般€佷紭缂虹偣鍒嗘瀽銆傛寜甯哥敤浼樺厛锛氬崟渚嬧啋宸ュ巶鈫掔瓥鐣モ啋瑙傚療鑰呪啋瑁呴グ鍣ㄢ啋浠ｇ悊鈫掆€?,
            "url": "https://www.bilibili.com/video/BV1G4411c7N4",
            "platform": "bilibili",
            "author": "灏氱璋?,
            "duration": "70:00",
        },
        # New videos
        {
            "title": "鏁版嵁缁撴瀯-鍥捐绠楁硶娣卞害瑙ｆ瀽锛堣棰戯級",
            "resource_type": "VIDEO",
            "difficulty": "ADVANCED",
            "tags": ["鏁版嵁缁撴瀯", "鍥捐", "DFS", "BFS", "Dijkstra", "Prim", "瑙嗛"],
            "summary": "鍏ㄩ潰瑕嗙洊鍥剧殑瀛樺偍缁撴瀯锛堥偦鎺ョ煩闃?閭绘帴琛級銆侀亶鍘嗭紙DFS/BFS锛夈€佹渶灏忕敓鎴愭爲锛圥rim/Kruskal锛夈€佹渶鐭矾寰勶紙Dijkstra/Floyd/Bellman-Ford锛夈€佹嫇鎵戞帓搴忓拰寮鸿繛閫氬垎閲忋€傞厤鍚堝彲瑙嗗寲鍔ㄧ敾璁茶В銆?,
            "url": "https://www.bilibili.com/video/BV1jE411W7wH",
            "platform": "bilibili",
            "author": "浠ｇ爜闅忔兂褰?,
            "duration": "65:00",
        },
        {
            "title": "璁＄畻鏈虹綉缁?HTTP鍗忚瀹屽叏瑙ｈ锛堣棰戯級",
            "resource_type": "VIDEO",
            "difficulty": "BASIC",
            "tags": ["璁＄畻鏈虹綉缁?, "HTTP", "HTTPS", "TLS", "搴旂敤灞?, "瑙嗛"],
            "summary": "HTTP/1.0鈫?.1鈫?鈫?瀹屾暣婕斿寲鍙诧紝娑电洊鎸佷箙杩炴帴銆佺绾垮寲銆佸璺鐢ㄣ€佹湇鍔″櫒鎺ㄩ€併€丵UIC鍗忚銆傝瑙TTPS鐨凾LS鎻℃墜杩囩▼銆佽瘉涔﹂摼楠岃瘉鏈哄埗锛屼互鍙婂父瑙丠TTP瀹夊叏澶撮厤缃€?,
            "url": "https://www.bilibili.com/video/BV1TY4y1H7dF",
            "platform": "bilibili",
            "author": "IT鑰佸崲",
            "duration": "55:00",
        },
        {
            "title": "鏁版嵁搴?Redis鏍稿績鏁版嵁缁撴瀯涓庡疄鎴橈紙瑙嗛锛?,
            "resource_type": "VIDEO",
            "difficulty": "INTERMEDIATE",
            "tags": ["Redis", "缂撳瓨", "鏁版嵁缁撴瀯", "璺宠〃", "甯冮殕杩囨护鍣?, "瑙嗛"],
            "summary": "娣卞叆Redis浜旂鏍稿績鏁版嵁缁撴瀯锛圫tring/List/Hash/Set/ZSet锛夌殑搴曞眰瀹炵幇锛歋DS銆亃iplist銆乹uicklist銆乨ict銆佽烦琛ㄣ€傝瑙ｇ紦瀛樼┛閫?鍑荤┛/闆穿鐨勮В鍐虫柟妗堝拰甯冮殕杩囨护鍣ㄧ殑搴旂敤銆?,
            "url": "https://www.bilibili.com/video/BV1if4y1d7GC",
            "platform": "bilibili",
            "author": "榛戦┈绋嬪簭鍛?,
            "duration": "60:00",
        },
        {
            "title": "绠楁硶-瀛楃涓插尮閰嶇畻娉曞叏闆嗭紙瑙嗛锛?,
            "resource_type": "VIDEO",
            "difficulty": "INTERMEDIATE",
            "tags": ["绠楁硶", "瀛楃涓插尮閰?, "KMP", "Boyer-Moore", "Rabin-Karp", "瑙嗛"],
            "summary": "浠庢毚鍔涘尮閰嶅嚭鍙戯紝閫愪竴鎺ㄥKMP鐨刵ext鏁扮粍鏋勯€犲師鐞嗐€丅oyer-Moore鐨勫潖瀛楃+濂藉悗缂€瑙勫垯銆丷abin-Karp鐨勬粴鍔ㄥ搱甯岃璁★紝浠ュ強Sunday绠楁硶鐨勪紭鍖栨€濊矾銆傞厤鏈夊鏉傚害瀵规瘮鍒嗘瀽銆?,
            "url": "https://www.bilibili.com/video/BV1YJ41197hM",
            "platform": "bilibili",
            "author": "姝ｆ湀鐐圭伅绗?,
            "duration": "42:00",
        },
        {
            "title": "鎿嶄綔绯荤粺-鍐呭瓨绠＄悊瀹屽叏鎸囧崡锛堣棰戯級",
            "resource_type": "VIDEO",
            "difficulty": "INTERMEDIATE",
            "tags": ["鎿嶄綔绯荤粺", "鍐呭瓨绠＄悊", "铏氭嫙鍐呭瓨", "椤佃〃", "TLB", "瑙嗛"],
            "summary": "浠庣墿鐞嗗唴瀛樺垎娈靛埌铏氭嫙鍐呭瓨鍒嗛〉鐨勬紨鍙橈紝娣卞叆瑙ｆ瀽澶氱骇椤佃〃銆乀LB鍔犻€熴€佺己椤典腑鏂鐞嗘祦绋嬨€傚姣擣IFO/LRU/Clock/Optimal椤甸潰缃崲绠楁硶鍦˙elady寮傚父鍜屽疄闄呮€ц兘涓婄殑宸紓銆?,
            "url": "https://www.bilibili.com/video/BV1ZK4y1b7mC",
            "platform": "bilibili",
            "author": "鐜嬮亾璁＄畻鏈烘暀鑲?,
            "duration": "50:00",
        },
    ]

    for v in videos:
        resources.append({
            **v,
            "domain": "COMPUTER_SCIENCE",
            "access_scope": "GLOBAL",
            "source_kind": "IMPORTED",
        })

    # === Document Resources (quick reference / cheat sheets) ===
    docs = [
        {
            "title": "鏁版嵁缁撴瀯閫熸煡鎵嬪唽锛堝浘鏂囩増锛?,
            "resource_type": "READING",
            "difficulty": "BASIC",
            "tags": ["鏁版嵁缁撴瀯", "閫熸煡", "鏁扮粍", "閾捐〃", "鏍?, "闃熷垪", "鏍?, "鍥?, "鍝堝笇"],
            "summary": "娑电洊鏁扮粍銆侀摼琛ㄣ€佹爤銆侀槦鍒椼€佹爲锛堜簩鍙夋爲/BST/AVL/绾㈤粦鏍?B鏍?B+鏍戯級銆佸浘銆佸搱甯岃〃绛夋牳蹇冩暟鎹粨鏋勭殑鎿嶄綔澶嶆潅搴﹂€熸煡琛紙鎻掑叆/鍒犻櫎/鏌ユ壘锛夊拰閫傜敤鍦烘櫙瀵圭収銆傞€傚悎鑰冨墠澶嶄範鍜岄潰璇曞噯澶囥€?,
        },
        {
            "title": "绠楁硶澶嶆潅搴﹂€熸煡琛?,
            "resource_type": "READING",
            "difficulty": "MIXED",
            "tags": ["绠楁硶", "澶嶆潅搴?, "鎺掑簭", "鎼滅储", "鍥捐", "鍔ㄦ€佽鍒?],
            "summary": "鏀跺綍鎺掑簭锛堝啋娉?閫夋嫨/鎻掑叆/甯屽皵/褰掑苟/蹇€?鍫?璁℃暟/鍩烘暟/妗讹級銆佹悳绱紙浜屽垎/绾挎€э級銆佸浘璁猴紙DFS/BFS/Dijkstra/Prim/Kruskal/Floyd锛夈€佸瓧绗︿覆鍖归厤绛夌畻娉曠殑鏃剁┖澶嶆潅搴﹀鐓ц〃銆傞檮甯︿富瀹氱悊閫熸煡銆?,
        },
        {
            "title": "SQL璇硶澶у叏锛堝惈闈㈣瘯楂橀棰橈級",
            "resource_type": "READING",
            "difficulty": "BASIC",
            "tags": ["SQL", "鏁版嵁搴?, "鏌ヨ", "JOIN", "闈㈣瘯"],
            "summary": "娑电洊DQL/DML/DDL/DCL鍏ㄩ潰璇硶锛岄噸鐐圭獊鐮碕OIN锛圛NNER/LEFT/RIGHT/FULL/CROSS锛夈€佸瓙鏌ヨ銆佽仛鍚堝嚱鏁般€佺獥鍙ｅ嚱鏁帮紙ROW_NUMBER/RANK/DENSE_RANK/LAG/LEAD锛夈€佷簨鍔℃帶鍒躲€傚弬鑰冭嚜LeetCode SQL棰樺簱銆?,
        },
        {
            "title": "璁＄畻鏈虹綉缁滃崗璁€熸煡鍥捐氨",
            "resource_type": "MINDMAP",
            "difficulty": "INTERMEDIATE",
            "tags": ["璁＄畻鏈虹綉缁?, "鍗忚", "TCP/IP", "OSI", "HTTP", "DNS"],
            "summary": "鐢ㄦ€濈淮瀵煎浘褰㈠紡灞曠ずOSI涓冨眰涓嶵CP/IP鍥涘眰鍗忚鏍堝搴斿叧绯伙紝鏍囨敞姣忓眰鏍稿績鍗忚锛圚TTP/DNS/TCP/UDP/IP/ARP/MAC锛夌殑鍏抽敭瀛楁鏍煎紡鍜孯FC缂栧彿锛屾柟渚垮揩閫熸绱㈠崗璁粏鑺傘€?,
        },
        {
            "title": "鎿嶄綔绯荤粺鏍稿績姒傚康涓€椤甸€?,
            "resource_type": "READING",
            "difficulty": "INTERMEDIATE",
            "tags": ["鎿嶄綔绯荤粺", "杩涚▼", "绾跨▼", "鍐呭瓨", "鏂囦欢绯荤粺", "IO"],
            "summary": "涓€椤电焊鎬荤粨鎿嶄綔绯荤粺鏍稿績姒傚康锛氳繘绋嬬姸鎬佽浆鎹㈠浘銆佺嚎绋嬫ā鍨嬪姣斻€佹閿佸洓鏉′欢涓庨闃茬瓥鐣ャ€侀〉闈㈢疆鎹㈢畻娉曞姣旇〃銆佺鐩樿皟搴︾畻娉曚竴瑙堛€傞€傚悎鎵撳嵃璐村湪澧欎笂闅忔椂鏌ラ槄銆?,
        },
        {
            "title": "璁捐妯″紡閫熸煡鍗＄墖锛?3绉嶅叏锛?,
            "resource_type": "READING",
            "difficulty": "INTERMEDIATE",
            "tags": ["璁捐妯″紡", "GoF", "鍒涘缓鍨?, "缁撴瀯鍨?, "琛屼负鍨?, "UML"],
            "summary": "23绉岹oF璁捐妯″紡鐨勯€熸煡鍗＄墖褰㈠紡鎬荤粨锛屾瘡绉嶆ā寮忓惈锛氫竴鍙ヨ瘽鎰忓浘銆乁ML绫诲浘绠€鍥俱€侀€傜敤鍦烘櫙銆佷笌鐩稿叧妯″紡鐨勫尯鍒€傛寜鍒涘缓鍨?缁撴瀯鍨?琛屼负鍨嬩笁澶х被鍒嗙粍锛屾柟渚块潰璇曞墠蹇€熷洖椤俱€?,
        },
        {
            "title": "Git鐗堟湰鎺у埗瀹炴垬鎵嬪唽",
            "resource_type": "READING",
            "difficulty": "BASIC",
            "tags": ["Git", "鐗堟湰鎺у埗", "鍒嗘敮", "鍚堝苟", "GitHub"],
            "summary": "浠巊it init鍒板崗鍚屽紑鍙戠殑瀹屾暣娴佺▼锛氬伐浣滃尯/鏆傚瓨鍖?鏈湴浠撳簱/杩滅▼浠撳簱鍥涘眰妯″瀷銆佸垎鏀瓥鐣ワ紙GitFlow/TrunkBased锛夈€佸悎骞朵笌鍙樺熀(git rebase)銆佸啿绐佽В鍐炽€乧herry-pick銆乬it bisect璋冭瘯銆?,
        },
        {
            "title": "Linux鍛戒护澶у叏锛堝紑鍙戝繀澶囷級",
            "resource_type": "READING",
            "difficulty": "BASIC",
            "tags": ["Linux", "鍛戒护琛?, "Shell", "绯荤粺绠＄悊"],
            "summary": "闈㈠悜绋嬪簭鍛樼殑Linux鍛戒护閫熸煡锛氭枃浠舵搷浣滐紙find/grep/awk/sed锛夈€佽繘绋嬬鐞嗭紙ps/top/kill/nohup锛夈€佹潈闄愮鐞嗭紙chmod/chown/sudo锛夈€佺綉缁滆瘖鏂紙netstat/ss/tcpdump/curl锛夈€佺郴缁熺洃鎺э紙df/du/free/iostat锛夈€?,
        },
        {
            "title": "缂栬瘧鍘熺悊鏍稿績娴佺▼鍥捐В",
            "resource_type": "MINDMAP",
            "difficulty": "ADVANCED",
            "tags": ["缂栬瘧鍘熺悊", "璇嶆硶鍒嗘瀽", "璇硶鍒嗘瀽", "璇箟鍒嗘瀽", "浠ｇ爜浼樺寲"],
            "summary": "浠ュ彲瑙嗗寲娴佺▼鍥惧睍绀虹紪璇戝櫒鍓嶇锛堣瘝娉曗啋璇硶鈫掕涔夆啋涓棿浠ｇ爜锛夈€佸悗绔紙浼樺寲鈫掔洰鏍囦唬鐮侊級鐨勫畬鏁村伐浣滄祦銆傛爣娉∟FA/DFA銆丩L(1)/LR(1)銆佺鍙疯〃銆佷腑闂翠唬鐮佷笁鍦板潃鐮佺瓑鍚勯樁娈垫牳蹇冩妧鏈€?,
        },
        {
            "title": "绂绘暎鏁板-鍥捐瀹氱悊閫熸煡",
            "resource_type": "READING",
            "difficulty": "INTERMEDIATE",
            "tags": ["绂绘暎鏁板", "鍥捐", "鏍?, "娆ф媺鍥?, "鍝堝瘑椤垮浘", "骞抽潰鍥?],
            "summary": "鏁寸悊绂绘暎鏁板鍥捐閮ㄥ垎閲嶈瀹氱悊锛氭彙鎵嬪畾鐞嗐€佹爲鐨勬€ц川锛坣-1杈?杩為€氭棤鍥炶矾锛夈€佹鎷夊浘鍏呰鏉′欢銆佸搱瀵嗛】鍥惧厖鍒嗘潯浠讹紙Dirac/Ore瀹氱悊锛夈€佸钩闈㈠浘娆ф媺鍏紡锛圴-E+F=2锛夈€佸洓鑹插畾鐞嗐€?,
        },
        {
            "title": "Python鏁版嵁绉戝鍏ラ棬鎸囧崡",
            "resource_type": "READING",
            "difficulty": "BASIC",
            "tags": ["Python", "鏁版嵁绉戝", "NumPy", "Pandas", "Matplotlib"],
            "summary": "闈㈠悜璁＄畻鏈轰笓涓氬鐢熺殑Python鏁版嵁绉戝鍏ラ棬锛歂umPy鏁扮粍杩愮畻涓庡箍鎾満鍒躲€丳andas鏁版嵁娓呮礂涓嶨roupBy鎿嶄綔銆丮atplotlib/Seaborn鍙鍖栧浘琛ㄩ€夋嫨鎸囧崡銆傛瘡涓富棰橀厤澶囧疄闄呬唬鐮佺墖娈点€?,
        },
    ]

    for d in docs:
        resources.append({
            **d,
            "domain": "COMPUTER_SCIENCE",
            "access_scope": "GLOBAL",
            "source_kind": "IMPORTED",
        })

    return resources


# 鈹€鈹€ DB Helpers 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€
def connect_db():
    return psycopg2.connect(**DB_CONFIG)


# 鈹€鈹€ MinIO Helpers 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€
def connect_minio():
    return Minio(
        MINIO_CONFIG["endpoint"],
        access_key=MINIO_CONFIG["access_key"],
        secret_key=MINIO_CONFIG["secret_key"],
        secure=MINIO_CONFIG["secure"],
    )


def ensure_bucket(client: Minio, bucket: str):
    if not client.bucket_exists(bucket):
        client.make_bucket(bucket)
        print(f"  Created bucket: {bucket}")
    else:
        print(f"  Bucket exists: {bucket}")


def upload_resource_meta(client: Minio, bucket: str, resource: dict) -> str:
    """Upload resource metadata JSON to MinIO, return object_key."""
    safe_name = resource["title"].replace("/", "-").replace(" ", "_")
    object_key = f"resources/{safe_name}.json"
    meta_json = json.dumps({
        "title": resource["title"],
        "resource_type": resource["resource_type"],
        "domain": resource["domain"],
        "difficulty": resource.get("difficulty", "MIXED"),
        "tags": resource.get("tags", []),
        "summary": resource.get("summary", ""),
        "url": resource.get("url"),
        "platform": resource.get("platform"),
        "author": resource.get("author"),
        "duration": resource.get("duration"),
    }, ensure_ascii=False, indent=2)

    data = BytesIO(meta_json.encode("utf-8"))
    client.put_object(bucket, object_key, data, len(meta_json.encode("utf-8")), content_type="application/json")
    return object_key


# 鈹€鈹€ Embedding 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€
def generate_embeddings(texts: list[str], dimension: int = RUNTIME_CONFIG.embedding_dimension) -> list[list[float]]:
    input_data = [{"text": t} for t in texts]
    resp = MultiModalEmbedding.call(
        model=RUNTIME_CONFIG.embedding_model_name,
        input=input_data,
        dimension=dimension,
        output_type="dense",
    )
    if resp.status_code != 200:
        raise RuntimeError(f"API error: {resp.code} {resp.message}")
    emb_list = resp.output.get("embeddings", [])
    emb_list.sort(key=lambda x: x.get("index", 0))
    return [e["embedding"] for e in emb_list]


def build_embedding_str(vec: list[float]) -> str:
    return "[" + ",".join(str(v) for v in vec) + "]"


# 鈹€鈹€ Main 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€
def main():
    dry_run = "--dry-run" in sys.argv
    print("=" * 60)
    print("Learning Resources 鈫?MinIO + PostgreSQL")
    print("=" * 60)

    resources = build_resources()
    print(f"\nResources defined: {len(resources)}")
    videos = sum(1 for r in resources if r["resource_type"] == "VIDEO")
    docs = sum(1 for r in resources if r["resource_type"] != "VIDEO")
    print(f"  Videos: {videos}")
    print(f"  Documents: {docs}")

    if dry_run:
        print("\n[DRY RUN] Would create resources in MinIO + PostgreSQL")
        for r in resources:
            print(f"  [{r['resource_type']:12s}] {r['title']}")
        return

    # Connect to services
    minio = connect_minio()
    ensure_bucket(minio, MINIO_BUCKET)

    conn = connect_db()
    try:
        with conn:
            with conn.cursor() as cur:
                # Clear existing resource data
                cur.execute("DELETE FROM rag.resource_chunk")
                cur.execute("DELETE FROM rag.resource_document")
                cur.execute("DELETE FROM app.learning_resource")
                cur.execute("DELETE FROM storage.resource_object")
                print("  Cleared existing resource data")

                # Also clear knowledge_document/chunks from vectorize_wiki since these overlap
                # (resource_document is separate from knowledge_document)
                print(f"\nProcessing {len(resources)} resources...")

                # Step 1: Upload to MinIO + create storage.resource_object
                object_ids: dict[str, str] = {}  # title -> storage_object_id
                for i, r in enumerate(resources):
                    object_key = upload_resource_meta(minio, MINIO_BUCKET, r)
                    obj_id = str(uuid.uuid4())
                    cur.execute("""
                        INSERT INTO storage.resource_object (id, provider, bucket_name, object_key, file_name, mime_type, size_bytes, access_mode, storage_url)
                        VALUES (%s, 'RUSTFS', %s, %s, %s, 'application/json', %s, 'PRESIGNED', %s)
                    """, (obj_id, MINIO_BUCKET, object_key, f"{r['title']}.json",
                          len(json.dumps(r, ensure_ascii=False).encode("utf-8")),
                          f"minio://{MINIO_BUCKET}/{object_key}"))
                    object_ids[r["title"]] = obj_id
                    if (i + 1) % 10 == 0:
                        print(f"  MinIO + storage [{i + 1}/{len(resources)}]")

                print(f"  Uploaded {len(resources)} objects to MinIO")

                # Step 2: Create app.learning_resource entries
                learning_ids: dict[str, str] = {}  # title -> learning_resource_id
                for r in resources:
                    lr_id = str(uuid.uuid4())
                    cur.execute("""
                        INSERT INTO app.learning_resource (id, title, domain, resource_type, difficulty_level,
                            source_kind, access_scope, summary_text, tags, storage_object_id)
                        VALUES (%s, %s, %s, %s::app.resource_type, %s::app.difficulty_level,
                            %s::app.source_kind, %s::app.access_scope, %s, %s, %s)
                    """, (
                        lr_id, r["title"], r["domain"], r["resource_type"], r["difficulty"],
                        r["source_kind"], r["access_scope"], r.get("summary", ""),
                        json.dumps(r.get("tags", []), ensure_ascii=False),
                        object_ids.get(r["title"]),
                    ))
                    learning_ids[r["title"]] = lr_id
                print(f"  Created {len(resources)} learning_resource entries")

                # Step 3: Create rag.resource_document entries
                resource_doc_ids: dict[str, str] = {}  # title -> resource_document_id
                for r in resources:
                    rd_id = str(uuid.uuid4())
                    cur.execute("""
                        INSERT INTO rag.resource_document (id, resource_id, title, domain, resource_type,
                            difficulty_level, source_kind, summary_text, access_scope, metadata_json)
                        VALUES (%s, %s, %s, %s, %s::app.resource_type, %s::app.difficulty_level,
                            %s::app.source_kind, %s, %s::app.access_scope, %s)
                    """, (
                        rd_id, learning_ids[r["title"]], r["title"], r["domain"], r["resource_type"],
                        r["difficulty"], r["source_kind"], r.get("summary", ""), r["access_scope"],
                        json.dumps({"url": r.get("url"), "platform": r.get("platform"),
                                    "author": r.get("author"), "duration": r.get("duration"),
                                    "object_key": f"resources/{r['title'].replace('/', '-').replace(' ', '_')}.json"},
                                   ensure_ascii=False),
                    ))
                    resource_doc_ids[r["title"]] = rd_id
                print(f"  Created {len(resources)} resource_document entries")

                # Step 4: Generate embeddings and create resource_chunk entries
                summaries = [r.get("summary", "") for r in resources]
                failed = 0
                for batch_start in range(0, len(resources), BATCH_SIZE):
                    batch = resources[batch_start : batch_start + BATCH_SIZE]
                    batch_summaries = summaries[batch_start : batch_start + BATCH_SIZE]

                    try:
                        embeddings = generate_embeddings(batch_summaries, DIMENSION)
                    except Exception as e:
                        print(f"  Batch [{batch_start + 1}] API error: {e}, retrying one by one...")
                        embeddings = []
                        for s in batch_summaries:
                            try:
                                emb = generate_embeddings([s], DIMENSION)
                                embeddings.extend(emb)
                            except Exception:
                                embeddings.append(None)
                                failed += 1
                            time.sleep(API_DELAY)

                    for j, r in enumerate(batch):
                        emb_vec = embeddings[j] if j < len(embeddings) and embeddings[j] is not None else None
                        if emb_vec is None:
                            print(f"  SKIP (no embedding): {r['title']}")
                            continue

                        cur.execute("""
                            INSERT INTO rag.resource_chunk (document_id, resource_id, chunk_no, content,
                                embedding, token_count, domain, resource_type, difficulty_level,
                                access_scope, quality_score, metadata_json)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s::app.resource_type, %s::app.difficulty_level,
                                %s::app.access_scope, %s, %s)
                        """, (
                            resource_doc_ids[r["title"]],
                            learning_ids[r["title"]],
                            1,
                            r.get("summary", ""),
                            build_embedding_str(emb_vec),
                            int(len(r.get("summary", "")) / 1.5),
                            r["domain"],
                            r["resource_type"],
                            r["difficulty"],
                            r["access_scope"],
                            0.85,
                            "{}",
                        ))
                    print(f"  Vectorized [{batch_start + len(batch)}/{len(resources)}]")

                    time.sleep(API_DELAY)

        if failed > 0:
            print(f"\nWarning: {failed} embeddings failed")
        print(f"\nDone. {len(resources)} resources imported:")
        print(f"  - storage.resource_object: {len(object_ids)}")
        print(f"  - app.learning_resource: {len(learning_ids)}")
        print(f"  - rag.resource_document: {len(resource_doc_ids)}")
        print(f"  - rag.resource_chunk: ~{len(resource_doc_ids) - failed}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()

