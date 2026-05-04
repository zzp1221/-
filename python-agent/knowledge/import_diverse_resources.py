"""
Batch 3: Diverse resource types 鈥?QUIZ exam banks, PRACTICE hands-on labs,
CODE coding challenges, SLIDES lecture outlines.
Uploads to MinIO, registers in PostgreSQL, and vectorizes.
Usage: python import_diverse_resources.py [--dry-run]
"""
import sys
import os
import uuid
import json
import hashlib
import time
from io import BytesIO
from pathlib import Path

import psycopg2
from minio import Minio
from dashscope import MultiModalEmbedding
from settings_helper import configure_dashscope_api_key

RUNTIME_CONFIG = configure_dashscope_api_key()


DB_CONFIG = RUNTIME_CONFIG.postgres.model_dump()
MINIO_CONFIG = RUNTIME_CONFIG.minio.model_dump(exclude={"bucket"})
BUCKET = RUNTIME_CONFIG.minio.bucket

RESOURCES = []

# 鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺?# QUIZ 鈥?棰樺簱锛堝惈绛旀涓庤В鏋愶級
# 鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺?
RESOURCES.append({
    "title": "鎿嶄綔绯荤粺-杩涚▼鍚屾PV鎿嶄綔棰樺簱",
    "description": "鎿嶄綔绯荤粺PV鎿嶄綔涓庤繘绋嬪悓姝ョ粡鍏镐範棰?5閬擄紝娑电洊鐢熶骇鑰呮秷璐硅€呫€佽鑰呭啓鑰呫€佸摬瀛﹀灏遍銆佺悊鍙戝笀闂绛夛紝姣忛亾闄勮缁嗚В鏋愬拰鏄撻敊鐐规爣娉ㄣ€?,
    "course": "鎿嶄綔绯荤粺", "chapter": "杩涚▼鍚屾", "difficulty": "INTERMEDIATE",
    "type": "QUIZ",
    "tags": ["鎿嶄綔绯荤粺", "PV鎿嶄綔", "淇″彿閲?, "鍚屾", "棰樺簱"],
    "source_url": "https://pages.cs.wisc.edu/~remzi/OSTEP/",
    "content": """# 鎿嶄綔绯荤粺PV鎿嶄綔涓庤繘绋嬪悓姝ラ搴?
## 棰?. 鐢熶骇鑰?娑堣垂鑰呴棶棰?璁炬湁n涓紦鍐插尯锛岀敤PV鎿嶄綔瀹炵幇鐢熶骇鑰?娑堣垂鑰呭悓姝ャ€?
**瑙ｇ瓟**:
```
Semaphore mutex=1, empty=n, full=0;
Producer:                   Consumer:
while(1) {                  while(1) {
    produce_item();             P(full);
    P(empty);                   P(mutex);
    P(mutex);                   item = get_item();
    put_item();                 V(mutex);
    V(mutex);                   V(empty);
    V(full);                    consume_item();
}                           }
```
P鎿嶄綔鐨勯『搴忎负浣曚笉鑳戒氦鎹紵鑻ュ厛P(mutex)鍐峆(empty)锛屽綋缂撳啿鍖烘弧鏃剁敓浜ц€呮寔鏈塵utex闃诲锛屾秷璐硅€呮棤娉曡繘鍏ヤ复鐣屽尯鍙栧嚭鐗╁搧鈫掓閿併€?
## 棰?. 璇昏€?鍐欒€呴棶棰橈紙璇昏€呬紭鍏堬級
**瑕佹眰**: 澶氫釜璇昏€呭彲鍚屾椂璇伙紝鍐欒€呯嫭鍗犺闂紝璇昏€呬紭鍏堬紙鏂拌鑰呭埌杈惧彲鎻掗槦鍐欒€咃級

**瑙ｇ瓟**:
```
int readcount=0;
Semaphore mutex=1, rw=1;
Reader:                   Writer:
P(mutex);                 P(rw);
readcount++;              write();
if(readcount==1) P(rw);   V(rw);
V(mutex);
read();
P(mutex);
readcount--;
if(readcount==0) V(rw);
V(mutex);
```

## 棰?. 鍝插瀹跺氨椁愰棶棰?5浣嶅摬瀛﹀鍥村渾妗岋紝5鍙瀛愶紝姣忎汉闇€宸﹀彸涓ゅ彧绛峰瓙鎵嶈兘杩涢銆傝鐢ㄤ俊鍙烽噺閬垮厤姝婚攣銆?
**瑙ｇ瓟锛堣嚦澶?浜哄悓鏃舵嬁绛峰瓙娉曪級**:
```
Semaphore chopstick[5] = {1,1,1,1,1};
Semaphore limit = 4;  // 鏈€澶?浜哄悓鏃跺彇绛峰瓙

philosopher(i):
while(1) {
    think();
    P(limit);
    P(chopstick[i]);
    P(chopstick[(i+1)%5]);
    eat();
    V(chopstick[i]);
    V(chopstick[(i+1)%5]);
    V(limit);
}
```
鍏朵粬瑙ｆ硶锛氬鏁板彿鍏堝乏鍚庡彸銆佸伓鏁板彿鍏堝彸鍚庡乏锛涙垨鍚屾椂鍙栦袱鍙瀛愶紙AND淇″彿閲忥級銆?
## 棰?. 鐞嗗彂甯堥棶棰?鐞嗗彂搴楁湁n鎶婃瀛愶紙鍚悊鍙戞锛夛紝鑻ユ棤椤惧鍒欑悊鍙戝笀鐫¤銆傝鐢ㄤ俊鍙烽噺鍚屾銆?
**瑙ｇ瓟**:
```
int waiting = 0;
Semaphore customers = 0, barber = 0, mutex = 1;

Barber:                         Customer:
while(1) {                      P(mutex);
    P(customers);               if(waiting < n) {
    P(mutex);                       waiting++;
    waiting--;                      V(customers);
    V(barber);                      V(mutex);
    V(mutex);                       P(barber);
    cut_hair();                     get_haircut();
}                               } else {
                                    V(mutex);  // 妞呭瓙婊?绂诲紑
                                }
```

## 棰?. 鐙湪妗ラ棶棰?涓€搴х嫭鏈ㄦˉ涓€娆″彧鑳借繃涓€浜恒€備笢瑗挎柟鍚戠殑浜鸿繃妗ラ渶鍚屾銆?
**瑙ｇ瓟锛堜氦鏇块€氳閬垮厤楗ラタ锛?*:
```
int east_waiting=0, west_waiting=0, east_count=0, west_count=0;
Semaphore mutex=1, bridge=1;
// 鎬濊矾锛氳褰曠瓑寰呬汉鏁帮紝杩囨ˉ璁℃暟杈句笂闄愭垨瀵归潰鏃犱汉绛夊緟鏃跺垏鎹㈡柟鍚?```

## 棰?-15锛堣鐐归€熸煡锛?
| # | 棰樼洰 | 鍏抽敭鐐?|
|---|------|--------|
| 6 | 鍚哥儫鑰呴棶棰?| 3涓惛鐑熻€?1涓緵搴斿晢锛屾瘡涓惛鐑熻€呴渶瑕佷笉鍚屼袱绉嶆潗鏂?|
| 7 | 鐫＄湢鐞嗗彂甯堝姞寮虹増 | 澶氫釜鐞嗗彂甯堝苟琛屾湇鍔?|
| 8 | 闈㈠寘甯堥棶棰?| 闃熷垪+鍙彿+澶氭湇鍔″彴 |
| 9 | 姘村垎瀛愰棶棰?| H2O锛氫袱涓狧绾跨▼+涓€涓狾绾跨▼缁勬垚姘村垎瀛?|
| 10 | 璇诲啓鍏钩 | 鍐欒€呭埌杈惧悗闃诲鏂拌鑰咃紝闃叉鍐欒€呴ゥ楗?|
| 11 | 绾㈢豢鐏矾鍙?| 鍥涗釜鏂瑰悜杞﹁締閫氳锛屼笉鑳芥湁鍐茬獊璺緞 |
| 12 | 閾惰鎺掗槦鍙彿 | 鍙栧彿鏈?澶氱獥鍙?绌洪棽澶勭悊 |
| 13 | FIFO鐞嗗彂搴?| 纭繚鍏堟潵鐨勯【瀹㈠厛鐞嗗彂 |
| 14 | 鍋滆溅鍦虹鐞?| 3涓嚭鍏ュ彛+杞︿綅璁℃暟+鏄剧ず寮曞 |
| 15 | 鏂囦欢鎵撳嵃闃熷垪 | SPOOLing绯荤粺+浼樺厛绾ф墦鍗?|

---
*鏉ユ簮: Operating System Concepts 10th Ed., 鐜嬮亾鑰冪爺鎿嶄綔绯荤粺*
"""
})

RESOURCES.append({
    "title": "鏁版嵁缁撴瀯-浜屽弶鏍戜笌閫掑綊绠楁硶棰樺簱",
    "description": "鏁版嵁缁撴瀯浜屽弶鏍戜笌閫掑綊缁忓吀涔犻25閬擄紝娑电洊閬嶅巻銆佹瀯閫犮€侀獙璇併€丩CA銆佽矾寰勫拰绛夐珮棰戦潰璇曢鍨嬶紝姣忛亾闄勯€掑綊涓庨潪閫掑綊涓ょ瑙ｆ硶銆?,
    "course": "鏁版嵁缁撴瀯", "chapter": "鏍戜笌浜屽弶鏍?, "difficulty": "INTERMEDIATE",
    "type": "QUIZ",
    "tags": ["鏁版嵁缁撴瀯", "浜屽弶鏍?, "閫掑綊", "闈㈣瘯", "棰樺簱"],
    "source_url": "https://leetcode.com/tag/binary-tree/",
    "content": """# 鏁版嵁缁撴瀯-浜屽弶鏍戜笌閫掑綊绠楁硶棰樺簱

## 鍩虹绡囷紙10棰橈級

### 棰?. 浜屽弶鏍戠殑鏈€澶ф繁搴?```python
def maxDepth(root):
    if not root: return 0
    return max(maxDepth(root.left), maxDepth(root.right)) + 1
# BFS: 闃熷垪灞傚簭閬嶅巻锛岃褰曞眰鏁?```

### 棰?. 楠岃瘉浜屽弶鎼滅储鏍?```python
def isValidBST(root, lo=float('-inf'), hi=float('inf')):
    if not root: return True
    if root.val <= lo or root.val >= hi: return False
    return isValidBST(root.left, lo, root.val) and isValidBST(root.right, root.val, hi)
# 鍏抽敭: BST鐨勬€ц川鈥斺€斿乏瀛愭爲鎵€鏈夎妭鐐?鏍?鍙冲瓙鏍戞墍鏈夎妭鐐癸紝涓嶆槸浠呮瘮杈冪埗瀛愯妭鐐?```

### 棰?. 瀵圭О浜屽弶鏍?```python
def isSymmetric(root):
    def check(p, q):
        if not p and not q: return True
        if not p or not q: return False
        return p.val == q.val and check(p.left, q.right) and check(p.right, q.left)
    return check(root, root)
```

### 棰?. 浜屽弶鏍戠殑灞傚簭閬嶅巻
```python
def levelOrder(root):
    if not root: return []
    res, queue = [], [root]
    while queue:
        level = [node.val for node in queue]
        res.append(level)
        queue = [child for node in queue for child in (node.left, node.right) if child]
    return res
```

### 棰?. 浠庡墠搴忎笌涓簭閬嶅巻鏋勯€犱簩鍙夋爲
```python
def buildTree(preorder, inorder):
    if not preorder: return None
    root = TreeNode(preorder[0])
    idx = inorder.index(preorder[0])
    root.left = buildTree(preorder[1:idx+1], inorder[:idx])
    root.right = buildTree(preorder[idx+1:], inorder[idx+1:])
    return root
```

### 棰?. 浜屽弶鏍戝睍寮€涓洪摼琛?鍓嶅簭閬嶅巻鍦ㄥ師鍦板睍寮€锛氭瘡涓妭鐐瑰乏鎸囬拡缃┖锛屽彸鎸囬拡鎸囧悜涓嬩竴涓墠搴忚妭鐐广€?
### 棰?. 濉厖姣忎釜鑺傜偣鐨勪笅涓€涓彸渚ф寚閽?灞傚簭BFS杩炴帴姣忓眰鑺傜偣锛屾垨鐢ㄩ€掑綊鍒╃敤宸插缓绔嬬殑next鎸囬拡銆?
### 棰?. 浜屽弶鏍戠殑鏈€杩戝叕鍏辩鍏?```python
def LCA(root, p, q):
    if not root or root == p or root == q: return root
    left = LCA(root.left, p, q)
    right = LCA(root.right, p, q)
    if left and right: return root
    return left or right
```

### 棰?. 浜屽弶鏍戠殑鎵€鏈夎矾寰?DFS + 鍥炴函锛屾敹闆嗘牴鍒版墍鏈夊彾鑺傜偣鐨勮矾寰勩€?
### 棰?0. 缈昏浆浜屽弶鏍戯紙闀滃儚锛?```python
def invertTree(root):
    if root:
        root.left, root.right = invertTree(root.right), invertTree(root.left)
    return root
```

## 杩涢樁绡囷紙15棰樿鐐癸級

| # | 棰樼洰 | 鏍稿績鎬濊矾 |
|---|------|---------|
| 11 | 浜屽弶鏍戠殑鏈€澶ц矾寰勫拰 | 鍚庡簭閬嶅巻+璐＄尞鍊?|
| 12 | 浜屽弶鏍戠殑搴忓垪鍖栦笌鍙嶅簭鍒楀寲 | 鍓嶅簭/灞傚簭+鐗规畩鏍囪null |
| 13 | 瀹屽叏浜屽弶鏍戠殑鑺傜偣涓暟 | 鍒╃敤瀹屽叏浜屽弶鏍戞€ц川O(log虏n) |
| 14 | 浜屽弶鎼滅储鏍戠殑绗琸灏忓厓绱?| 涓簭閬嶅巻鍒扮k涓仠姝?|
| 15 | 鎶夿ST杞崲涓虹疮鍔犳爲 | 閫嗕腑搴忥紙鍙斥啋鏍光啋宸︼級 |
| 16 | 鍚堝苟浜屽弶鏍?| 鍚屾鍓嶅簭閬嶅巻锛屽搴斾綅缃浉鍔?|
| 17 | 浜屽弶鏍戠殑鐩村緞 | 鍚庡簭姹傛繁搴︽椂鏇存柊鍏ㄥ眬鐩村緞 |
| 18 | 浜屽弶鏍戜腑鎵€鏈夎窛绂讳负K鐨勮妭鐐?| 寤哄浘锛堢埗鎸囬拡锛?BFS |
| 19 | 浜屽弶鏍戠殑鍚庡簭閬嶅巻(闈為€掑綊) | 鍙屾爤娉曟垨prev鎸囬拡娉?|
| 20 | 浜屽弶鎼滅储鏍戠殑鎻掑叆/鍒犻櫎 | 鍒犻櫎鍒嗕笁绉嶆儏鍐?鍙?鍗曞瓙/鍙屽瓙 |
| 21 | 琚洿缁曠殑鑺傜偣 | 涓夎壊鏍囪娉?|
| 22 | 骞宠　浜屽弶鏍戝垽瀹?| 鑷簳鍚戜笂杩斿洖楂樺害鍜屽钩琛℃爣蹇?|
| 23 | 浜屽弶鏍戞渶灏忔繁搴?| BFS閬囩涓€涓彾鑺傜偣鍗宠繑鍥?|
| 24 | 宸﹀彾瀛愪箣鍜?| 閬嶅巻鏃跺姞鐖惰妭鐐规爣蹇?|
| 25 | 鎵炬爲宸︿笅瑙掔殑鍊?| BFS浠庡彸寰€宸﹀眰搴忛亶鍘?|

---
*鏉ユ簮: LeetCode, 鍓戞寚Offer, 绋嬪簭鍛樹唬鐮侀潰璇曟寚鍗?
"""
})

RESOURCES.append({
    "title": "璁＄畻鏈虹綉缁?IP涓庤矾鐢卞崗璁搴?,
    "description": "璁＄畻鏈虹綉缁淚P鍦板潃璁＄畻涓庤矾鐢卞崗璁範棰?0閬擄紝娑电洊瀛愮綉鍒掑垎銆丆IDR鑱氬悎銆丷IP璺濈鍚戦噺銆丱SPF閾捐矾鐘舵€併€丅GP璺緞閫夋嫨绛夋牳蹇冭€冪偣锛岄檮璇︾粏璁＄畻姝ラ銆?,
    "course": "璁＄畻鏈虹綉缁?, "chapter": "缃戠粶灞?, "difficulty": "INTERMEDIATE",
    "type": "QUIZ",
    "tags": ["璁＄畻鏈虹綉缁?, "IP鍦板潃", "瀛愮綉鍒掑垎", "璺敱", "棰樺簱"],
    "source_url": "https://www.rfc-editor.org/",
    "content": """# 璁＄畻鏈虹綉缁?IP鍦板潃涓庤矾鐢卞崗璁搴?
## 棰?. 瀛愮綉鍒掑垎
鏌愬叕鍙歌幏寰桟绫诲湴鍧€200.1.1.0/24锛岄渶瑕佸垝鍒?涓瓙缃戯紝姣忓瓙缃戞渶澶?0鍙颁富鏈恒€傝鍒掑垎瀛愮綉銆?
**瑙ｇ瓟**: 30涓绘満闇€5浣嶄富鏈轰綅(2鈦?2=30鈮?0), 瀛愮綉浣?8-5=3, 鍙垝2鲁=8涓瓙缃戔墺5
- 瀛愮綉鎺╃爜: 255.255.255.224 (/27)
- 缃戠粶鍦板潃: 200.1.1.0/27, 200.1.1.32/27, 200.1.1.64/27, ..., 200.1.1.224/27
- 姣忓瓙缃慖P鑼冨洿: .1-.30, .33-.62, .65-.94, ...
- 姣忓瓙缃戝箍鎾湴鍧€: .31, .63, .95, ..., .255

## 棰?. CIDR璺敱鑱氬悎
灏嗕互涓嬬綉缁滆仛鍚堟垚鏈€灏戠殑CIDR鍧? 192.168.1.0/24, 192.168.2.0/24, 192.168.3.0/24, 192.168.4.0/24

**瑙ｇ瓟**: 192.168.0.0/21锛堣仛鍚?92.168.0.0-192.168.7.255鍏?涓?24锛?
## 棰?. 璺濈鍚戦噺璺敱绠楁硶
RIP鐢ㄨ窛绂诲悜閲忥紙Bellman-Ford锛夛紝鏈€澶ц烦鏁?5锛?6=鈭烇級锛屾瘡30s浜ゆ崲璺敱琛ㄣ€傛敹鏁涙參锛屾湁璁℃暟鍒版棤绌烽棶棰橈紙瑙ｅ喅锛氭按骞冲垎鍓?姣掓€у弽杞?瑙﹀彂鏇存柊锛夈€?
## 棰?. OSPF閾捐矾鐘舵€佽矾鐢?- Hello鍗忚鍙戠幇閭诲眳鈫扡SA娉涙椽鈫扴PF(Dijkstra)璁＄畻鏈€鐭矾寰勬爲
- 鍖哄煙鍒掑垎: Backbone(Area 0) + 鏅€氬尯鍩?- DR/BDR閫変妇: 骞挎挱缃戠粶鍑忓皯閭绘帴鍏崇郴鏁?- LSA绫诲瀷: Type 1(璺敱鍣? Type 2(缃戠粶) Type 3(姹囨€? Type 4(ASBR) Type 5(澶栭儴)

## 棰?. BGP璺緞閫夋嫨
BGP閫夎矾13鏉″噯鍒欙紙鍓?鏉℃渶閲嶈锛夛細
1. 鏈€楂楲ocal Preference 鈫?2. 鏈€鐭瑼S Path 鈫?3. 鏈€浣嶰rigin Type(IGP<EGP<Incomplete) 鈫?4. 鏈€浣嶮ED 鈫?5. eBGP浼樺厛浜巌BGP

## 棰?. 瀛愮綉璁＄畻棰?IP: 172.16.100.50/255.255.240.0锛屾眰缃戠粶鍙枫€佸箍鎾湴鍧€銆佸彲鐢↖P鑼冨洿銆?**瑙?*: 240=11110000, /20, 缃戠粶鍙?72.16.96.0, 骞挎挱172.16.111.255, 鍙敤172.16.96.1-172.16.111.254

## 棰?-20 瑕佺偣閫熸煡

| # | 棰樼洰 | 鍏抽敭鐐?|
|---|------|--------|
| 7 | NAT绌胯秺 | STUN/TURN/ICE鍗忚 |
| 8 | ICMP搴旂敤 | ping(TTL瓒呮椂)/traceroute(绔彛涓嶅彲杈? |
| 9 | 璺敱鐜矾閬垮厤 | 姘村钩鍒嗗壊/姣掓€у弽杞?Holddown璁℃椂鍣?|
| 10 | IP鍒嗙墖涓庨噸缁?| MF/DF鏍囧織+鍋忕Щ閲忥紙8瀛楄妭涓哄崟浣嶏級 |
| 11 | ARP娆洪獥鍘熺悊 | 浼€燗RP搴旂瓟瀹炵幇涓棿浜烘敾鍑?|
| 12 | DHCP鍥涙鎻℃墜 | Discover鈫扥ffer鈫扲equest鈫扐CK |
| 13 | IPv6鏃犵姸鎬佽嚜鍔ㄩ厤缃?| SLAAC (Router Solicitation/Advertisement) |
| 14 | 澶氭挱璺敱 | IGMP + PIM-SM/PIM-DM |
| 15 | MPLS鏍囩浜ゆ崲 | LDP鍒嗗彂鏍囩锛孎EC鍒嗙被 |
| 16 | VLSM璁捐 | 涓嶅悓瀛愮綉涓嶅悓鎺╃爜锛屾渶澶у寲鍦板潃鍒╃敤鐜?|
| 17 | 绛栫暐璺敱(PBR) | 鍩轰簬婧愬湴鍧€/鍗忚/绔彛閫夎矾 |
| 18 | ECMP璐熻浇鍧囪　 | 绛変环澶氳矾寰勶紝瀵规祦/瀵瑰寘鍒嗘祦 |
| 19 | BGP璺敱鍙嶅皠鍣?| RR+Cluster List闃茬幆锛屽噺灏慖BGP鍏ㄨ繛鎺?|
| 20 | SDN鏋舵瀯 | 鎺у埗闈?Controller)涓庢暟鎹潰(Switch)鍒嗙 |

---
*鏉ユ簮: RFC 791(IP), RFC 2328(OSPF), RFC 4271(BGP), 璁＄畻鏈虹綉缁滆嚜椤跺悜涓?Kurose)*
"""
})

RESOURCES.append({
    "title": "鏁版嵁搴撳師鐞?SQL鏌ヨ涓庝紭鍖栭搴?,
    "description": "SQL鏌ヨ涓庢暟鎹簱浼樺寲楂橀璇曢30閬擄紝娑电洊澶氳〃JOIN銆佸瓙鏌ヨ銆佺獥鍙ｅ嚱鏁般€佺储寮曡璁°€佷簨鍔￠殧绂荤骇鍒€佹參鏌ヨ浼樺寲绛夋牳蹇冭€冪偣锛岄檮绛旀鍜孍XPLAIN鍒嗘瀽銆?,
    "course": "鏁版嵁搴撳師鐞?, "chapter": "SQL涓庢煡璇紭鍖?, "difficulty": "INTERMEDIATE",
    "type": "QUIZ",
    "tags": ["鏁版嵁搴?, "SQL", "鏌ヨ浼樺寲", "绱㈠紩", "棰樺簱"],
    "source_url": "https://www.postgresql.org/docs/current/sql.html",
    "content": """# 鏁版嵁搴撳師鐞?SQL鏌ヨ涓庝紭鍖栭搴?
## 棰?. 绗簩楂樿柂姘?```sql
-- 鍛樺伐琛?employee(id, name, salary)
SELECT MAX(salary) AS SecondHighestSalary
FROM employee
WHERE salary < (SELECT MAX(salary) FROM employee);
-- 鎴栫敤绐楀彛鍑芥暟: DENSE_RANK
```

## 棰?. 閮ㄩ棬鏈€楂樺伐璧?```sql
-- employee(id,name,salary,dept_id), department(id,name)
SELECT d.name AS dept, e.name AS emp, e.salary
FROM employee e
JOIN department d ON e.dept_id = d.id
WHERE (e.dept_id, e.salary) IN (
    SELECT dept_id, MAX(salary) FROM employee GROUP BY dept_id
);
-- 鎴栫敤RANK() OVER (PARTITION BY dept_id ORDER BY salary DESC)
```

## 棰?. 杩炵画鍑虹幇N娆?```sql
-- 鎵惧嚭杩炵画鍑虹幇鑷冲皯3娆＄殑鏁板瓧
SELECT DISTINCT l1.num AS ConsecutiveNums
FROM logs l1, logs l2, logs l3
WHERE l1.id = l2.id - 1 AND l2.id = l3.id - 1
  AND l1.num = l2.num AND l2.num = l3.num;
-- 鎴栫敤绐楀彛鍑芥暟 LAG/LEAD
```

## 棰?. 鐢ㄦ埛鐣欏瓨鐜?璁＄畻娆℃棩鐣欏瓨鐜囷細鐧诲綍娆℃棩鍐嶆鐧诲綍鐨勭敤鎴?褰撳ぉ鎬荤敤鎴锋暟銆?```sql
SELECT a.login_date,
       COUNT(DISTINCT b.user_id)*1.0/COUNT(DISTINCT a.user_id) AS retention
FROM login a
LEFT JOIN login b ON a.user_id=b.user_id AND b.login_date=a.login_date+1
GROUP BY a.login_date;
```

## 棰?. 绱㈠紩澶辨晥鍦烘櫙
WHERE鏉′欢涓摢浜涘啓娉曚細瀵艰嚧绱㈠紩澶辨晥锛?1. 绱㈠紩鍒椾笂浣跨敤鍑芥暟: `WHERE YEAR(create_time)=2024` 鈫?澶辨晥
2. 闅愬紡绫诲瀷杞崲: `WHERE phone=13800138000` (phone鏄痸archar) 鈫?澶辨晥
3. LIKE鍓嶅妯＄硦: `WHERE name LIKE '%test'` 鈫?澶辨晥
4. OR杩炴帴闈炵储寮曞垪 鈫?鍙兘澶辨晥
5. 澶嶅悎绱㈠紩涓嶆弧瓒虫渶宸﹀墠缂€ 鈫?澶辨晥

## 棰?. 鎱㈡煡璇㈣瘖鏂祦绋?1. 寮€鍚參鏌ヨ鏃ュ織 `long_query_time=2`
2. `EXPLAIN ANALYZE` 鏌ョ湅瀹為檯鎵ц璁″垝鍜岃€楁椂
3. 妫€鏌ype鍒? ALL(鍏ㄨ〃鎵弿鈫掗渶绱㈠紩)/index/index range/ref/const
4. 妫€鏌ows浼拌鍊间笌actual rows鐨勫樊璺濓紙缁熻淇℃伅杩囨湡锛?5. 妫€鏌xtra: Using filesort/Using temporary 鈫?闇€浼樺寲

## 棰?-30 瑕佺偣閫熸煡

| # | 鑰冪偣 | 鍏抽敭SQL/姒傚康 |
|---|------|------------|
| 7 | 鍒犻櫎閲嶅琛?| ROW_NUMBER()+PARTITION BY |
| 8 | 琛岃浆鍒?| CASE WHEN + GROUP BY 鎴?CROSSTAB |
| 9 | 绱姹傚拰 | SUM() OVER (ORDER BY) |
| 10 | 鍒嗙粍TopN | ROW_NUMBER() OVER (PARTITION BY ... ORDER BY) |
| 11 | 涓綅鏁?| PERCENTILE_CONT(0.5) 鎴栨帓搴忓彇涓棿 |
| 12 | 杩炵画鍖洪棿 | 琛屽彿宸€煎垎缁勬硶 |
| 13 | JOIN vs 瀛愭煡璇?| JOIN鍙浼樺寲鍣ㄩ噸鎺掑簭锛屽瓙鏌ヨ鍙兘鍥哄畾鎵ц椤哄簭 |
| 14 | 瑕嗙洊绱㈠紩 | SELECT鍒楀潎鍦ㄧ储寮曚腑鈫扷sing index锛屼笉鍥炶〃 |
| 15 | 绱㈠紩涓嬫帹ICP | MySQL 5.6+, 绱㈠紩灞傞潰杩囨护WHERE鏉′欢 |
| 16 | MRR浼樺寲 | Multi-Range Read: 鎵归噺鍥炶〃闅忔満IO鍙橀『搴廔O |
| 17 | 鍒嗛〉浼樺寲 | 娓告爣鍒嗛〉 WHERE id>last_id LIMIT N |
| 18 | count(*) vs count(1) | MySQL涓璫ount(*)琚紭鍖栬繃锛屾棤鍖哄埆 |
| 19 | UNION vs UNION ALL | UNION鍘婚噸锛堥澶栨帓搴忥級锛孶NION ALL涓嶅幓閲?|
| 20 | 姝婚攣妫€娴?| SHOW ENGINE INNODB STATUS; 鏌ョ湅LATEST DETECTED DEADLOCK |
| 21 | 闂撮殭閿?| InnoDB REPEATABLE READ涓嬮槻姝㈠够璇?|
| 22 | 涓ら樁娈甸攣2PL | 鍔犻攣闃舵鈫掕В閿侀樁娈碉紝浜嬪姟缁撴潫鎵嶉噴鏀?|
| 23 | 涔愯閿乿s鎮茶閿?| 鐗堟湰鍙稢AS vs SELECT FOR UPDATE |
| 24 | 鍒嗗簱鍒嗚〃 | 姘村钩鎷嗗垎锛堟寜ID鑼冨洿/鍝堝笇锛塿s 鍨傜洿鎷嗗垎锛堟寜涓氬姟妯″潡锛?|
| 25 | ReadView鍙鎬?| trx_id<min_trx_id鍙, >max_trx_id涓嶅彲瑙? 涔嬮棿鏌ユ椿璺冨垪琛?|
| 26 | MVCC鐗堟湰閾?| undo log涓茶仈澶氱増鏈紝ReadView蹇収璇?|
| 27 | redo log | 鐗╃悊鏃ュ織锛宑rash recovery锛學AL棰勫啓鏃ュ織 |
| 28 | binlog vs redo log | binlog(Server灞傞€昏緫鏃ュ織) + redo(InnoDB鐗╃悊鏃ュ織) |
| 29 | 涓ら樁娈垫彁浜?| redo prepare鈫抌inlog write鈫抮edo commit锛堜繚璇佷竴鑷存€э級 |
| 30 | EXPLAIN鍏抽敭瀛楁 | type/rows/Extra/key/key_len/ref/filtered |

---
*鏉ユ簮: PostgreSQL瀹樻柟鏂囨。, MySQL 8.0鍙傝€冩墜鍐? 楂樻€ц兘MySQL*
"""
})

RESOURCES.append({
    "title": "绠楁硶璁捐涓庡垎鏋?鍔ㄦ€佽鍒掔粡鍏搁搴?,
    "description": "鍔ㄦ€佽鍒掔粡鍏镐範棰?0閬擄紝娑电洊鑳屽寘闂銆丩CS/LIS銆佺紪杈戣窛绂汇€佸尯闂碊P銆佺姸鎬佸帇缂〥P銆佹爲褰P绛夋牳蹇冪被鍨嬶紝姣忛亾闄勭姸鎬佸畾涔夈€佽浆绉绘柟绋嬪拰浠ｇ爜瀹炵幇銆?,
    "course": "绠楁硶璁捐涓庡垎鏋?, "chapter": "鍔ㄦ€佽鍒?, "difficulty": "ADVANCED",
    "type": "QUIZ",
    "tags": ["绠楁硶", "鍔ㄦ€佽鍒?, "DP", "鑳屽寘", "棰樺簱"],
    "source_url": "https://cp-algorithms.com/dynamic_programming/intro-to-dp.html",
    "content": """# 绠楁硶璁捐涓庡垎鏋?鍔ㄦ€佽鍒掔粡鍏搁搴?
## 棰?. 0-1鑳屽寘闂
n浠剁墿鍝?閲嶉噺w[i]浠峰€紇[i],瀹归噺W銆傛瘡浠堕€夋垨涓嶉€夛紝鏈€澶у寲浠峰€笺€?```
dp[i][j] = max(dp[i-1][j], dp[i-1][j-w[i]] + v[i])  if j >= w[i]
绌洪棿浼樺寲: dp[j] = max(dp[j], dp[j-w[i]] + v[i])  // 閫嗗簭j
鏃堕棿澶嶆潅搴? O(nW), 绌洪棿O(W)
```

## 棰?. 瀹屽叏鑳屽寘
姣忎欢鐗╁搧鍙彇鏃犻檺娆°€?```
dp[j] = max(dp[j], dp[j-w[i]] + v[i])  // 姝ｅ簭j
```
涓?-1鑳屽寘鐨勫敮涓€鍖哄埆锛歫鐨勯亶鍘嗛『搴忥紒

## 棰?. 澶氶噸鑳屽寘
姣忎欢鐗╁搧鏈€澶氬彇c[i]浠躲€傝В娉曪細浜岃繘鍒舵媶鍒?O(nW log C) 鎴?鍗曡皟闃熷垪浼樺寲 O(nW)銆?
## 棰?. 浜岀淮璐圭敤鑳屽寘
鐗╁搧鏈夐噸閲弚[i]鍜屼綋绉痓[i]锛岃儗鍖呴檺鍒堕噸閲廤浣撶НB銆?```
dp[j][k] = max(dp[j][k], dp[j-w[i]][k-b[i]] + v[i])
```

## 棰?. 鍒嗙粍鑳屽寘
鐗╁搧鍒唊缁勶紝姣忕粍鏈€澶氶€変竴浠躲€?```
for 姣忕粍: for j=W..0: for 璇ョ粍姣忎欢鐗╁搧: dp[j] = max(dp[j], dp[j-w]+v)
```

## 棰?. 鏈€闀垮叕鍏卞瓙搴忓垪(LCS)
```
if s1[i]==s2[j]: dp[i][j] = dp[i-1][j-1] + 1
else: dp[i][j] = max(dp[i-1][j], dp[i][j-1])
O(nm)
```

## 棰?. 鏈€闀块€掑瀛愬簭鍒?LIS)
```
DP: dp[i] = max(dp[j]+1) for j<i, a[j]<a[i]  // O(n虏)
璐績+浜屽垎: 缁存姢閫掑鏁扮粍tails, O(n log n)
```

## 棰?. 缂栬緫璺濈
```
dp[i][j] = min(
    dp[i-1][j] + 1,        // 鍒犻櫎
    dp[i][j-1] + 1,        // 鎻掑叆
    dp[i-1][j-1] + (a[i]!=b[j])  // 鏇挎崲
)
```

## 棰?. 鐭╅樀閾句箻
```
dp[i][j] = min(dp[i][k] + dp[k+1][j] + p[i-1]*p[k]*p[j]) for k=i..j-1
鍖洪棿DP: 鎸夐暱搴en浠庡皬鍒板ぇ璁＄畻
```

## 棰?0. 姝ｅ垯琛ㄨ揪寮忓尮閰?```
if p[j-1]=='*':
    dp[i][j] = dp[i][j-2] or (match(s[i-1],p[j-2]) and dp[i-1][j])
elif match(s[i-1], p[j-1]):
    dp[i][j] = dp[i-1][j-1]
```

## 棰?1-20 鍒嗙被閫熸煡

| 绫诲瀷 | # | 棰樼洰 | 鍏抽敭鎶€宸?|
|------|---|------|---------|
| 璺緞DP | 11 | 涓嶅悓璺緞(鏈夐殰纰? | dp[i][j]=dp[i-1][j]+dp[i][j-1] |
| 璺緞DP | 12 | 鏈€灏忚矾寰勫拰 | 鍚屼笂锛屽彇min |
| 鎵撳鍔垗 | 13 | House Robber | dp[i]=max(dp[i-1],dp[i-2]+nums[i]) |
| 鎵撳鍔垗 | 14 | House Robber II(鐜舰) | 鍒嗙被璁ㄨ:鍋风涓€闂?涓嶅伔绗竴闂?|
| 鑲＄エ涔板崠 | 15 | 鏈€澶欿娆′氦鏄?| dp[i][k][0/1] 涓夌淮鐘舵€?|
| 鍖洪棿DP | 16 | 鎴虫皵鐞?| dp[i][j]=max(dp[i][k]+dp[k][j]+nums[i]nums[k]nums[j]) |
| 鍖洪棿DP | 17 | 鐭冲瓙鍚堝苟 | dp[i][j]=min(dp[i][k]+dp[k+1][j])+sum[i..j] |
| 鐘舵€佸帇缂?| 18 | TSP鏃呰鍟?| dp[mask][i]=min(dp[mask^1<<i][j]+dist[j][i]) |
| 鏍戝舰DP | 19 | 浜屽弶鏍戞渶澶х嫭绔嬮泦 | dp[node][0/1]閫夋垨涓嶉€?|
| 鏍戝舰DP | 20 | 鏍戠殑鏈€闀胯矾寰?鐩村緞) | 鍚庡簭閬嶅巻姹傛瘡涓妭鐐瑰悜涓嬫渶娣卞拰娆℃繁 |

---
*鏉ユ簮: Introduction to Algorithms (CLRS), LeetCode, Codeforces DP涓撻*
"""
})

RESOURCES.append({
    "title": "绂绘暎鏁板-閫昏緫涓庨泦鍚堣棰樺簱",
    "description": "绂绘暎鏁板鍛介閫昏緫銆佽皳璇嶉€昏緫銆侀泦鍚堣銆佸叧绯讳笌鍑芥暟涔犻25閬擄紝娑电洊鐪熷€艰〃銆佽寖寮忋€佹帹鐞嗐€佸叧绯绘€ц川鍒ゅ畾銆侀棴鍖呰绠椼€佺瓑浠峰叧绯讳笌鍒掑垎绛夎€冪偣锛岄檮璇︾粏瑙ｆ瀽銆?,
    "course": "绂绘暎鏁板", "chapter": "閫昏緫涓庨泦鍚?, "difficulty": "INTERMEDIATE",
    "type": "QUIZ",
    "tags": ["绂绘暎鏁板", "閫昏緫", "闆嗗悎璁?, "鍏崇郴", "棰樺簱"],
    "source_url": "https://ocw.mit.edu/courses/6-042j-mathematics-for-computer-science/",
    "content": """# 绂绘暎鏁板-閫昏緫涓庨泦鍚堣棰樺簱

## 棰?. 鍛介閫昏緫绛夊€兼紨绠?璇佹槑: (P鈫扱) 鈭?(P鈫扲) 鈬?P 鈫?(Q鈭)

**璇佹槑**:
(P鈫扱)鈭?P鈫扲) 鈬?(卢P鈭≦)鈭?卢P鈭≧) 鈬?卢P鈭?Q鈭) 鈬?P鈫?Q鈭)

## 棰?. 姹備富鏋愬彇鑼冨紡
姹?(P鈭)鈫扲 鐨勪富鏋愬彇鑼冨紡銆?**瑙?*: 卢(P鈭)鈭≧ 鈬?卢P鈭琎鈭≧ 锛堝凡鏄瀽鍙栬寖寮忥紝涓绘瀽鍙栭渶琛ュ叏鏋佸皬椤癸級

## 棰?. 璋撹瘝閫昏緫缈昏瘧
鐢ㄨ皳璇嶉€昏緫琛ㄧず锛?姣忎釜鍠滄鏁板鐨勫鐢熼兘鍠滄璁＄畻鏈虹瀛?
**瑙?*: 鈭€x (Student(x) 鈭?Like(x, Math) 鈫?Like(x, CS))

## 棰?. 闆嗗悎杩愮畻
A={1,2,3,4}, B={3,4,5,6}, C={1,3,5,7}銆傛眰(A鈭〣)鈭?B-C)銆?**瑙?*: A鈭〣={3,4}, B-C={4,6}锛堝幓鎺塀涓睘浜嶤鐨?,5锛? 缁撴灉={3,4,6}

## 棰?. 骞傞泦涓庣瑳鍗″皵绉?鑻A|=3, |B|=2锛屾眰|P(A脳B)|銆?**瑙?*: |A脳B|=6, |P(A脳B)|=2鈦?64

## 棰?. 鍏崇郴鎬ц川鍒ゅ畾
R={(1,1), (2,2), (3,3), (1,2), (2,1)} 鍦ㄩ泦鍚坽1,2,3}涓婂垽瀹氭€ц川銆?- 鑷弽: 鉁?(姣忓厓绱犳湁(a,a))
- 瀵圭О: 鉁?((1,2)涓?2,1)瀵瑰簲)
- 鍙嶅绉? 鉁?((1,2)鍜?2,1)閮藉湪浣?鈮?)
- 浼犻€? 鉁?
## 棰?. 绛変环鍏崇郴涓庡垝鍒?A={1,2,3,4,5}锛屽叧绯籖锛歛Rb iff a鈮 (mod 2)銆傛眰绛変环绫诲拰鍟嗛泦銆?**瑙?*: 绛変环绫籟1]={1,3,5}, [2]={2,4}銆傚晢闆咥/R={{1,3,5},{2,4}}

## 棰?. 鍝堟柉鍥句笌鍋忓簭
S={1,2,3,4,6,8,9,12,18,24}锛屽亸搴忓叧绯讳负鏁撮櫎銆傜敾鍑篐asse鍥撅紝姹傛渶澶у厓/鏈€灏忓厓/鏋佸ぇ鍏?鏋佸皬鍏冦€?**瑙?*: 鏃犳渶澶у厓(澶氫釜24,18涓嶈褰兼鏁撮櫎), 鏈€灏忓厓=1, 鏋佸皬鍏?{1}, 鏋佸ぇ鍏?{24,18}

## 棰?-25 瑕佺偣閫熸煡

| # | 棰樼洰 | 鍏抽敭鏂规硶 |
|---|------|---------|
| 9 | 璇佹槑姘哥湡寮?| 鐪熷€艰〃/绛夊€兼紨绠?鍙嶈瘉娉?|
| 10 | 鍓嶆潫鑼冨紡 | 閲忚瘝鍓嶇疆+鏀瑰悕瑙勫垯 |
| 11 | 鎺ㄧ悊瑙勫垯璇佹槑 | 鈭€x(P(x)鈫扱(x)), 鈭儀P(x) 鈯?鈭儀Q(x) |
| 12 | 闆嗗悎绛夊紡璇佹槑 | 璇佹槑A鈯咮鍜孊鈯咥 |
| 13 | 瀹规枼鍘熺悊搴旂敤 | 涓夐泦鍚堝強浠ヤ笂 |
| 14 | 骞傞泦鍩烘暟 | |P(A)|=2^|A| |
| 15 | 瀵圭О宸?| A鈯旴=(A-B)鈭?B-A)=(A鈭狟)-(A鈭〣) |
| 16 | 鍏崇郴鐭╅樀涓庡浘 | 鐢?-1鐭╅樀鍜屽叧绯诲浘琛ㄧず |
| 17 | 鑷弽闂寘 | r(R)=R鈭獅(a,a)|a鈭圓} |
| 18 | 瀵圭О闂寘 | s(R)=R鈭猂鈦宦?|
| 19 | Warshall绠楁硶 | 浼犻€掗棴鍖匫(n鲁) |
| 20 | 鑹簭闆?| 姣忎釜闈炵┖瀛愰泦鏈夋渶灏忓厓 |
| 21 | 鍑芥暟绫诲瀷鍒ゅ畾 | 鍗曞皠(f(a)=f(b)鈫抋=b), 婊″皠(鈭€y鈭儀 f(x)=y) |
| 22 | 鍙嶅嚱鏁板瓨鍦ㄦ潯浠?| 鍙屽皠锛堜竴涓€瀵瑰簲锛夋墠鏈夊弽鍑芥暟 |
| 23 | 鑷劧鏁板綊绾虫硶 | 璇佹槑P(0)鈭?P(k)鈫扨(k+1))鈫掆垁nP(n) |
| 24 | 寮哄綊绾虫硶 | 璇佹槑P(0)鈭?鈭€k<n P(k)鈫扨(n))鈫掆垁nP(n) |
| 25 | 鎶藉眽鍘熺悊搴旂敤 | 鑷冲皯m+1涓墿浣撴斁鍏涓洅瀛愨啋鏌愮洅鈮? |

---
*鏉ユ簮: Discrete Mathematics and Its Applications (Rosen), MIT 6.042J*
"""
})

# 鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺?# PRACTICE 鈥?瀹炴搷妗堜緥锛堝姩鎵嬪疄楠?椤圭洰妗堜緥锛?# 鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺?
RESOURCES.append({
    "title": "瀹炴搷妗堜緥-浠庨浂鎼缓Linux寮€鍙戠幆澧?,
    "description": "鎵嬫妸鎵嬪疄鎿嶆寚鍗楋細鍦ㄨ櫄鎷熸満鎴朩SL涓惌寤哄畬鏁碙inux寮€鍙戠幆澧冿紝鍖呮嫭Ubuntu瀹夎銆佸父鐢ㄥ伐鍏烽厤缃€丼SH杩滅▼寮€鍙戙€丏ocker鐜銆乂S Code Remote閰嶇疆銆傛瘡涓€姝ラ厤鍏蜂綋鍛戒护鍜屾埅鍥捐鏄庛€?,
    "course": "鎿嶄綔绯荤粺", "chapter": "Linux瀹炶返", "difficulty": "BASIC",
    "type": "PRACTICE",
    "tags": ["Linux", "寮€鍙戠幆澧?, "瀹炴搷", "WSL", "Docker"],
    "source_url": "https://ubuntu.com/tutorials/command-line-for-beginners",
    "content": """# 瀹炴搷妗堜緥-浠庨浂鎼缓Linux寮€鍙戠幆澧?
## 瀹為獙鐩爣
鍦ㄦ湰鍦版惌寤轰竴濂楀畬鏁寸殑Linux寮€鍙戠幆澧冿紝鍙繘琛孭ython/C++/Java椤圭洰鐨勬棩甯稿紑鍙戙€?
## 鏂规閫夋嫨
| 鏂规 | 閫傜敤鍦烘櫙 | 鎬ц兘 |
|------|---------|------|
| WSL2 | Windows寮€鍙戣€呯殑棣栭€?| 鎺ヨ繎鍘熺敓 |
| VirtualBox + Ubuntu | 闇€瑕佸畬鏁存闈㈢幆澧?| 杈冨ソ |
| 浜戞湇鍔″櫒 | 闇€瑕佸叕缃戣闂?| 鍙栧喅浜庨厤缃?|
| 鍙岀郴缁?| 鎬ц兘鏋佽嚧闇€姹?| 鍘熺敓 |

## 姝ラ1: 瀹夎WSL2 (Windows)
```powershell
# PowerShell绠＄悊鍛樻ā寮?wsl --install
wsl --set-default-version 2
wsl --install -d Ubuntu-22.04
```
閲嶅惎鍚庡彲璁剧疆鐢ㄦ埛鍚嶅拰瀵嗙爜銆?
## 姝ラ2: 鍩虹閰嶇疆
```bash
# 鏇存柊绯荤粺
sudo apt update && sudo apt upgrade -y

# 瀹夎鍩虹宸ュ叿
sudo apt install -y build-essential curl wget git vim zsh

# 瀹夎Oh My Zsh
sh -c "$(curl -fsSL https://raw.github.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"

# 閰嶇疆Git
git config --global user.name "Your Name"
git config --global user.email "your@email.com"
git config --global init.defaultBranch main
```

## 姝ラ3: 瀹夎寮€鍙戣瑷€鐜
```bash
# Python
sudo apt install -y python3 python3-pip python3-venv

# Node.js (閫氳繃nvm)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
nvm install --lts

# Java
sudo apt install -y openjdk-17-jdk

# GCC/G++
sudo apt install -y gcc g++ gdb cmake
```

## 姝ラ4: 瀹夎Docker
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER  # 鍏峴udo浣跨敤docker
# 閲嶆柊鐧诲綍鐢熸晥
```

## 姝ラ5: VS Code Remote寮€鍙?1. 瀹夎VS Code + Remote Development鎵╁睍鍖?2. `Ctrl+Shift+P` 鈫?"Remote-WSL: New Window"
3. 鍦╓SL涓洿鎺ユ墦寮€椤圭洰鏂囦欢澶?4. 缁堢鑷姩浣跨敤WSL鐨凷hell

## 姝ラ6: SSH杩滅▼寮€鍙戯紙鍙€夛級
```bash
# 鏈嶅姟绔畨瑁匰SH
sudo apt install -y openssh-server
sudo systemctl enable ssh

# 鏈湴鐢熸垚瀵嗛挜
ssh-keygen -t ed25519 -C "your@email.com"
# 澶嶅埗鍏挜鍒版湇鍔″櫒
ssh-copy-id user@server-ip

# VS Code: Remote-SSH杩炴帴鍒版湇鍔″櫒
```

## 楠岃瘉娓呭崟
- [ ] `python3 --version` 姝ｅ父杈撳嚭
- [ ] `node --version` 姝ｅ父杈撳嚭
- [ ] `java -version` 姝ｅ父杈撳嚭
- [ ] `gcc --version` 姝ｅ父杈撳嚭
- [ ] `docker ps` 鏃犳姤閿?- [ ] `git --version` 姝ｅ父杈撳嚭
- [ ] VS Code鍙繛鎺SL

---
*鏉ユ簮: Microsoft WSL鏂囨。, Ubuntu瀹樻柟鏁欑▼, VS Code Remote寮€鍙戞枃妗?
"""
})

RESOURCES.append({
    "title": "瀹炴搷妗堜緥-Git鍗忓悓寮€鍙戝叏娴佺▼婕旂粌",
    "description": "妯℃嫙鐪熷疄鍥㈤槦Git宸ヤ綔娴侊細浠嶧ork鈫扖lone鈫払ranch鈫扖ommit鈫扨R鈫扖ode Review鈫掑悎骞垛啋閮ㄧ讲鐨勫畬鏁村崗鍚屽紑鍙戞祦绋嬶紝鍖呭惈鍐茬獊瑙ｅ喅銆乺ebase vs merge銆乬it bisect璋冭瘯绛夊疄鎴樺満鏅€?,
    "course": "杞欢宸ョ▼", "chapter": "鐗堟湰鎺у埗瀹炶返", "difficulty": "BASIC",
    "type": "PRACTICE",
    "tags": ["Git", "GitHub", "鍗忓悓寮€鍙?, "瀹炴搷", "PR"],
    "source_url": "https://git-scm.com/book/en/v2",
    "content": """# 瀹炴搷妗堜緥-Git鍗忓悓寮€鍙戝叏娴佺▼婕旂粌

## 鍦烘櫙璁惧畾
涓変汉鍥㈤槦寮€鍙戜竴涓狿ython Web椤圭洰锛屼娇鐢℅itHub Flow宸ヤ綔娴併€?
## 娴佺▼姒傝
```
Fork涓婃父浠撳簱 鈫?Clone鍒版湰鍦?鈫?鍒涘缓Feature鍒嗘敮 鈫?寮€鍙?鎻愪氦 鈫?Push鍒拌繙绋?鈫?鍒涘缓Pull Request 鈫?Code Review 鈫?瑙ｅ喅鍐茬獊 鈫?鍚堝苟鍒癿ain 鈫?閮ㄧ讲
```

## 姝ラ1: Fork鍜孋lone
```bash
# GitHub缃戦〉涓奆ork upstream/team-project鍒拌嚜宸辩殑璐﹀彿
git clone https://github.com/yourname/team-project.git
cd team-project
git remote add upstream https://github.com/upstream/team-project.git
git remote -v  # 楠岃瘉: origin(your fork), upstream(涓讳粨搴?
```

## 姝ラ2: 鍒涘缓鍔熻兘鍒嗘敮
```bash
git checkout -b feature/add-login-page
# 鍒嗘敮鍛藉悕瑙勮寖: feature/xxx, fix/xxx, docs/xxx, refactor/xxx
```

## 姝ラ3: 寮€鍙戜笌鎻愪氦
```bash
# 缂栬緫浠ｇ爜...
git add app/login.py tests/test_login.py
git diff --staged  # 鎻愪氦鍓嶅鏌ュ彉鏇达紙閲嶈涔犳儻锛侊級
git commit -m "feat(auth): add login page with form validation"
# 閬靛惊Conventional Commits: type(scope): description
```

## 姝ラ4: 淇濇寔鍚屾
```bash
git fetch upstream
git rebase upstream/main  # 灏嗕綘鐨勬彁浜ゅ彉鍩哄埌鏈€鏂扮殑main涓?# 瑙ｅ喅鍐茬獊锛堝鏋滄湁锛?# git add <resolved-files>
# git rebase --continue
```

## 姝ラ5: Push鍜屽垱寤篜R
```bash
git push origin feature/add-login-page
# 鍦℅itHub涓婂垱寤篜ull Request
# PR鏍囬: feat(auth): add login page with form validation
# PR鎻忚堪: 璇存槑鍙樻洿鍐呭銆佹祴璇曟柟娉曘€佹埅鍥?```

## 姝ラ6: Code Review
瀹℃煡鑰呭叧娉ㄧ偣锛?- 浠ｇ爜閫昏緫鏄惁姝ｇ‘
- 鏄惁鏈夊畨鍏ㄦ紡娲烇紙XSS/SQL娉ㄥ叆绛夛級
- 鏄惁鏈夋祴璇曡鐩?- 鍛藉悕鏄惁娓呮櫚
- 鏄惁鏈夌‖缂栫爜/榄旀硶鏁板瓧

## 姝ラ7: 鍐茬獊瑙ｅ喅瀹炴垬
```bash
# 褰揚R鏈夊啿绐佹椂
git fetch upstream
git rebase upstream/main
# 鍐茬獊鏍囪:
# <<<<<<< HEAD
# (浣犵殑鍙樻洿)
# =======
# (涓婃父鍙樻洿)
# >>>>>>>
# 鎵嬪姩缂栬緫鍚?
git add <resolved-files>
git rebase --continue
git push --force-with-lease origin feature/add-login-page
```

## 姝ラ8: git bisect璋冭瘯
褰撳彂鐜癰ug浣嗕笉纭畾鍝釜鎻愪氦寮曞叆鏃讹細
```bash
git bisect start
git bisect bad HEAD  # 褰撳墠鐗堟湰鏈夐棶棰?git bisect good v1.2.0  # 纭濂界殑鐗堟湰
# Git鑷姩浜屽垎鏌ユ壘锛屾爣璁版瘡娆＄殑good/bad
git bisect reset  # 瀹屾垚鍚庢仮澶?```

## 甯歌浜嬫晠澶勭悊

| 浜嬫晠 | 瑙ｅ喅鏂规 |
|------|---------|
| 鎻愪氦浜嗘晱鎰熶俊鎭?| `git filter-branch` 鎴?BFG Repo-Cleaner |
| 鎻愪氦鍒颁簡閿欒鍒嗘敮 | `git reset HEAD~1` + stash + checkout姝ｇ‘鍒嗘敮 |
| merge閿欎簡鍒嗘敮 | `git reset --hard HEAD~1` (鏈猵ush) |
| 璇垹浜嗗垎鏀?| `git reflog` 鎵惧洖commit hash鍐嶅缓鍒嗘敮 |

---
*鏉ユ簮: Pro Git (Scott Chacon), GitHub Flow鏂囨。, Atlassian Git鏁欑▼*
"""
})

RESOURCES.append({
    "title": "瀹炴搷妗堜緥-RESTful API鍚庣鏈嶅姟瀹屾暣寮€鍙?,
    "description": "浠庨浂寮€鍙戜竴涓猂ESTful API鍚庣鏈嶅姟鐨勫畬鏁村疄鎿嶆渚嬶細浣跨敤FastAPI妗嗘灦锛屽寘鍚敤鎴疯璇?JWT)銆丆RUD鎿嶄綔銆佹暟鎹簱ORM(SQLAlchemy)銆佽姹傞獙璇?Pydantic)銆丄PI鏂囨。鑷姩鐢熸垚銆佸崟鍏冩祴璇曘€?,
    "course": "杞欢宸ョ▼", "chapter": "API寮€鍙戝疄璺?, "difficulty": "INTERMEDIATE",
    "type": "PRACTICE",
    "tags": ["FastAPI", "RESTful", "API", "鍚庣", "瀹炴搷"],
    "source_url": "https://fastapi.tiangolo.com/tutorial/",
    "content": """# 瀹炴搷妗堜緥-RESTful API鍚庣鏈嶅姟瀹屾暣寮€鍙?
## 椤圭洰姒傝堪
寮€鍙戜竴涓畝鍗曠殑鍥句功绠＄悊API绯荤粺锛屾兜鐩栫敤鎴疯璇佸拰鍥句功CRUD銆?
## 鎶€鏈爤
- FastAPI (Web妗嗘灦)
- SQLAlchemy (ORM)
- PostgreSQL (鏁版嵁搴?
- Pydantic (鏁版嵁楠岃瘉)
- JWT (璁よ瘉)
- pytest (娴嬭瘯)

## 椤圭洰缁撴瀯
```
bookapi/
鈹溾攢鈹€ app/
鈹?  鈹溾攢鈹€ __init__.py
鈹?  鈹溾攢鈹€ main.py          # FastAPI鍏ュ彛
鈹?  鈹溾攢鈹€ config.py        # 閰嶇疆绠＄悊
鈹?  鈹溾攢鈹€ database.py      # 鏁版嵁搴撹繛鎺?鈹?  鈹溾攢鈹€ models.py        # SQLAlchemy妯″瀷
鈹?  鈹溾攢鈹€ schemas.py       # Pydantic schemas
鈹?  鈹溾攢鈹€ auth.py          # JWT璁よ瘉
鈹?  鈹溾攢鈹€ crud.py          # CRUD鎿嶄綔
鈹?  鈹斺攢鈹€ routers/
鈹?      鈹溾攢鈹€ books.py     # 鍥句功API璺敱
鈹?      鈹斺攢鈹€ users.py     # 鐢ㄦ埛API璺敱
鈹溾攢鈹€ tests/
鈹?  鈹溾攢鈹€ test_books.py
鈹?  鈹斺攢鈹€ test_users.py
鈹斺攢鈹€ requirements.txt
```

## 姝ラ1: 鏁版嵁搴撴ā鍨?```python
# models.py
from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    email = Column(String(100), unique=True)
    hashed_password = Column(String(200))
    books = relationship("Book", back_populates="owner")

class Book(Base):
    __tablename__ = "books"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), index=True)
    author = Column(String(100))
    isbn = Column(String(13), unique=True)
    price = Column(Float)
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="books")
```

## 姝ラ2: Pydantic Schema
```python
# schemas.py
from pydantic import BaseModel, EmailStr
from typing import Optional

class BookCreate(BaseModel):
    title: str
    author: str
    isbn: str
    price: float

class BookResponse(BaseModel):
    id: int
    title: str
    author: str
    isbn: str
    price: float
    class Config: from_attributes = True

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
```

## 姝ラ3: JWT璁よ瘉
```python
# auth.py
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=30))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
```

## 姝ラ4: API璺敱
```python
# routers/books.py
from fastapi import APIRouter, Depends, HTTPException, status
from .. import crud, schemas, auth

router = APIRouter(prefix="/books", tags=["books"])

@router.get("/", response_model=list[schemas.BookResponse])
def list_books(skip: int = 0, limit: int = 100, db = Depends(get_db)):
    return crud.get_books(db, skip=skip, limit=limit)

@router.post("/", response_model=schemas.BookResponse, status_code=201)
def create_book(book: schemas.BookCreate, db = Depends(get_db),
                current_user = Depends(auth.get_current_user)):
    return crud.create_book(db, book, current_user.id)

@router.get("/{book_id}", response_model=schemas.BookResponse)
def get_book(book_id: int, db = Depends(get_db)):
    book = crud.get_book(db, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book
```

## 姝ラ5: 娴嬭瘯
```python
# tests/test_books.py
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_create_book(auth_headers):
    resp = client.post("/books/", json={
        "title": "Clean Code", "author": "Robert Martin",
        "isbn": "9780132350884", "price": 39.99
    }, headers=auth_headers)
    assert resp.status_code == 201
    assert resp.json()["title"] == "Clean Code"
```

## 姝ラ6: 杩愯鍜孉PI鏂囨。
```bash
uvicorn app.main:app --reload
# 璁块棶 http://localhost:8000/docs 鏌ョ湅鑷姩鐢熸垚鐨凷wagger鏂囨。
# 璁块棶 http://localhost:8000/redoc 鏌ョ湅ReDoc鏂囨。
```

## 楠屾敹鏍囧噯
- [ ] POST /users/ 娉ㄥ唽鐢ㄦ埛锛屽瘑鐮丅Crypt鍔犲瘑瀛樺偍
- [ ] POST /token 鐧诲綍鑾峰彇JWT token
- [ ] GET /books/ 鍒嗛〉鍒楀嚭鍥句功
- [ ] POST /books/ 鍒涘缓鍥句功锛堥渶璁よ瘉锛?- [ ] GET /books/{id} 鎸塈D鑾峰彇鍥句功璇︽儏
- [ ] PUT /books/{id} 鏇存柊鍥句功
- [ ] DELETE /books/{id} 鍒犻櫎鍥句功锛堜粎鍒涘缓鑰呭彲鍒狅級
- [ ] 422杈撳叆楠岃瘉 鑷姩鐢熸垚閿欒鍝嶅簲
- [ ] 鎵€鏈夌鐐规湁鍗曞厓娴嬭瘯瑕嗙洊

---
*鏉ユ簮: FastAPI瀹樻柟鏂囨。, Pydantic V2鏂囨。, SQLAlchemy 2.0鏂囨。*
"""
})

RESOURCES.append({
    "title": "瀹炴搷妗堜緥-鏁版嵁搴撶储寮曚紭鍖栧疄鎴?,
    "description": "鏁版嵁搴撶储寮曚紭鍖栧姩鎵嬪疄楠岋細鍦ㄤ竴涓湁100涓囪鏁版嵁鐨勮〃涓婏紝閫愭娣诲姞绱㈠紩瑙傚療鍒版煡璇㈡€ц兘鍙樺寲銆傛兜鐩朎XPLAIN鍒嗘瀽銆佸崟鍒楃储寮?澶嶅悎绱㈠紩/瑕嗙洊绱㈠紩瀵规瘮銆佺储寮曢€夋嫨鎬ц绠椼€佹參鏌ヨ鏃ュ織閰嶇疆銆?,
    "course": "鏁版嵁搴撳師鐞?, "chapter": "鏌ヨ浼樺寲瀹炶返", "difficulty": "INTERMEDIATE",
    "type": "PRACTICE",
    "tags": ["鏁版嵁搴?, "绱㈠紩浼樺寲", "EXPLAIN", "瀹炴搷", "PostgreSQL"],
    "source_url": "https://www.postgresql.org/docs/current/indexes.html",
    "content": """# 瀹炴搷妗堜緥-鏁版嵁搴撶储寮曚紭鍖栧疄鎴?
## 瀹為獙鐜鍑嗗
```sql
-- PostgreSQL
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    amount DECIMAL(10,2),
    status VARCHAR(20),
    created_at TIMESTAMP DEFAULT NOW()
);

-- 鎻掑叆100涓囪娴嬭瘯鏁版嵁
INSERT INTO orders (user_id, product_id, amount, status, created_at)
SELECT
    floor(random() * 10000 + 1)::int,
    floor(random() * 1000 + 1)::int,
    (random() * 1000)::decimal(10,2),
    (ARRAY['pending','paid','shipped','cancelled'])[floor(random()*4+1)],
    timestamp '2023-01-01' + random() * interval '365 days'
FROM generate_series(1, 1000000);

ANALYZE orders;  -- 鏇存柊缁熻淇℃伅
```

## 瀹為獙1: 鏃犵储寮曞叏琛ㄦ壂鎻?```sql
EXPLAIN ANALYZE
SELECT * FROM orders WHERE user_id = 42;

-- 缁撴灉: Parallel Seq Scan, 鎵ц鏃堕棿~150ms
-- rows=100 (瀹為檯100琛?, 浣嗘壂鎻忎簡鍏ㄨ〃100涓囪
```

## 瀹為獙2: 娣诲姞鍗曞垪绱㈠紩
```sql
CREATE INDEX idx_orders_user_id ON orders(user_id);

EXPLAIN ANALYZE
SELECT * FROM orders WHERE user_id = 42;
-- 缁撴灉: Index Scan using idx_orders_user_id, ~0.5ms!
-- 鎻愬崌: 300x
```
**瑙傚療**: Index Scan 鈫?鐩存帴瀹氫綅鍒扮鍚堟潯浠剁殑琛岋紱鑻ョ粨鏋滈泦鍗犳瘮澶?>5-10%)锛屼紭鍖栧櫒鍙兘浠嶉€塖eq Scan銆?
## 瀹為獙3: 澶嶅悎绱㈠紩 vs 鍗曞垪绱㈠紩
```sql
-- 鏌ヨ: 鏌愮敤鎴锋煇鐘舵€佺殑璁㈠崟
EXPLAIN ANALYZE
SELECT * FROM orders WHERE user_id = 42 AND status = 'paid';

-- 鏂规A: 涓や釜鍗曞垪绱㈠紩
CREATE INDEX idx_user ON orders(user_id);
CREATE INDEX idx_status ON orders(status);
-- 鍙兘鍙敤1涓储寮曪紝鐒跺悗杩囨护鍙︿竴鏉′欢

-- 鏂规B: 澶嶅悎绱㈠紩
CREATE INDEX idx_user_status ON orders(user_id, status);
-- Bitmap Index Scan 鎴?Index Scan, ~0.3ms
```
**鍘熷垯**: 绛夊€兼潯浠跺垪鍦ㄥ鍚堢储寮曞墠鍒楋紝鑼冨洿鏉′欢鍒楀湪鍚庛€?
## 瀹為獙4: 瑕嗙洊绱㈠紩娑堥櫎鍥炶〃
```sql
-- 鏌ヨ鍙彇user_id鍜宎mount
EXPLAIN ANALYZE
SELECT user_id, amount FROM orders WHERE user_id = 42;

-- 鏅€氱储寮昳dx_user_id: 鎵惧埌row浣嶇疆鈫掑洖琛ㄥ彇amount
-- 瑕嗙洊绱㈠紩:
CREATE INDEX idx_user_amount ON orders(user_id) INCLUDE (amount);
-- 缁撴灉: Index Only Scan, ~0.2ms (鏃犻渶鍥炶〃)
```

## 瀹為獙5: 绱㈠紩澶辨晥鍦烘櫙瑙傚療
```sql
-- 1. 鍑芥暟鍖呰９鍒?鈫?Seq Scan
EXPLAIN ANALYZE SELECT * FROM orders WHERE DATE(created_at)='2023-06-15';
-- 淇: 鐢ㄨ寖鍥存煡璇?-- WHERE created_at >= '2023-06-15' AND created_at < '2023-06-16'

-- 2. 鍓嶅妯＄硦LIKE 鈫?Seq Scan
EXPLAIN ANALYZE SELECT * FROM orders WHERE status LIKE '%ped';

-- 3. OR鏉′欢(閮ㄥ垎鍒楁棤绱㈠紩) 鈫?鍙兘Seq Scan
EXPLAIN ANALYZE SELECT * FROM orders WHERE user_id=1 OR amount>500;
```

## 瀹為獙6: 鏌ョ湅绱㈠紩浣跨敤鎯呭喌
```sql
-- 鏌ョ湅鏈娇鐢ㄧ殑绱㈠紩
SELECT schemaname, tablename, indexname, idx_scan, idx_tup_read
FROM pg_stat_user_indexes
WHERE idx_scan = 0
ORDER BY pg_relation_size(indexrelid) DESC;

-- 鏌ョ湅琛ㄤ笂绱㈠紩鐨勫ぇ灏?SELECT tablename, indexname,
       pg_size_pretty(pg_relation_size(indexrelid)) AS size
FROM pg_stat_user_indexes
WHERE tablename = 'orders'
ORDER BY pg_relation_size(indexrelid) DESC;
```

## 瀹為獙缁撹
| 浼樺寲鎵嬫 | 鎬ц兘鎻愬崌 | 浠ｄ环 |
|---------|---------|------|
| 鍗曞垪绱㈠紩(绛夊€兼煡璇? | 10-1000x | 鍐欐搷浣滃彉鎱?瀛樺偍 |
| 澶嶅悎绱㈠紩(澶氬垪绛夊€? | 棰濆2-5x | 鏇村ぇ鐨勭储寮?|
| 瑕嗙洊绱㈠紩 | 棰濆1.5-3x | 棰濆瀛樺偍 |
| 閮ㄥ垎绱㈠紩(WHERE) | 鍚屼笂 | 浠呴儴鍒嗘煡璇㈠彈鐩?|

---
*鏉ユ簮: PostgreSQL瀹樻柟绱㈠紩鏂囨。, Use The Index Luke (Winand)*
"""
})

RESOURCES.append({
    "title": "瀹炴搷妗堜緥-缃戠粶鎶撳寘涓庡崗璁垎鏋愬疄楠?,
    "description": "浣跨敤Wireshark/tcpdump杩涜缃戠粶鍗忚鍒嗘瀽鐨勫姩鎵嬪疄楠岋細鎹曡幏HTTP/HTTPS銆丏NS銆乀CP涓夋鎻℃墜銆乀LS鎻℃墜杩囩▼锛屽垎鏋愭瘡灞傚崗璁殑鍖呯粨鏋勩€傚寘鍚?涓疄楠屽満鏅拰鎴浘鏍囨敞銆?,
    "course": "璁＄畻鏈虹綉缁?, "chapter": "鍗忚鍒嗘瀽瀹炶返", "difficulty": "INTERMEDIATE",
    "type": "PRACTICE",
    "tags": ["璁＄畻鏈虹綉缁?, "Wireshark", "鎶撳寘", "鍗忚鍒嗘瀽", "瀹炴搷"],
    "source_url": "https://wiki.wireshark.org/SampleCaptures",
    "content": """# 瀹炴搷妗堜緥-缃戠粶鎶撳寘涓庡崗璁垎鏋愬疄楠?
## 瀹為獙鐜
- Wireshark (GUI鍒嗘瀽宸ュ叿)
- tcpdump (鍛戒护琛屾姄鍖?
- curl / 娴忚鍣?(浜х敓娴侀噺)

## 瀹為獙1: TCP涓夋鎻℃墜
```bash
# 缁堢1: 寮€濮嬫姄鍖?sudo tcpdump -i any -w tcp_handshake.pcap port 80

# 缁堢2: 鍙戣捣HTTP璇锋眰
curl http://example.com

# 鍋滄鎶撳寘(Ctrl+C), 鐢╓ireshark鎵撳紑tcp_handshake.pcap
```
**Wireshark杩囨护鍣?*: `tcp.flags.syn==1 or tcp.flags.fin==1`
**瑙傚療**:
- 鍖?: SYN (Client鈫扴erver, Seq=0, SYN=1)
- 鍖?: SYN+ACK (Server鈫扖lient, Seq=0, Ack=1, SYN=1, ACK=1)
- 鍖?: ACK (Client鈫扴erver, Seq=1, Ack=1, ACK=1)

## 瀹為獙2: HTTP璇锋眰涓庡搷搴?**杩囨护鍣?*: `http`
**瑙傚療**:
- 灞曞紑Hypertext Transfer Protocol灞?- GET / HTTP/1.1\\r\\nHost: example.com\\r\\n...
- 鍝嶅簲: HTTP/1.1 200 OK\\r\\nContent-Type: text/html...
- 缁熻: Statistics 鈫?HTTP 鈫?Packet Counter

## 瀹為獙3: DNS鏌ヨ杩囩▼
```bash
# 娓呯┖DNS缂撳瓨
sudo systemd-resolve --flush-caches
# 鎶撳寘
sudo tcpdump -i any -w dns_query.pcap port 53
# 鍙︿竴缁堢
nslookup github.com
```
**Wireshark杩囨护鍣?*: `dns`
**瑙傚療**:
- DNS Query: 鏌ヨgithub.com鐨凙璁板綍
- DNS Response: 杩斿洖IP鍦板潃鍒楄〃
- 鍏虫敞Transaction ID鍖归厤鏌ヨ涓庡搷搴?- 鏌ョ湅閫掑綊鏌ヨ鏍囧織浣?
## 瀹為獙4: TLS 1.3鎻℃墜
```bash
sudo tcpdump -i any -w tls_handshake.pcap port 443
# 鍙︿竴缁堢
curl -v https://www.baidu.com
```
**杩囨护鍣?*: `tls.handshake.type`
**TLS 1.3鎻℃墜娴佺▼**锛?-RTT锛?
1. ClientHello: 鏀寔鐨勫瘑鐮佸浠?Key Share (ECDHE)
2. ServerHello: 閫夊畾瀵嗙爜濂椾欢+Key Share+璇佷功+CertificateVerify+Finished
3. Client: Finished
4. 闅忓悗搴旂敤鏁版嵁鍗冲姞瀵?
瀵规瘮TLS 1.2(2-RTT)灏戜簡ServerHello Done绛夋楠ゃ€?
## 瀹為獙5: TCP鎷ュ鎺у埗瑙傚療
```bash
# 涓嬭浇澶ф枃浠跺苟鎶撳寘
curl -o /dev/null http://speedtest.tele2.net/1GB.zip &
sudo tcpdump -i any -w tcp_congestion.pcap port 80
```
**Wireshark鍒嗘瀽**: Statistics 鈫?TCP Stream Graphs 鈫?Time-Sequence (Stevens)
**瑙傚療**:
- 鎱㈠惎鍔ㄩ樁娈? cwnd鎸囨暟澧為暱锛堝寘鏁板揩閫熷鍔狅級
- 鎷ュ閬垮厤闃舵: 绾挎€у闀?- 涓㈠寘鍚? 绐楀彛鍑忓崐鈫掑揩鎭㈠鈫掔户缁嫢濉為伩鍏?
## 瀹為獙6: ICMP涓庣綉缁滆瘖鏂?```bash
# TTL瓒呮椂 (traceroute鍘熺悊)
ping -c 1 -t 1 baidu.com   # TTL=1鈫掔涓€璺宠矾鐢卞櫒杩斿洖Time Exceeded
traceroute baidu.com       # 閫愭澧炲姞TTL
```
**杩囨护鍣?*: `icmp`
**瑙傚療ICMP绫诲瀷**:
- Type 0: Echo Reply (ping鍝嶅簲)
- Type 8: Echo Request (ping璇锋眰)
- Type 11: Time Exceeded (TTL瓒呮椂)
- Type 3: Destination Unreachable

## 甯哥敤Wireshark杩囨护鍣ㄩ€熸煡
| 鐢ㄩ€?| 杩囨护鍣?|
|------|--------|
| HTTP璇锋眰 | `http.request` |
| DNS鏌ヨ | `dns.flags.response == 0` |
| TCP閲嶄紶 | `tcp.analysis.retransmission` |
| TLS Alert | `tls.alert_message` |
| 鐗瑰畾IP | `ip.addr == 192.168.1.1` |

---
*鏉ユ簮: Wireshark User Guide, TCP/IP Illustrated (Stevens), RFC 8446 (TLS 1.3)*
"""
})

RESOURCES.append({
    "title": "瀹炴搷妗堜緥-鎺掑簭绠楁硶鎬ц兘瀵规瘮瀹為獙",
    "description": "璁捐骞惰繍琛屾帓搴忕畻娉曟€ц兘瀵规瘮瀹為獙锛氬疄鐜?绉嶆帓搴忕畻娉曪紝鍦ㄤ笉鍚屾暟鎹妯?100~100000)鍜屾暟鎹垎甯?闅忔満/杩戜箮鏈夊簭/閫嗗簭/澶ч噺閲嶅)涓嬫祴璇曡繍琛屾椂闂达紝鐢╩atplotlib缁樺埗瀵规瘮鍥捐〃銆?,
    "course": "绠楁硶璁捐涓庡垎鏋?, "chapter": "鎺掑簭绠楁硶瀹炶返", "difficulty": "INTERMEDIATE",
    "type": "PRACTICE",
    "tags": ["鎺掑簭", "绠楁硶", "鎬ц兘娴嬭瘯", "Python", "瀹炴搷"],
    "source_url": "https://docs.python.org/3/howto/sorting.html",
    "content": '''# 瀹炴搷妗堜緥-鎺掑簭绠楁硶鎬ц兘瀵规瘮瀹為獙

## 瀹為獙鐩爣
绯荤粺瀵规瘮7绉嶆帓搴忕畻娉曞湪涓嶅悓鍦烘櫙涓嬬殑瀹為檯杩愯鎬ц兘銆?
## 瀹為獙浠ｇ爜妗嗘灦
```python
import random, time, sys
import matplotlib.pyplot as plt
sys.setrecursionlimit(100000)

# ... (7绉嶆帓搴忕畻娉曞疄鐜? bubble/selection/insertion/shell/merge/quick/heap)

def generate_data(n, pattern):
    if pattern == "random":
        return [random.randint(0, n) for _ in range(n)]
    elif pattern == "nearly_sorted":
        arr = list(range(n))
        for _ in range(n // 20):
            i, j = random.randint(0, n-1), random.randint(0, n-1)
            arr[i], arr[j] = arr[j], arr[i]
        return arr
    elif pattern == "reversed":
        return list(range(n, 0, -1))
    elif pattern == "many_duplicates":
        return [random.randint(0, n//100) for _ in range(n)]

def benchmark(algorithms, sizes, patterns, repeats=3):
    results = {}
    for name, fn in algorithms.items():
        results[name] = {}
        for size in sizes:
            for pat in patterns:
                times = []
                for _ in range(repeats):
                    data = generate_data(size, pat)
                    start = time.perf_counter()
                    fn(data)
                    elapsed = time.perf_counter() - start
                    times.append(elapsed)
                results[name][(size, pat)] = min(times)  # 鍙栨渶蹇?    return results

algorithms = {
    "Bubble": bubble_sort, "Selection": selection_sort,
    "Insertion": insertion_sort, "Shell": shell_sort,
    "Merge": merge_sort, "Quick": quick_sort, "Heap": heap_sort,
}

sizes = [100, 500, 1000, 5000, 10000, 50000]
patterns = ["random", "nearly_sorted", "reversed", "many_duplicates"]

results = benchmark(algorithms, sizes, patterns)

# 缁樺埗: 闅忔満鏁版嵁涓嬪悇绠楁硶鎬ц兘
plt.figure(figsize=(12, 8))
for name in algorithms:
    times = [results[name][(s, "random")] for s in sizes]
    plt.plot(sizes, times, marker='o', label=name)
plt.xscale('log'); plt.yscale('log')
plt.xlabel('Array Size (log)'); plt.ylabel('Time (s, log)')
plt.legend(); plt.grid(True, alpha=0.3)
plt.title('Sorting Algorithm Performance (Random Data)')
plt.savefig('sorting_performance.png', dpi=150)
```

## 棰勬湡瀹為獙缁撴灉

| 绠楁硶 | 闅忔満O(n虏) | 闅忔満O(n log n) | 杩戜箮鏈夊簭 | 閫嗗簭 | 澶ч噺閲嶅 |
|------|-----------|---------------|---------|------|---------|
| Bubble | 鏋佹參(>1s) | - | 浼樺寲鍚庡揩 | 鏋佹參 | 鎱?|
| Selection | 鎱?| - | 鎱?| 鎱?| 鎱?|
| Insertion | 鎱?| - | 鏋佸揩(~0.01s) | 鎱?| 灏氬彲 |
| Shell | 涓瓑 | - | 蹇?| 涓瓑 | 蹇?|
| Merge | - | 绋冲畾~0.2s | 绋冲畾 | 绋冲畾 | 绋冲畾 |
| Quick | - | 蹇珇0.1s | 鍙兘閫€鍖?| 閫€鍖?| 涓夎矾蹇帓蹇?|
| Heap | - | 涓瓑~0.3s | 涓瓑 | 涓瓑 | 涓瓑 |

## 鍏抽敭鍙戠幇锛堥渶瑕侀獙璇侊級
1. Insertion鍦╪<100涓旇繎涔庢湁搴忔椂鏄渶蹇殑
2. Quick Sort涓夎矾鍒嗗尯鍦ㄥ鐞嗗ぇ閲忛噸澶嶅厓绱犳椂纰惧帇鏍囧噯蹇帓
3. 绯荤粺鎺掑簭(Timsort)鍦ㄧ湡瀹炴暟鎹笂鐨勪紭鍔?4. 閫掑綊娣卞害瀵筂erge/Quick鍦ㄥぇ鏁版嵁閲忎笅鏄釜闂(闇€sys.setrecursionlimit)

## 瀹為獙鎶ュ憡妯℃澘
1. 瀹為獙鐩殑涓庤缃?2. 鍚勭畻娉曟纭€ч獙璇佺粨鏋?3. 瑙勬ā-鏃堕棿鍏崇郴鍥?n浠?00鍒?0000)
4. 鏁版嵁鍒嗗竷瀵圭畻娉曟€ц兘鐨勫奖鍝嶅垎鏋?5. 缁撹: 鍚勫満鏅渶浣崇畻娉曟帹鑽?
---
*鏉ユ簮: 绠楁硶瀵艰(CLRS), Python Sorting HOWTO, Timsort璁烘枃(Peters)*
'''
})

# 鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺?# CODE 鈥?浠ｇ爜绀轰緥涓庣紪绋嬫寫鎴?# 鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺?
RESOURCES.append({
    "title": "缂栫▼鎸戞垬-Python澶氱嚎绋嬩笌骞跺彂缂栫▼瀹炴垬",
    "description": "Python骞跺彂缂栫▼瀹屾暣浠ｇ爜绀轰緥涓庢寫鎴橈細threading妯″潡銆乧oncurrent.futures绾跨▼姹?杩涚▼姹犮€乤syncio寮傛缂栫▼銆乹ueue闃熷垪銆丩ock/RLock/Semaphore鍚屾鍘熻鐨勪娇鐢ㄥ満鏅拰鎬ц兘瀵规瘮銆?,
    "course": "鎿嶄綔绯荤粺", "chapter": "骞跺彂缂栫▼", "difficulty": "ADVANCED",
    "type": "CODE",
    "tags": ["Python", "骞跺彂", "澶氱嚎绋?, "asyncio", "浠ｇ爜"],
    "source_url": "https://docs.python.org/3/library/concurrency.html",
    "content": '''# Python澶氱嚎绋嬩笌骞跺彂缂栫▼瀹炴垬

## 1. 绾跨▼姹?vs 杩涚▼姹?
```python
import time, math
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

def cpu_intensive(n):
    """CPU瀵嗛泦鍨? 璁＄畻绱犳暟"""
    count = 0
    for i in range(2, n):
        is_prime = True
        for j in range(2, int(math.sqrt(i)) + 1):
            if i % j == 0:
                is_prime = False; break
        if is_prime: count += 1
    return count

def io_intensive(n):
    """IO瀵嗛泦鍨? 妯℃嫙缃戠粶璇锋眰"""
    time.sleep(0.1)
    return n * 2

def benchmark():
    tasks = list(range(100))

    # CPU瀵嗛泦鍨?鈫?杩涚▼姹犺儨鍑?    start = time.time()
    with ProcessPoolExecutor(max_workers=4) as ex:
        list(ex.map(cpu_intensive, [5000]*16))
    print(f"ProcessPool CPU: {time.time()-start:.2f}s")

    start = time.time()
    with ThreadPoolExecutor(max_workers=4) as ex:
        list(ex.map(cpu_intensive, [5000]*16))
    print(f"ThreadPool CPU: {time.time()-start:.2f}s  # GIL闄愬埗!")

    # IO瀵嗛泦鍨?鈫?绾跨▼姹犺儨鍑?    start = time.time()
    with ThreadPoolExecutor(max_workers=10) as ex:
        list(ex.map(io_intensive, tasks))
    print(f"ThreadPool IO: {time.time()-start:.2f}s")
```

## 2. 鐢熶骇鑰?娑堣垂鑰呮ā寮?
```python
import threading, queue, time, random

def producer(q: queue.Queue, n: int):
    for i in range(n):
        item = f"data_{i}"
        q.put(item)
        print(f"Produced: {item}")
        time.sleep(random.uniform(0.01, 0.1))
    q.put(None)  # 姣掍父: 閫氱煡娑堣垂鑰呯粨鏉?
def consumer(q: queue.Queue, name: str):
    while True:
        item = q.get()
        if item is None:
            q.task_done()
            break
        print(f"[{name}] Processing: {item}")
        time.sleep(random.uniform(0.05, 0.2))
        q.task_done()

q = queue.Queue(maxsize=10)
producers = [threading.Thread(target=producer, args=(q, 20))]
consumers = [threading.Thread(target=consumer, args=(q, f"C{i}")) for i in range(3)]

for t in producers + consumers: t.start()
for t in producers: t.join()
q.join()  # 绛夊緟鎵€鏈塼ask_done
```

## 3. asyncio鍗忕▼瀹炴垬

```python
import asyncio

async def fetch_url(session, url):
    """寮傛HTTP璇锋眰"""
    async with session.get(url) as resp:
        return await resp.text()

async def main():
    urls = [
        "http://httpbin.org/delay/1",
        "http://httpbin.org/delay/2",
        "http://httpbin.org/delay/1",
    ]
    import aiohttp
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_url(session, url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        for i, r in enumerate(results):
            print(f"URL {i}: {len(r) if isinstance(r, str) else r} chars")
```

## 4. 绾跨▼瀹夊叏璁℃暟鍣?
```python
import threading

# BAD: 闈炵嚎绋嬪畨鍏?class UnsafeCounter:
    def __init__(self): self.val = 0
    def inc(self): self.val += 1  # 璇?鏀?鍐? 闈炲師瀛?

# GOOD: 浣跨敤Lock
class SafeCounter:
    def __init__(self):
        self.val = 0
        self.lock = threading.Lock()
    def inc(self):
        with self.lock:
            self.val += 1

# BETTER: 浣跨敤鍘熷瓙鎿嶄綔 (Python 3.8+ 鏃燝IL鏃剁殑鑰冭檻)
# 鎴栦娇鐢?queue.Queue / multiprocessing.Value
```

## 鎸戞垬缁冧範

### 鎸戞垬1: 骞跺彂Web鐖櫕
瀹炵幇涓€涓苟鍙戠埇铏紝缁欏畾璧峰URL鍜宮ax_depth锛屼娇鐢ㄧ嚎绋嬫睜骞跺彂鎶撳彇椤甸潰骞舵彁鍙栭摼鎺ャ€?瑕佹眰: 鍘婚噸宸茶闂甎RL銆侀檺閫?姣忕涓嶈秴杩嘚涓姹?銆佷紭闆呴€€鍑?KeyboardInterrupt鏃朵繚瀛樼姸鎬?銆?
### 鎸戞垬2: 骞惰鏁版嵁澶勭悊
鐢≒rocessPoolExecutor澶勭悊100涓囪CSV鏂囦欢锛屽苟琛岃绠楁瘡鍒楃殑缁熻淇℃伅(mean/std/min/max)銆?
### 鎸戞垬3: 瀹炴椂鏃ュ織澶勭悊绯荤粺
鐢╝syncio瀹炵幇涓€涓棩蹇楀鐞嗙閬?
1. 鍗忕▼A: 妯℃嫙浠庢枃浠惰鍙栨棩蹇楄
2. 鍗忕▼B: 瑙ｆ瀽JSON鏍煎紡
3. 鍗忕▼C: 杩囨护+鑱氬悎(濡傛寜灏忔椂缁熻閿欒鏁?
4. 鍗忕▼D: 杈撳嚭鍒版帶鍒跺彴鍜屾枃浠?
---
*鏉ユ簮: Python骞跺彂缂栫▼瀹樻柟鏂囨。, Fluent Python (Ramalho)*
'''
})

RESOURCES.append({
    "title": "缂栫▼鎸戞垬-鏁版嵁缁撴瀯浠庨浂瀹炵幇",
    "description": "浠庨浂瀹炵幇鏍稿績鏁版嵁缁撴瀯鐨勭紪绋嬫寫鎴橈細鍔ㄦ€佹暟缁?ArrayList)銆侀摼琛?鍗曞悜/鍙屽悜)銆佹爤涓庨槦鍒椼€佷簩鍙夋悳绱㈡爲銆丄VL鏍戙€佸搱甯岃〃銆佷紭鍏堥槦鍒?鍫?銆佸浘(閭绘帴琛?銆傛瘡缁撴瀯鍖呭惈瀹屾暣鐨刬nsert/delete/search鎿嶄綔鍜屽崟鍏冩祴璇曘€?,
    "course": "鏁版嵁缁撴瀯", "chapter": "鏁版嵁缁撴瀯瀹炵幇", "difficulty": "INTERMEDIATE",
    "type": "CODE",
    "tags": ["鏁版嵁缁撴瀯", "Python", "瀹炵幇", "浠ｇ爜"],
    "source_url": "https://docs.python.org/3/tutorial/datastructures.html",
    "content": '''# 缂栫▼鎸戞垬-鏁版嵁缁撴瀯浠庨浂瀹炵幇

## 1. 鍔ㄦ€佹暟缁?(ArrayList)

```python
class ArrayList:
    def __init__(self, capacity=4):
        self._data = [None] * capacity
        self._size = 0

    def __len__(self): return self._size

    def __getitem__(self, index):
        if index < 0 or index >= self._size:
            raise IndexError
        return self._data[index]

    def append(self, value):
        if self._size == len(self._data):
            self._resize(len(self._data) * 2)
        self._data[self._size] = value
        self._size += 1
        # 鎽婇攢 O(1)

    def insert(self, index, value):
        if index < 0 or index > self._size:
            raise IndexError
        if self._size == len(self._data):
            self._resize(len(self._data) * 2)
        for i in range(self._size, index, -1):
            self._data[i] = self._data[i - 1]
        self._data[index] = value
        self._size += 1
        # O(n)

    def remove(self, index):
        if index < 0 or index >= self._size:
            raise IndexError
        removed = self._data[index]
        for i in range(index, self._size - 1):
            self._data[i] = self._data[i + 1]
        self._size -= 1
        if self._size < len(self._data) // 4:
            self._resize(len(self._data) // 2)
        return removed

    def _resize(self, new_cap):
        new_data = [None] * new_cap
        for i in range(self._size):
            new_data[i] = self._data[i]
        self._data = new_data
```

## 2. 鍙屽悜閾捐〃

```python
class Node:
    __slots__ = ('val', 'prev', 'next')
    def __init__(self, val, prev=None, next=None):
        self.val = val; self.prev = prev; self.next = next

class LinkedList:
    def __init__(self):
        self.head = Node(None)  # 鍝ㄥ叺澶?        self.tail = Node(None)  # 鍝ㄥ叺灏?        self.head.next = self.tail
        self.tail.prev = self.head
        self._size = 0

    def __len__(self): return self._size

    def append(self, val):
        node = Node(val, self.tail.prev, self.tail)
        self.tail.prev.next = node
        self.tail.prev = node
        self._size += 1

    def __iter__(self):
        cur = self.head.next
        while cur != self.tail:
            yield cur.val
            cur = cur.next
```

## 3. 浜屽弶鎼滅储鏍?(BST)

```python
class BSTNode:
    __slots__ = ('key', 'left', 'right')
    def __init__(self, key):
        self.key = key; self.left = None; self.right = None

class BST:
    def __init__(self):
        self.root = None

    def insert(self, key):
        self.root = self._insert(self.root, key)

    def _insert(self, node, key):
        if node is None: return BSTNode(key)
        if key < node.key:
            node.left = self._insert(node.left, key)
        elif key > node.key:
            node.right = self._insert(node.right, key)
        return node

    def search(self, key):
        return self._search(self.root, key)

    def _search(self, node, key):
        if node is None or node.key == key:
            return node
        if key < node.key:
            return self._search(node.left, key)
        return self._search(node.right, key)

    def inorder(self):
        result = []
        self._inorder(self.root, result)
        return result

    def _inorder(self, node, result):
        if node:
            self._inorder(node.left, result)
            result.append(node.key)
            self._inorder(node.right, result)
```

## 4. 鍝堝笇琛?(閾惧湴鍧€娉?

```python
class HashTable:
    LOAD_FACTOR = 0.75

    def __init__(self, capacity=8):
        self._capacity = capacity
        self._size = 0
        self._buckets = [[] for _ in range(capacity)]

    def _hash(self, key):
        return hash(key) % self._capacity

    def put(self, key, value):
        idx = self._hash(key)
        bucket = self._buckets[idx]
        for i, (k, v) in enumerate(bucket):
            if k == key:
                bucket[i] = (key, value)
                return
        bucket.append((key, value))
        self._size += 1
        if self._size / self._capacity > self.LOAD_FACTOR:
            self._resize(self._capacity * 2)

    def get(self, key):
        idx = self._hash(key)
        for k, v in self._buckets[idx]:
            if k == key: return v
        raise KeyError(key)

    def _resize(self, new_cap):
        old = self._buckets
        self._capacity = new_cap
        self._size = 0
        self._buckets = [[] for _ in range(new_cap)]
        for bucket in old:
            for k, v in bucket:
                self.put(k, v)
```

## 缂栫▼鎸戞垬

### 鎸戞垬1: AVL鏍?鍦˙ST鍩虹涓婂疄鐜癆VL鏍戠殑鏃嬭浆锛圠L/RR/LR/RL锛夛紝纭繚姣忔鎻掑叆鍚庢爲淇濇寔骞宠　銆?
### 鎸戞垬2: 浼樺厛闃熷垪(鍫?
鐢ㄦ暟缁勫疄鐜版渶灏忓爢锛屾敮鎸乸ush/pop/peek/heapify鎿嶄綔銆?
### 鎸戞垬3: 鍥?閭绘帴琛?閬嶅巻)
瀹炵幇Graph绫?閭绘帴琛ㄥ瓨鍌?锛屾敮鎸乤dd_edge銆丅FS銆丏FS锛堥€掑綊+闈為€掑綊锛夈€丏ijkstra鏈€鐭矾寰勩€佹嫇鎵戞帓搴忋€?
### 鎸戞垬4: 璺宠〃(SkipList)
瀹炵幇涓€涓敮鎸丱(log n)骞冲潎鏌ユ壘鐨勮烦琛ㄣ€?
---
*鏉ユ簮: Data Structures and Algorithms in Python (Goodrich)*
'''
})

RESOURCES.append({
    "title": "缂栫▼鎸戞垬-绠楁硶楂橀濂楄矾浠ｇ爜妯℃澘",
    "description": "绠楁硶绔炶禌鍜岄潰璇曢珮棰戜唬鐮佹ā鏉块泦鍚堬細浜屽垎鏌ユ壘/蹇€熸帓搴?褰掑苟鎺掑簭妯℃澘銆佹粦鍔ㄧ獥鍙ｃ€佸洖婧?N鐨囧悗/鍏ㄦ帓鍒?銆丅FS/DFS銆佸苟鏌ラ泦銆乀rie鏍戙€佹爲鐘舵暟缁勩€佺嚎娈垫爲銆傞檮澶嶆潅搴﹀垎鏋愬拰鏄撻敊鐐规爣娉ㄣ€?,
    "course": "绠楁硶璁捐涓庡垎鏋?, "chapter": "绠楁硶妯℃澘", "difficulty": "ADVANCED",
    "type": "CODE",
    "tags": ["绠楁硶", "妯℃澘", "闈㈣瘯", "浠ｇ爜"],
    "source_url": "https://github.com/azl397985856/leetcode",
    "content": '''# 绠楁硶楂橀濂楄矾浠ｇ爜妯℃澘

## 浜屽垎鏌ユ壘妯℃澘

```python
def binary_search(arr, target):
    """鍩虹浜屽垎: 鍦ㄦ湁搴忔暟缁勪腑鏌ユ壘target"""
    lo, hi = 0, len(arr) - 1
    while lo <= hi:
        mid = lo + (hi - lo) // 2  # 闃叉孩鍑?        if arr[mid] == target: return mid
        elif arr[mid] < target: lo = mid + 1
        else: hi = mid - 1
    return -1

def lower_bound(arr, target):
    """绗竴涓?=target鐨勪綅缃?""
    lo, hi = 0, len(arr)
    while lo < hi:
        mid = lo + (hi - lo) // 2
        if arr[mid] < target: lo = mid + 1
        else: hi = mid
    return lo

def upper_bound(arr, target):
    """绗竴涓?target鐨勪綅缃?""
    lo, hi = 0, len(arr)
    while lo < hi:
        mid = lo + (hi - lo) // 2
        if arr[mid] <= target: lo = mid + 1
        else: hi = mid
    return lo
```

## 蹇€熸帓搴忔ā鏉?
```python
import random

def quick_sort(arr, lo=0, hi=None):
    if hi is None: hi = len(arr) - 1
    if lo >= hi: return
    pivot_idx = partition(arr, lo, hi)
    quick_sort(arr, lo, pivot_idx - 1)
    quick_sort(arr, pivot_idx + 1, hi)

def partition(arr, lo, hi):
    # 闅忔満閫塸ivot闃查€€鍖?    pi = random.randint(lo, hi)
    arr[pi], arr[hi] = arr[hi], arr[pi]
    pivot = arr[hi]
    i = lo
    for j in range(lo, hi):
        if arr[j] < pivot:
            arr[i], arr[j] = arr[j], arr[i]
            i += 1
    arr[i], arr[hi] = arr[hi], arr[i]
    return i
```

## 鍥炴函妯℃澘

```python
def backtrack(path, choices):
    """鍥炴函閫氱敤妯℃澘"""
    if 婊¤冻缁撴潫鏉′欢:
        result.append(path[:])
        return

    for choice in choices:
        if 涓嶅悎娉? continue
        path.append(choice)   # 鍋氶€夋嫨
        backtrack(path, 鏂扮殑choices)
        path.pop()             # 鎾ら攢閫夋嫨

# 鍏ㄦ帓鍒楃ず渚?def permute(nums):
    res = []
    used = [False] * len(nums)
    def dfs(path):
        if len(path) == len(nums):
            res.append(path[:]); return
        for i, n in enumerate(nums):
            if used[i]: continue
            used[i] = True; path.append(n)
            dfs(path)
            used[i] = False; path.pop()
    dfs([])
    return res
```

## BFS/DFS妯℃澘

```python
from collections import deque

def bfs(graph, start):
    visited = {start}
    queue = deque([start])
    while queue:
        node = queue.popleft()
        for neighbor in graph[node]:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)
    return visited

def dfs_iterative(graph, start):
    visited = set()
    stack = [start]
    while stack:
        node = stack.pop()
        if node not in visited:
            visited.add(node)
            stack.extend(graph[node] - visited)
    return visited
```

## 骞舵煡闆?
```python
class UnionFind:
    def __init__(self, n):
        self.parent = list(range(n))
        self.rank = [0] * n

    def find(self, x):
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])  # 璺緞鍘嬬缉
        return self.parent[x]

    def union(self, x, y):
        px, py = self.find(x), self.find(y)
        if px == py: return False
        if self.rank[px] < self.rank[py]: px, py = py, px
        self.parent[py] = px
        if self.rank[px] == self.rank[py]: self.rank[px] += 1
        return True
```

## Trie (鍓嶇紑鏍?

```python
class TrieNode:
    __slots__ = ('children', 'is_end')
    def __init__(self):
        self.children = {}
        self.is_end = False

class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word):
        node = self.root
        for ch in word:
            if ch not in node.children:
                node.children[ch] = TrieNode()
            node = node.children[ch]
        node.is_end = True

    def search(self, word):
        node = self.root
        for ch in word:
            if ch not in node.children: return False
            node = node.children[ch]
        return node.is_end

    def starts_with(self, prefix):
        node = self.root
        for ch in prefix:
            if ch not in node.children: return False
            node = node.children[ch]
        return True
```

## 绾挎鏍?(鍖洪棿鏌ヨ)

```python
class SegTree:
    def __init__(self, arr):
        n = len(arr)
        self.n = n
        self.tree = [0] * (4 * n)
        self._build(arr, 0, 0, n - 1)

    def _build(self, arr, node, l, r):
        if l == r:
            self.tree[node] = arr[l]; return
        mid = (l + r) // 2
        self._build(arr, node * 2 + 1, l, mid)
        self._build(arr, node * 2 + 2, mid + 1, r)
        self.tree[node] = self.tree[node*2+1] + self.tree[node*2+2]

    def query(self, ql, qr, node=0, l=0, r=None):
        if r is None: r = self.n - 1
        if ql > r or qr < l: return 0
        if ql <= l and r <= qr: return self.tree[node]
        mid = (l + r) // 2
        return self.query(ql, qr, node*2+1, l, mid) + self.query(ql, qr, node*2+2, mid+1, r)

    def update(self, idx, val, node=0, l=0, r=None):
        if r is None: r = self.n - 1
        if l == r:
            self.tree[node] = val; return
        mid = (l + r) // 2
        if idx <= mid: self.update(idx, val, node*2+1, l, mid)
        else: self.update(idx, val, node*2+2, mid+1, r)
        self.tree[node] = self.tree[node*2+1] + self.tree[node*2+2]
```

---
*鏉ユ簮: LeetCode Discuss, CP-Algorithms, 绠楁硶绔炶禌鍏ラ棬缁忓吀*
'''
})

# 鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺?# SLIDES 鈥?璇句欢澶х翰
# 鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺?
RESOURCES.append({
    "title": "鎿嶄綔绯荤粺璇剧▼瀹屾暣璇句欢澶х翰",
    "description": "鎿嶄綔绯荤粺璇剧▼30璁茬殑PPT璇句欢澶х翰锛屾瘡璁插寘鍚煡璇嗙洰鏍囥€佹牳蹇冩蹇点€佸浘瑙ｃ€佷緥棰樺拰璇惧悗鎬濊€冮銆傞€傜敤浜庢暀甯堝璇惧拰瀛︾敓鑷瀵艰埅銆?,
    "course": "鎿嶄綔绯荤粺", "chapter": "璇剧▼缁艰堪", "difficulty": "BASIC",
    "type": "SLIDES",
    "tags": ["鎿嶄綔绯荤粺", "璇句欢", "鏁欏澶х翰"],
    "source_url": "https://pages.cs.wisc.edu/~remzi/OSTEP/",
    "content": """# 鎿嶄綔绯荤粺璇剧▼瀹屾暣璇句欢澶х翰

## 绗?璁? 鎿嶄綔绯荤粺姒傝堪
- 浠€涔堟槸鎿嶄綔绯荤粺锛堣祫婧愮鐞嗚€?鐢ㄦ埛鎺ュ彛锛?- OS鍙戝睍鍙? 鎵嬪伐鈫掓壒澶勭悊鈫掑閬撶▼搴忊啋鍒嗘椂鈫掑疄鏃垛啋缃戠粶鈫掑垎甯冨紡
- 涓柇/寮傚父/绯荤粺璋冪敤
- 鍐呮牳鎬佷笌鐢ㄦ埛鎬?
## 绗?-3璁? 杩涚▼绠＄悊
- 杩涚▼姒傚康涓嶱CB
- 杩涚▼鐘舵€佽浆鎹㈠浘(5鐘舵€?7鐘舵€?
- 鍘熻鎿嶄綔: 鍒涘缓/鎾ら攢/闃诲/鍞ら啋
- 杩涚▼閫氫俊: 鍏变韩鍐呭瓨/娑堟伅闃熷垪/绠￠亾

## 绗?-5璁? 绾跨▼
- 绾跨▼寮曞叆鍔ㄦ満(涓轰粈涔堥渶瑕佹洿杞婚噺鐨勬墽琛屽崟鍏?
- 鐢ㄦ埛绾х嚎绋?vs 鍐呮牳绾х嚎绋?- 澶氱嚎绋嬫ā鍨? 1:1 / N:1 / M:N
- 绾跨▼姹?
## 绗?-8璁? CPU璋冨害
- 璋冨害灞傛: 浣滀笟璋冨害/涓骇璋冨害/浣庣骇璋冨害
- 璋冨害绠楁硶: FCFS/SJF/浼樺厛绾?RR/澶氱骇闃熷垪/MLFQ
- CFS(Linux)璋冨害鍘熺悊
- 瀹炴椂璋冨害: RMS/EDF

## 绗?-11璁? 杩涚▼鍚屾
- 涓寸晫鍖洪棶棰?Critical Section)
- Peterson绠楁硶/TSL鎸囦护
- 淇″彿閲?PV鎿嶄綔)
- 缁忓吀鍚屾闂: 鐢熶骇鑰呮秷璐硅€?璇昏€呭啓鑰?鍝插瀹跺氨椁?
## 绗?2-13璁? 姝婚攣
- 姝婚攣鐨勫洓涓繀瑕佹潯浠?- 璧勬簮鍒嗛厤鍥?- 姝婚攣棰勯槻/閬垮厤(閾惰瀹剁畻娉?/妫€娴嬩笌鎭㈠
- Linux姝婚攣妫€娴?lockdep)

## 绗?4-16璁? 鍐呭瓨绠＄悊鍩虹
- 杩炵画鍒嗛厤: 棣栨/鏈€浣?鏈€宸€傞厤
- 鍒嗛〉: 椤佃〃/蹇〃(TLB)/澶氱骇椤佃〃
- 鍒嗘涓庢椤靛紡
- 铏氭嫙鍐呭瓨姒傚康

## 绗?7-19璁? 铏氭嫙鍐呭瓨
- 鎸夐渶璋冮〉+缂洪〉涓柇
- 椤甸潰缃崲绠楁硶: FIFO/Optimal/LRU/Clock/鏀硅繘Clock
- Belady寮傚父
- 宸ヤ綔闆嗘ā鍨?鎶栧姩
- 鍐欐椂澶嶅埗(COW)

## 绗?0-22璁? 鏂囦欢绯荤粺
- 鏂囦欢姒傚康涓庡睘鎬?iNode)
- 鐩綍缁撴瀯(鏍戝舰/鏃犵幆鍥?
- 鏂囦欢鍒嗛厤: 杩炵画/閾炬帴(闅愬紡+鏄惧紡FAT)/绱㈠紩
- 绌洪棽绌洪棿绠＄悊: 浣嶅浘/閾捐〃/鎴愮粍閾炬帴娉?- ext4/XFS/Btrfs绠€浠?
## 绗?3-24璁? IO绯荤粺
- IO纭欢: 璁惧鎺у埗鍣?DMA
- 涓柇澶勭悊: 椤跺崐閮?搴曞崐閮?- IO澶氳矾澶嶇敤: select/poll/epoll
- 闃诲/闈為樆濉?寮傛IO
- io_uring鏂颁竴浠ｅ紓姝O

## 绗?5-26璁? 澶у閲忓瓨鍌?- 纾佺洏缁撴瀯涓庢€ц兘鍙傛暟(瀵婚亾/鏃嬭浆/浼犺緭)
- 纾佺洏璋冨害: FCFS/SSTF/SCAN/C-SCAN/LOOK
- RAID 0-6绛夌骇
- SSD涓嶧TL

## 绗?7-28璁? 淇濇姢涓庡畨鍏?- 淇濇姢鍩?璁块棶鐭╅樀
- 璁块棶鎺у埗鍒楄〃(ACL)
- Capability-based绯荤粺
- 璁よ瘉鏈哄埗

## 绗?9-30璁? 铏氭嫙鍖栦笌鎬荤粨
- Hypervisor Type-1 vs Type-2
- KVM/QEMU
- Cgroups + Namespaces 鈫?Docker
- 瀹瑰櫒 vs VM

---
*鏉ユ簮: Operating System Concepts 10th Ed. (Silberschatz), OSTEP (Arpaci-Dusseau)*
"""
})

RESOURCES.append({
    "title": "璁＄畻鏈虹綉缁滆绋嬪畬鏁磋浠跺ぇ绾?,
    "description": "璁＄畻鏈虹綉缁滆绋?5璁茬殑PPT璇句欢澶х翰锛岃鐩朤CP/IP浜斿眰鍗忚鏍堬紝姣忚鍖呭惈鍗忚鏍煎紡鍥捐В銆佺姸鎬佹満銆佽绠椾緥棰樺拰Wireshark瀹為獙鎸囧銆?,
    "course": "璁＄畻鏈虹綉缁?, "chapter": "璇剧▼缁艰堪", "difficulty": "BASIC",
    "type": "SLIDES",
    "tags": ["璁＄畻鏈虹綉缁?, "璇句欢", "TCP/IP", "鏁欏澶х翰"],
    "source_url": "https://www.rfc-editor.org/",
    "content": """# 璁＄畻鏈虹綉缁滆绋嬪畬鏁磋浠跺ぇ绾?
## 绗?-2璁? 璁＄畻鏈虹綉缁滄杩?- 缃戠粶瀹氫箟涓庡垎绫?LAN/MAN/WAN)
- 浜ゆ崲鎶€鏈? 鐢佃矾浜ゆ崲/鎶ユ枃浜ゆ崲/鍒嗙粍浜ゆ崲
- 鏃跺欢鍒嗘瀽: 澶勭悊/鎺掗槦/浼犺緭/浼犳挱
- OSI涓冨眰妯″瀷 vs TCP/IP鍥涘眰妯″瀷

## 绗?-4璁? 搴旂敤灞?- 缃戠粶搴旂敤妯″瀷: C/S vs P2P
- HTTP/1.1鈫?鈫?婕旇繘
- HTTPS涓嶵LS 1.3
- DNS瑙ｆ瀽鍏ㄨ繃绋?
## 绗?-6璁? 浼犺緭灞?TCP
- TCP澶撮儴鏍煎紡(20+閫夐」瀛楄妭)
- 涓夋鎻℃墜/鍥涙鎸ユ墜
- 鍙潬浼犺緭: 鍋滅瓑鈫扜BN鈫扴R
- 娴侀噺鎺у埗(婊戝姩绐楀彛)

## 绗?-8璁? 浼犺緭灞?鎷ュ鎺у埗
- 鎷ュ鎺у埗: Tahoe鈫扲eno鈫扖UBIC鈫払BR
- TCP鐘舵€佹満(11绉嶇姸鎬?
- TCP瀹氭椂鍣? 閲嶄紶/鍧氭寔/淇濇椿
- UDP涓嶲UIC鍗忚

## 绗?-10璁? 缃戠粶灞?IPv4
- IPv4澶撮儴鏍煎紡
- IP鍒嗙墖涓庨噸缁?- 瀛愮綉鍒掑垎涓嶤IDR
- NAT/NAPT

## 绗?1-12璁? 缃戠粶灞?璺敱
- 璺敱绠楁硶鍒嗙被: 闈欐€?鍔ㄦ€? 鍏ㄥ眬/鍒嗗竷寮?- RIP(璺濈鍚戦噺)鍘熺悊涓庣己闄?- OSPF(閾捐矾鐘舵€?鍖哄煙鍒掑垎
- BGP(璺緞鍚戦噺)閫夎矾绛栫暐

## 绗?3-14璁? 缃戠粶灞?IPv6涓庡鎾?- IPv6澶撮儴涓庡湴鍧€鍒嗙被
- IPv4鈫扞Pv6杩囨浮鎶€鏈? 鍙屾爤/闅ч亾/缈昏瘧
- IGMP澶氭挱缁勭鐞?- 澶氭挱璺敱: PIM-SM/DM

## 绗?5-16璁? 鏁版嵁閾捐矾灞?- 鎴愬抚/宸敊妫€娴?CRC)
- 娴侀噺鎺у埗: 鍋滅瓑/婊戝姩绐楀彛
- 浠ュお缃戝抚鏍煎紡
- CSMA/CD

## 绗?7-18璁? 閾捐矾灞傞珮绾т富棰?- 浜ゆ崲鏈哄伐浣滃師鐞?鑷涔?MAC琛?
- VLAN(802.1Q)
- STP鐢熸垚鏍戝崗璁?- PPP/HDLC

## 绗?9-20璁? 鐗╃悊灞?- 浼犺緭浠嬭川: 鍙岀粸绾?鍏夌氦/鍚岃酱/鏃犵嚎
- 鏁板瓧缂栫爜: NRZ/鏇煎交鏂壒/宸垎鏇煎交鏂壒
- 澶嶇敤鎶€鏈? FDM/TDM/WDM/CDM
- 甯﹀涓庝俊閬撳閲?棣欏啘瀹氱悊)

## 绗?1-22璁? 鏃犵嚎涓庣Щ鍔ㄧ綉缁?- 802.11(WiFi) MAC瀛愬眰(CSMA/CA)
- 钃濈墮/鐗╄仈缃?- 绉诲姩IP: 褰掑睘浠ｇ悊+澶栭儴浠ｇ悊
- 5G缃戠粶鏋舵瀯绠€浠?
## 绗?3-24璁? 缃戠粶瀹夊叏
- 瀵嗙爜瀛﹀熀纭€: 瀵圭О/闈炲绉?鍝堝笇
- TLS鎻℃墜杩囩▼
- 闃茬伀澧?IDS/IPS
- Web瀹夊叏: XSS/CSRF/SQL娉ㄥ叆闃插尽

## 绗?5璁? 鍓嶆部涓撻
- SDN(杞欢瀹氫箟缃戠粶)
- NFV(缃戠粶鍔熻兘铏氭嫙鍖?
- QUIC涓嶩TTP/3
- 杈圭紭璁＄畻/CDN

---
*鏉ユ簮: Computer Networking: A Top-Down Approach (Kurose & Ross) 8th Ed.*
"""
})

print(f"Defined {len(RESOURCES)} diverse resources (QUIZ/PRACTICE/CODE/SLIDES)")

# 鈹€鈹€ Import pipeline (same as import_extra_resources.py) 鈹€鈹€鈹€鈹€鈹€鈹€
def connect_db():
    return psycopg2.connect(**DB_CONFIG)

def connect_minio():
    return Minio(MINIO_CONFIG["endpoint"], access_key=MINIO_CONFIG["access_key"],
                 secret_key=MINIO_CONFIG["secret_key"], secure=MINIO_CONFIG["secure"])

def ensure_bucket(client, bucket):
    if not client.bucket_exists(bucket):
        client.make_bucket(bucket)

def upload_resource_file(client, bucket, resource):
    safe_name = resource["title"].replace("/", "-").replace(" ", "_")
    object_key = f"resources/{safe_name}.md"
    content_bytes = resource["content"].encode("utf-8")
    data = BytesIO(content_bytes)
    client.put_object(bucket, object_key, data, len(content_bytes), content_type="text/markdown")
    return object_key, len(content_bytes)

def generate_embeddings(texts, dimension=RUNTIME_CONFIG.embedding_dimension):
    input_data = [{"text": t} for t in texts]
    resp = MultiModalEmbedding.call(model=RUNTIME_CONFIG.embedding_model_name, input=input_data,
                                     dimension=dimension, output_type="dense")
    if resp.status_code != 200:
        raise RuntimeError(f"API error: {resp.code} {resp.message}")
    emb_list = resp.output.get("embeddings", [])
    emb_list.sort(key=lambda x: x.get("index", 0))
    return [e["embedding"] for e in emb_list]

def build_embedding_str(vec):
    return "[" + ",".join(str(v) for v in vec) + "]"

def main():
    dry_run = "--dry-run" in sys.argv
    print("=" * 60)
    print(f"Batch 3: {len(RESOURCES)} Diverse Resources -> MinIO + PostgreSQL")
    print("=" * 60)

    if dry_run:
        for r in RESOURCES:
            print(f"  [{r['type']:8s}] {r['title']}")
        return

    minio = connect_minio()
    ensure_bucket(minio, BUCKET)
    conn = connect_db()

    try:
        with conn:
            with conn.cursor() as cur:
                # MinIO upload
                object_ids = {}
                for i, r in enumerate(RESOURCES):
                    object_key, size_bytes = upload_resource_file(minio, BUCKET, r)
                    obj_id = str(uuid.uuid4())
                    cur.execute("""
                        INSERT INTO storage.resource_object (id, provider, bucket_name, object_key,
                            file_name, mime_type, size_bytes, access_mode, storage_url)
                        VALUES (%s, 'RUSTFS', %s, %s, %s, 'text/markdown', %s, 'PRESIGNED', %s)
                    """, (obj_id, BUCKET, object_key,
                          f"{r['title'].replace('/', '-')}.md", size_bytes,
                          f"minio://{BUCKET}/{object_key}"))
                    object_ids[r["title"]] = obj_id
                    if (i + 1) % 10 == 0:
                        print(f"  MinIO upload [{i + 1}/{len(RESOURCES)}]")
                print(f"  Uploaded {len(RESOURCES)} objects to MinIO")

                # learning_resource
                resource_ids = {}
                for r in RESOURCES:
                    lr_id = str(uuid.uuid4())
                    cur.execute("""
                        INSERT INTO app.learning_resource (id, title, domain, resource_type,
                            difficulty_level, source_kind, access_scope, summary_text, tags,
                            metadata_json, storage_object_id, status)
                        VALUES (%s, %s, 'COMPUTER_SCIENCE', %s::app.resource_type,
                            %s::app.difficulty_level, 'IMPORTED'::app.source_kind,
                            'GLOBAL'::app.access_scope, %s, %s, %s, %s, 'ACTIVE')
                    """, (lr_id, r["title"], r["type"], r["difficulty"], r["description"],
                          json.dumps(r["tags"], ensure_ascii=False),
                          json.dumps({"course": r["course"], "chapter": r["chapter"],
                                      "source_url": r["source_url"]}, ensure_ascii=False),
                          object_ids.get(r["title"])))
                    resource_ids[r["title"]] = lr_id
                print(f"  Created {len(RESOURCES)} learning_resource entries")

                # resource_document
                resource_doc_ids = {}
                for r in RESOURCES:
                    rd_id = str(uuid.uuid4())
                    cur.execute("""
                        INSERT INTO rag.resource_document (id, resource_id, title, domain,
                            resource_type, difficulty_level, source_kind, source_ref,
                            summary_text, access_scope, metadata_json)
                        VALUES (%s, %s, %s, 'COMPUTER_SCIENCE', %s::app.resource_type,
                            %s::app.difficulty_level, 'IMPORTED'::app.source_kind, %s, %s,
                            'GLOBAL'::app.access_scope, %s)
                    """, (rd_id, resource_ids[r["title"]], r["title"],
                          r["type"], r["difficulty"], r["source_url"], r["description"],
                          json.dumps({"course": r["course"], "chapter": r["chapter"],
                                      "object_key": f"resources/{r['title'].replace('/', '-').replace(' ', '_')}.md"},
                                     ensure_ascii=False)))
                    resource_doc_ids[r["title"]] = rd_id
                print(f"  Created {len(RESOURCES)} resource_document entries")

                # Vectorize
                DIMENSION, BATCH_SIZE = RUNTIME_CONFIG.embedding_dimension, 5
                descriptions = [r["description"] for r in RESOURCES]
                failed = 0
                for bs in range(0, len(RESOURCES), BATCH_SIZE):
                    batch = RESOURCES[bs:bs + BATCH_SIZE]
                    batch_descs = descriptions[bs:bs + BATCH_SIZE]
                    try:
                        embeddings = generate_embeddings(batch_descs, DIMENSION)
                    except Exception as e:
                        print(f"  Batch [{bs+1}] err: {e}, retry individually...")
                        embeddings = []
                        for desc in batch_descs:
                            try:
                                emb = generate_embeddings([desc], DIMENSION)
                                embeddings.extend(emb)
                            except Exception:
                                embeddings.append(None); failed += 1
                            time.sleep(0.5)
                    for j, r in enumerate(batch):
                        emb_vec = embeddings[j] if j < len(embeddings) and embeddings[j] is not None else None
                        if emb_vec is None: continue
                        cur.execute("""
                            INSERT INTO rag.resource_chunk (document_id, resource_id, chunk_no,
                                content, embedding, token_count, domain, resource_type,
                                difficulty_level, access_scope, quality_score, metadata_json)
                            VALUES (%s, %s, 1, %s, %s, %s, 'COMPUTER_SCIENCE',
                                %s::app.resource_type, %s::app.difficulty_level,
                                'GLOBAL'::app.access_scope, 0.90, %s)
                        """, (resource_doc_ids[r["title"]], resource_ids[r["title"]],
                              r["description"], build_embedding_str(emb_vec),
                              int(len(r["description"]) / 1.5), r["type"], r["difficulty"],
                              json.dumps({"course": r["course"], "chapter": r["chapter"]}, ensure_ascii=False)))
                    print(f"  Vectorized [{min(bs+BATCH_SIZE, len(RESOURCES))}/{len(RESOURCES)}]")
                    time.sleep(0.3)

        if failed > 0: print(f"\\nWarning: {failed} embeddings failed")
        print(f"\\nDone. {len(RESOURCES)} diverse resources imported.")
    finally:
        conn.close()

if __name__ == "__main__":
    main()

