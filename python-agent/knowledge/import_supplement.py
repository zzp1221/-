"""
Quick supplement: add ~20 resources to bring total past 100.
Focus on underrepresented types: QUIZ, PRACTICE, CODE, SLIDES.
"""
import sys, os, uuid, json, hashlib, time
from io import BytesIO
import psycopg2
from minio import Minio
from dashscope import MultiModalEmbedding
from settings_helper import configure_dashscope_api_key

RUNTIME_CONFIG = configure_dashscope_api_key()


DB_CONFIG = RUNTIME_CONFIG.postgres.model_dump()
MINIO_CONFIG = RUNTIME_CONFIG.minio.model_dump(exclude={"bucket"})
BUCKET = RUNTIME_CONFIG.minio.bucket

RESOURCES = []

# 鈹€鈹€ 5 more QUIZ 鈹€鈹€
RESOURCES.append({
    "title":"缂栬瘧鍘熺悊-璇硶鍒嗘瀽棰樺簱",
    "description":"缂栬瘧鍘熺悊璇硶鍒嗘瀽缁忓吀涔犻20閬擄紝娑电洊LL(1)棰勬祴鍒嗘瀽琛ㄦ瀯閫犮€丩R(0)/SLR(1)/LR(1)/LALR(1)椤圭洰闆嗘棌鏋勯€犮€丗irst/Follow闆嗚绠楃瓑鏍稿績鑰冪偣锛岄檮璇︾粏鎺ㄥ杩囩▼銆?,
    "course":"缂栬瘧鍘熺悊","chapter":"璇硶鍒嗘瀽","difficulty":"ADVANCED","type":"QUIZ",
    "tags":["缂栬瘧鍘熺悊","璇硶鍒嗘瀽","LL(1)","LR(1)","棰樺簱"],
    "source_url":"https://en.wikipedia.org/wiki/LL_parser",
    "content":"# 缂栬瘧鍘熺悊-璇硶鍒嗘瀽棰樺簱\n\n## 棰?. 娑堥櫎宸﹂€掑綊\n鏂囨硶G: E鈫扙+T|T, T鈫扵*F|F, F鈫?E)|id銆傛秷闄ゅ乏閫掑綊骞舵瀯閫燣L(1)棰勬祴鍒嗘瀽琛ㄣ€俓n\n**瑙ｇ瓟**: E鈫扵E', E'鈫?TE'|蔚, T鈫扚T', T'鈫?FT'|蔚, F鈫?E)|id\n\n## 棰?. First/Follow闆哱n瀵逛笂杩版枃娉曡绠桭irst鍜孎ollow闆嗐€俓n- First(E)=First(T)=First(F)={(,id}\n- First(E')={+,蔚}, First(T')={*,蔚}\n- Follow(E)=Follow(E')={$,)}\n- Follow(T)=Follow(T')={+,$,)}\n- Follow(F)={+,*,$,)}\n\n## 棰?. LL(1)棰勬祴鍒嗘瀽琛╘n瀵规秷闄ゅ乏閫掑綊鍚庣殑E鈫扵E' E'鈫?TE'|蔚 T鈫扚T' T'鈫?FT'|蔚 F鈫?E)|id鏋勯€燣L(1)鍒嗘瀽琛紝楠岃瘉鏄惁涓篖L(1)鏂囨硶銆俓n\n## 棰?. LR(0)椤圭洰闆嗚鑼冩棌\n瀵筍鈫抋A|bB, A鈫抍A|d, B鈫抍B|d锛屾瀯閫燣R(0)椤圭洰闆嗚鑼冩棌鍜孌FA銆俓n\n## 棰?. SLR(1)鍒嗘瀽琛╘n瀵笶鈫扙+T|T, T鈫扵*F|F, F鈫?E)|id鏋勯€燬LR(1)鍒嗘瀽琛ㄣ€備笌LR(0)瀵规瘮锛孲LR(1)瑙ｅ喅浜嗗摢浜涚Щ杩?褰掔害鍐茬獊锛焅n\n## 棰?-20 瑕佺偣閫熸煡\n\n| # | 棰樼洰 | 鍏抽敭鐐?|\n|---|------|--------|\n| 6 | LR(1) vs LALR(1) | LALR鍚堝苟鍚屽績椤圭洰闆?|\n| 7 | 浜屼箟鎬ф枃娉曞鐞?| 浼樺厛绾?缁撳悎鎬у０鏄?|\n| 8 | 鎮┖else闂 | if-then-else鐨勪簩涔夋€?|\n| 9 | 绠楃浼樺厛鏂囨硶 | 浼樺厛鍏崇郴琛ㄦ瀯閫?|\n| 10 | 璇硶鍒跺缈昏瘧 | SDD缁煎悎灞炴€s缁ф壙灞炴€?|\n| 11 | 渚濊禆鍥句笌姹傚€奸『搴?| 鎷撴墤鎺掑簭 |\n| 12 | S灞炴€у畾涔?| 浠呯患鍚堝睘鎬р啋鑷簳鍚戜笂 |\n| 13 | L灞炴€у畾涔?| 鍙嚜椤跺悜涓嬬炕璇?|\n| 14 | 缈昏瘧鏂规 | 璇箟鍔ㄤ綔宓屽叆浜х敓寮忓彸閮?|\n| 15 | 涓棿浠ｇ爜鐢熸垚 | 涓夊湴鍧€鐮?鍥涘厓寮?|\n| 16 | 鍥炲～鎶€鏈?| 甯冨皵琛ㄨ揪寮忕煭璺眰鍊?|\n| 17 | 绗﹀彿琛ㄨ璁?| 鏁ｅ垪琛?浣滅敤鍩熸爤 |\n| 18 | 绫诲瀷琛ㄨ揪寮?| 绫诲瀷绛変环(鍚嶇瓑浠穠s缁撴瀯绛変环) |\n| 19 | 鍙傛暟浼犻€?| 浼犲€?浼犲紩鐢?浼犲€?缁撴灉/浼犲悕 |\n| 20 | Yacc/Bison瀹炴垬 | .y鏂囦欢鈫扖浠ｇ爜鈫掕娉曞垎鏋愬櫒 |\n\n---\n*鏉ユ簮: Dragon Book (Compilers: Principles, Techniques, and Tools)*"
})

RESOURCES.append({
    "title":"璁＄畻鏈虹粍鎴愬師鐞?鎸囦护娴佹按绾夸笌鍐掗櫓棰樺簱",
    "description":"CPU娴佹按绾胯璁′範棰?5閬擄紝娑电洊浜旂骇娴佹按绾?IF/ID/EX/MEM/WB)銆佹暟鎹啋闄?鍓嶆帹/鏃佽矾)銆佹帶鍒跺啋闄?鍒嗘敮棰勬祴)銆佺粨鏋勫啋闄╃殑妫€娴嬩笌瑙ｅ喅锛岄檮娴佹按绾挎椂绌哄浘涓庢椂搴忓垎鏋愩€?,
    "course":"璁＄畻鏈虹粍鎴愬師鐞?,"chapter":"CPU娴佹按绾?,"difficulty":"ADVANCED","type":"QUIZ",
    "tags":["璁＄畻鏈虹粍鎴愬師鐞?,"娴佹按绾?,"鍐掗櫓","CPU","棰樺簱"],
    "source_url":"https://en.wikipedia.org/wiki/Instruction_pipelining",
    "content":"# 璁＄畻鏈虹粍鎴愬師鐞?鎸囦护娴佹按绾垮啋闄╅搴揬n\n## 棰?. 娴佹按绾垮姞閫熸瘮\n鏌?绾ф祦姘寸嚎CPU锛屽悇绾ц€楁椂(IF:200ps, ID:150ps, EX:200ps, MEM:250ps, WB:100ps)銆傛祦姘寸嚎瀵勫瓨鍣ㄥ欢杩?0ps銆傛眰锛?1)闈炴祦姘寸嚎鎵ц鏃堕棿 (2)娴佹按绾垮懆鏈?(3)鐞嗘兂鍔犻€熸瘮銆俓n**瑙?*: 闈炴祦姘寸嚎=900ps, 鍛ㄦ湡=max(200,150,200,250,100)+20=270ps, 鐞嗘兂鍔犻€熸瘮=900/270=3.33\n\n## 棰?. 鏁版嵁鍐掗櫓妫€娴媆n```asm\nadd x1, x2, x3\nsub x4, x1, x5    ; RAW: x1鍦╝dd鐨刉B鍓嶈sub鐨処D闇€瑕乗nand x6, x1, x7    ; RAW: x1\nor  x8, x2, x9    ; 鏃犲啋闄‐n```\n鍓嶆帹(forwarding)鍙В鍐冲摢鏉℃寚浠ょ殑鍐掗櫓锛焅n\n## 棰?. 鍓嶆帹璺緞璁捐\nEX/MEM鈫扐LU杈撳叆銆丮EM/WB鈫扐LU杈撳叆涓ゆ潯鍓嶆帹璺緞鍚勮嚜瑙ｅ喅鍝RAW鍐掗櫓锛熶綍鏃堕渶瑕佹彃鍏ユ皵娉?stall)锛焅n\n## 棰?. 鍒嗘敮棰勬祴\n5绾ф祦姘寸嚎涓垎鏀寚浠ゅ湪EX闃舵鎵嶇‘瀹氭槸鍚﹁烦杞紝闇€鍐插埛2鏉℃寚浠ゃ€傝嫢鍒嗘敮棰戠巼20%銆侀娴嬪噯纭巼85%銆佽棰勬祴鎯╃綒2鍛ㄦ湡锛屾眰CPI澧炲姞閲忋€俓n**瑙?*: CPI澧炲姞 = 0.20 * (1-0.85) * 2 = 0.06\n\n## 棰?-15 閫熸煡\n| # | 棰樼洰 | 鍏抽敭鐐?|\n|---|------|--------|\n| 5 | 缁撴瀯鍐掗櫓 | 鍗曞瓨鍌ㄥ櫒鍚屾椂鍙栨寚+璁垮瓨鍐茬獊 |\n| 6 | 1浣?2浣嶅垎鏀娴嬪櫒 | 2浣嶉ケ鍜岃鏁板櫒 |\n| 7 | 鐩稿叧棰勬祴鍣?| (鍏ㄥ眬+灞€閮?缁勫悎) |\n| 8 | 寰幆灞曞紑 | 缂栬瘧鍣ㄥ噺灏戝垎鏀殑鎶€鏈?|\n| 9 | 瓒呮爣閲?| 澶氬彂灏?澶氭墽琛屽崟鍏?|\n| 10 | 鍔ㄦ€佽皟搴?| Tomasulo绠楁硶 |\n| 11 | 涔卞簭鎵ц | 淇濈暀绔?閲嶆帓搴忕紦鍐睷OB |\n| 12 | 瀵勫瓨鍣ㄩ噸鍛藉悕 | 娑堥櫎WAR/WAW鍋囩浉鍏?|\n| 13 | VLIW | 缂栬瘧鍣ㄩ潤鎬佽皟搴s纭欢鍔ㄦ€?|\n| 14 | SIMD | 鍚戦噺澶勭悊 vs 鏍囬噺 |\n| 15 | 澶氭牳Cache涓€鑷存€?| MESI鍗忚 |\n\n---\n*鏉ユ簮: Computer Organization and Design (Patterson & Hennessy)*"
})

RESOURCES.append({
    "title":"杞欢宸ョ▼-杞欢鏋舵瀯涓庤璁℃ā寮忛搴?,
    "description":"杞欢鏋舵瀯涓庤璁℃ā寮忎範棰?0閬擄紝娑电洊MVC/MVP/MVVM銆丼OLID鍘熷垯銆丟oF 23绉嶆ā寮忓垎绫汇€佹灦鏋勯鏍?鍒嗗眰/寰湇鍔?浜嬩欢椹卞姩)绛夋牳蹇冭€冪偣锛岄檮绫诲浘鍜屼唬鐮佺ず渚嬨€?,
    "course":"杞欢宸ョ▼","chapter":"杞欢璁捐","difficulty":"INTERMEDIATE","type":"QUIZ",
    "tags":["杞欢宸ョ▼","璁捐妯″紡","鏋舵瀯","SOLID","棰樺簱"],
    "source_url":"https://refactoring.guru/design-patterns",
    "content":"# 杞欢宸ョ▼-杞欢鏋舵瀯涓庤璁℃ā寮忛搴揬n\n## 棰?. SOLID鍘熷垯\n绠€杩伴潰鍚戝璞¤璁＄殑SOLID浜斿師鍒欍€俓n- S-SRP鍗曚竴鑱岃矗銆丱-OCP寮€闂師鍒欍€丩-LSP閲屾皬鏇挎崲銆両-ISP鎺ュ彛闅旂銆丏-DIP渚濊禆鍊掔疆\n\n## 棰?. 绛栫暐妯″紡 vs 鐘舵€佹ā寮廫n涓ょ被妯″紡绫诲浘鐩稿悓锛屾剰鍥炬湁浣曚笉鍚岋紵\n- 绛栫暐: 瀹㈡埛绔富鍔ㄩ€夋嫨绠楁硶锛岀瓥鐣ラ棿閫氬父鏃犵姸鎬佽浆鎹n- 鐘舵€? 瀵硅薄琛屼负闅忓唴閮ㄧ姸鎬佹敼鍙樿€屾敼鍙橈紝鐘舵€侀棿鏈夎浆鎹㈠叧绯籠n\n## 棰?. 瑙傚療鑰呮ā寮廫n鐢诲嚭瑙傚療鑰呮ā寮忕被鍥俱€傛帹(Push)妯″瀷涓庢媺(Pull)妯″瀷鍖哄埆锛焅n\n## 棰?-20 閫熸煡\n| # | 棰樼洰 | 鍏抽敭鐐?|\n|---|------|--------|\n| 4 | 鍗曚緥绾跨▼瀹夊叏 | 鍙岄噸妫€鏌ラ攣瀹?DCL+volatile |\n| 5 | 宸ュ巶鏂规硶 vs 鎶借薄宸ュ巶 | 鍗曚骇鍝佺瓑绾s浜у搧鏃?|\n| 6 | 閫傞厤鍣?vs 瑁呴グ鍣?| 鎺ュ彛杞崲vs鍔熻兘澧炲己 |\n| 7 | 浠ｇ悊 vs 瑁呴グ鍣?| 璁块棶鎺у埗vs鍔ㄦ€佸寮?|\n| 8 | MVC/MVP/MVVM | Controller/Presenter/ViewModel |\n| 9 | 鍒嗗眰鏋舵瀯 | Presentation鈫払usiness鈫扨ersistence鈫扗atabase |\n| 10 | 鍏竟褰㈡灦鏋?| 绔彛-閫傞厤鍣紝棰嗗煙鏍稿績鏃犲閮ㄤ緷璧?|\n| 11 | 寰湇鍔℃灦鏋?| 鐙珛閮ㄧ讲/鍘讳腑蹇冨寲娌荤悊/鏁版嵁鍒嗘不 |\n| 12 | 浜嬩欢椹卞姩鏋舵瀯 | 鍙戝竷-璁㈤槄/浜嬩欢婧簮/CQRS |\n| 13 | DDD鑱氬悎璁捐 | 涓嶅彉寮忎繚鎶?閫氳繃ID寮曠敤 |\n| 14 | 璐妯″瀷 vs 鍏呰妯″瀷 | 鏁版嵁+琛屼负鍒嗙vs鍚堜竴 |\n| 15 | 渚濊禆娉ㄥ叆(DI) | 鎺у埗鍙嶈浆IoC瀹瑰櫒 |\n| 16 | 鍗曚竴鑱岃矗鍘熷垯 | 涓€涓被鍙湁涓€涓彉鍖栫殑鍘熷洜 |\n| 17 | 寮€闂師鍒?| 瀵规墿灞曞紑鏀? 瀵逛慨鏀瑰叧闂?|\n| 18 | 閲屾皬鏇挎崲 | 瀛愮被鍙浛鎹㈠熀绫讳笉鐮村潖姝ｇ‘鎬?|\n| 19 | 杩背鐗规硶鍒?| 鏈€灏戠煡璇嗗師鍒?鍙笌鏈嬪弸閫氫俊) |\n| 20 | 鎺ュ彛闅旂 | 涓嶅己杩緷璧栦笉闇€瑕佺殑鎺ュ彛 |\n\n---\n*鏉ユ簮: Design Patterns (GoF), Clean Architecture (Martin), Refactoring.Guru*"
})

RESOURCES.append({
    "title":"绋嬪簭璁捐-Python甯歌闄烽槺涓庢渶浣冲疄璺甸搴?,
    "description":"Python缂栫▼甯歌闄烽槺涔犻闆?5閬擄紝娑电洊鍙彉榛樿鍙傛暟銆侀棴鍖呭欢杩熺粦瀹氥€佹祬鎷疯礉涓庢繁鎷疯礉銆丟IL涓庡绾跨▼銆乮s vs ==銆佺户鎵縮uper()绛夐珮棰戞槗閿欑偣锛岄檮瑙ｉ噴鍜屼慨姝ｄ唬鐮併€?,
    "course":"绋嬪簭璁捐","chapter":"Python杩涢樁","difficulty":"INTERMEDIATE","type":"QUIZ",
    "tags":["Python","闄烽槺","鏈€浣冲疄璺?,"棰樺簱"],
    "source_url":"https://docs.python-guide.org/",
    "content":"# 绋嬪簭璁捐-Python甯歌闄烽槺棰樺簱\n\n## 棰?. 鍙彉榛樿鍙傛暟\n```python\ndef add_item(item, items=[]):\n    items.append(item)\n    return items\nprint(add_item(1))  # [1]\nprint(add_item(2))  # [1, 2] 鈫?涓嶆槸棰勬湡鐨刐2]!\n```\n**瑙ｉ噴**: 榛樿鍙傛暟鍦ㄥ嚱鏁板畾涔夋椂鍒涘缓涓€娆★紝澶氭璋冪敤鍏变韩鍚屼竴鍒楄〃瀵硅薄銆俓n**淇**: `def add_item(item, items=None): items = items or []`\n\n## 棰?. 闂寘寤惰繜缁戝畾\n```python\nfuncs = [lambda x: x + i for i in range(5)]\nprint([f(0) for f in funcs])  # [4,4,4,4,4] 鈫?涓嶆槸[0,1,2,3,4]!\n```\n**瑙ｉ噴**: lambda涓殑i鏄紩鐢紝鍦ㄨ皟鐢ㄦ椂鎵嶅彇鍊硷紝姝ゆ椂i=4銆俓n**淇**: `lambda x, i=i: x + i` (榛樿鍙傛暟鍦ㄥ畾涔夋椂缁戝畾)\n\n## 棰?. 娴呮嫹璐濅笌娣辨嫹璐漒n```python\nimport copy\na = [[1,2],[3,4]]\nb = a.copy()        # 娴呮嫹璐漒nc = copy.deepcopy(a) # 娣辨嫹璐漒na[0][0] = 99\nprint(b[0][0])  # 99 鈫?b鍏变韩鍐呴儴鍒楄〃\nprint(c[0][0])  # 1  鈫?c瀹屽叏鐙珛\n```\n\n## 棰?. is vs ==\n```python\na = 256; b = 256; print(a is b)  # True (灏忔暣鏁扮紦瀛?5鍒?56)\na = 257; b = 257; print(a is b)  # False (鍙兘! 鍙栧喅浜庡疄鐜?\n# 姘歌繙鐢?=姣旇緝鍊肩浉绛夛紝is姣旇緝瀵硅薄韬唤\n```\n\n## 棰?. GIL\nCPU瀵嗛泦浠诲姟鐢ㄥ绾跨▼鍙嶈€屽彉鎱?鍥犱负GIL绔炰簤)銆侷O瀵嗛泦浠诲姟澶氱嚎绋嬪彲浠ユ彁鍗囨€ц兘銆侰PU瀵嗛泦鐢╩ultiprocessing銆俓n\n## 棰?-15 閫熸煡\n| # | 闄烽槺 | 瑙ｉ噴 |\n|---|------|------|\n| 6 | `del list[i]`閬嶅巻涓垹闄?| 鍊掑簭閬嶅巻鎴栧垪琛ㄦ帹瀵?|\n| 7 | 绫诲彉閲弙s瀹炰緥鍙橀噺 | 绫诲彉閲忚鎵€鏈夊疄渚嬪叡浜?|\n| 8 | `+=` 瀵逛笉鍙彉绫诲瀷 | a+=[4] vs a=a+[4] 琛屼负涓嶅悓 |\n| 9 | `try-except-else-finally` | else: 鏃犲紓甯告椂鎵ц |\n| 10 | 鐢熸垚鍣ㄥ彧鑳借凯浠ｄ竴娆?| 鑰楀敖鍚庤繑鍥炵┖ |\n| 11 | `re.match` vs `re.search` | match浠庡紑澶村尮閰? search浠绘剰浣嶇疆 |\n| 12 | 澶氱户鎵縈RO | C3绾挎€у寲/`__mro__` |\n| 13 | super()鍙傛暟 | Python 3鍙棤鍙俿uper() |\n| 14 | `__new__` vs `__init__` | new鍒涘缓瀵硅薄/init鍒濆鍖?|\n| 15 | decorator鎵ц鏃舵満 | 瑁呴グ鍣ㄥ湪妯″潡鍔犺浇鏃舵墽琛?|\n\n---\n*鏉ユ簮: Python瀹樻柟鏂囨。, Fluent Python, Effective Python*"
})

RESOURCES.append({
    "title":"鏁版嵁搴撳師鐞?浜嬪姟涓庨攣鏈哄埗棰樺簱",
    "description":"鏁版嵁搴撲簨鍔′笌閿佹満鍒朵範棰?0閬擄紝娑电洊ACID鐗规€с€侀殧绂荤骇鍒笌骞跺彂寮傚父銆丮VCC澶氱増鏈苟鍙戞帶鍒躲€?PL涓ら樁娈甸攣鍗忚銆佹閿佹娴嬩笌瑙ｅ喅绛夋牳蹇冭€冪偣銆?,
    "course":"鏁版嵁搴撳師鐞?,"chapter":"浜嬪姟绠＄悊","difficulty":"ADVANCED","type":"QUIZ",
    "tags":["鏁版嵁搴?,"浜嬪姟","閿?,"MVCC","棰樺簱"],
    "source_url":"https://www.postgresql.org/docs/current/mvcc.html",
    "content":"# 鏁版嵁搴撳師鐞?浜嬪姟涓庨攣鏈哄埗棰樺簱\n\n## 棰?. ACID\n瑙ｉ噴浜嬪姟鐨凙CID鐗规€у苟璇存槑瀹炵幇鏈哄埗銆俓n- A(鍘熷瓙鎬?: undo log鍥炴粴\n- C(涓€鑷存€?: 绾︽潫妫€鏌?瑙﹀彂鍣╘n- I(闅旂鎬?: MVCC+閿乗n- D(鎸佷箙鎬?: redo log+WAL\n\n## 棰?. 闅旂绾у埆涓庡苟鍙戝紓甯竆n| 绾у埆 | 鑴忚 | 涓嶅彲閲嶅璇?| 骞昏 |\n|------|------|-----------|------|\n| Read Uncommitted | 鍙兘 | 鍙兘 | 鍙兘 |\n| Read Committed | 鍚?| 鍙兘 | 鍙兘 |\n| Repeatable Read | 鍚?| 鍚?| 鍙兘(MySQL鍚? |\n| Serializable | 鍚?| 鍚?| 鍚?|\n\n## 棰?. MVCC ReadView\nRR绾у埆鍦ㄦ瘡涓簨鍔＄涓€娆″揩鐓ц鏃剁敓鎴怰eadView锛孯C绾у埆姣忔蹇収璇婚兘鐢熸垚鏂癛eadView銆俓n\n## 棰?-20 閫熸煡\n| # | 棰樼洰 | 鍏抽敭鐐?|\n|---|------|--------|\n| 4 | 涓ら樁娈甸攣2PL | 鍔犻攣鈫掕В閿侊紝涓嶄氦鍙?|\n| 5 | 姝婚攣妫€娴?| wait-for鍥?瓒呮椂鍥炴粴 |\n| 6 | 鎰忓悜閿?IS/IX) | 澶氱矑搴﹀皝閿?|\n| 7 | 闂撮殭閿?Gap Lock) | 闃叉骞昏 |\n| 8 | 涓撮敭閿?Next-Key) | 璁板綍閿?闂撮殭閿?|\n| 9 | 涔愯閿丆AS | 鐗堟湰鍙?鏃堕棿鎴?|\n| 10 | 鎮茶閿丼ELECT FOR UPDATE | 琛岄攣 |\n| 11 | 鍏变韩閿乿s鎺掍粬閿?| S(璇?/X(鍐?鍏煎鐭╅樀 |\n| 12 | 閿佸崌绾?| 琛岄攣鈫掕〃閿?閿佹暟閲忛槇鍊? |\n| 13 | 姝婚攣棰勯槻 | 鎺掑簭鍔犻攣/涓€娆℃€у姞閿?|\n| 14 | WAL棰勫啓鏃ュ織 | Write-Ahead Logging |\n| 15 | Checkpoint | 缂╃煭鎭㈠鏃堕棿 |\n| 16 | ARIES鎭㈠绠楁硶 | 鍒嗘瀽鈫掗噸鍋氣啋鎾ら攢 |\n| 17 | 淇濆瓨鐐筍avepoint | 閮ㄥ垎鍥炴粴 |\n| 18 | XA鍒嗗竷寮忎簨鍔?| 2PC涓ら樁娈垫彁浜?|\n| 19 | Saga妯″紡 | 闀夸簨鍔℃媶鍒嗕负鐭簨鍔￠摼 |\n| 20 | TCC(Try-Confirm-Cancel) | 琛ュ伩浜嬪姟妯″紡 |\n\n---\n*鏉ユ簮: Database System Concepts (Silberschatz), MySQL/PostgreSQL瀹樻柟鏂囨。*"
})

# 鈹€鈹€ 5 more PRACTICE 鈹€鈹€
RESOURCES.append({
    "title":"瀹炴搷妗堜緥-Docker瀹瑰櫒鍖栭儴缃插畬鏁村疄璺?,
    "description":"浠嶥ockerfile缂栧啓鍒板瀹瑰櫒缂栨帓鐨勫畬鏁村疄鎿嶆寚鍗楋細闀滃儚鏋勫缓涓庝紭鍖?澶氶樁娈垫瀯寤?灞傜紦瀛?銆乨ocker-compose缂栨帓銆佺綉缁滀笌鍗风鐞嗐€佺敓浜х幆澧冩渶浣冲疄璺点€?,
    "course":"鎿嶄綔绯荤粺","chapter":"瀹瑰櫒瀹炶返","difficulty":"INTERMEDIATE","type":"PRACTICE",
    "tags":["Docker","瀹瑰櫒","docker-compose","瀹炴搷","閮ㄧ讲"],
    "source_url":"https://docs.docker.com/get-started/",
    "content":"# 瀹炴搷妗堜緥-Docker瀹瑰櫒鍖栭儴缃插畬鏁村疄璺礬n\n## 瀹為獙鐩爣\n灏嗕竴涓狿ython Web搴旂敤瀹瑰櫒鍖栧苟缂栨帓閮ㄧ讲銆俓n\n## 姝ラ1: Dockerfile\n```dockerfile\nFROM python:3.11-slim AS builder\nWORKDIR /app\nCOPY requirements.txt .\nRUN pip install --no-cache-dir -r requirements.txt\n\nFROM python:3.11-slim\nWORKDIR /app\nCOPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages\nCOPY . .\nEXPOSE 8000\nUSER nobody\nCMD [\\\"uvicorn\\\", \\\"app.main:app\\\", \\\"--host\\\", \\\"0.0.0.0\\\", \\\"--port\\\", \\\"8000\\\"]\n```\n澶氶樁娈垫瀯寤? builder瀹夎渚濊禆, 鏈€缁堥暅鍍忔嫹璐漵ite-packages銆傛渶缁堥暅鍍忓噺灏憕200MB銆俓n\n## 姝ラ2: docker-compose.yml\n```yaml\nservices:\n  web:\n    build: .\n    ports: [\\\"8000:8000\\\"]\n    environment:\n      DATABASE_URL: postgresql://user:pass@db:5432/app\n    depends_on: [db]\n    restart: unless-stopped\n  db:\n    image: postgres:16-alpine\n    environment:\n      POSTGRES_USER: user\n      POSTGRES_PASSWORD: pass\n      POSTGRES_DB: app\n    volumes: [pgdata:/var/lib/postgresql/data]\nvolumes:\n  pgdata:\n```\n\n## 姝ラ3: 鏋勫缓涓庤繍琛孿n```bash\ndocker compose build\ndocker compose up -d\ndocker compose logs -f web\ndocker compose ps\n```\n\n## 姝ラ4: 鐢熶骇妫€鏌ユ竻鍗昞n- [ ] 浣跨敤闈瀝oot鐢ㄦ埛杩愯 `USER nobody`\n- [ ] 澶氶樁娈垫瀯寤哄噺灏忛暅鍍廫n- [ ] .dockerignore鎺掗櫎venv/__pycache__/.git\n- [ ] 涓嶅皢secret纭紪鐮佸湪Dockerfile\n- [ ] 璁剧疆HEALTHCHECK\n- [ ] 闄愬埗璧勬簮 `deploy.resources.limits`\n\n---\n*鏉ユ簮: Docker瀹樻柟鏂囨。, Dockerfile鏈€浣冲疄璺垫寚鍗?"
})

RESOURCES.append({
    "title":"瀹炴搷妗堜緥-绯荤粺鎬ц兘鐩戞帶涓庢晠闅滄帓鏌?,
    "description":"Linux绯荤粺鎬ц兘鐩戞帶涓庢晠闅滄帓鏌ュ疄鎿嶏細CPU/鍐呭瓨/IO/缃戠粶鍥涘ぇ璧勬簮浣跨敤鍒嗘瀽锛宼op/htop/iostat/vmstat/netstat/perf绛夊伐鍏峰疄鎴橈紝瀹氫綅CPU椋欏崌/鍐呭瓨娉勬紡/纾佺洏IO鐡堕鐨勫畬鏁存帓鏌ユ祦绋嬨€?,
    "course":"鎿嶄綔绯荤粺","chapter":"鎬ц兘璋冧紭","difficulty":"ADVANCED","type":"PRACTICE",
    "tags":["Linux","鎬ц兘","鐩戞帶","鏁呴殰鎺掓煡","瀹炴搷"],
    "source_url":"https://www.brendangregg.com/linuxperf.html",
    "content":"# 瀹炴搷妗堜緥-绯荤粺鎬ц兘鐩戞帶涓庢晠闅滄帓鏌n\n## 瀹為獙鍦烘櫙\n妯℃嫙涓€涓敓浜х幆澧冧腑閫愭笎鍙樻參鐨刉eb鏈嶅姟锛岄€氳繃绯荤粺宸ュ叿瀹氫綅鏍瑰洜銆俓n\n## 鍦烘櫙1: CPU浣跨敤鐜?00%\n```bash\n# 鎸塁PU鎺掑簭杩涚▼\ntop -o %CPU\n# 鏌ョ湅鍏蜂綋杩涚▼鐨勭嚎绋媆nps -Lf <PID>\n# 鍝釜鍑芥暟鍗犵敤CPU锛堥噰鏍凤級\nperf top -p <PID>\n# 鎴栫敓鎴愮伀鐒板浘\nperf record -p <PID> -g -- sleep 30\nperf script | stackcollapse-perf.pl | flamegraph.pl > flame.svg\n```\n\n## 鍦烘櫙2: 鍐呭瓨娉勬紡\n```bash\n# 鏌ョ湅鍐呭瓨浣跨敤\nfree -h\n# 杩涚▼鍐呭瓨璇︽儏\npmap -x <PID>\n# 鎴?/proc/<PID>/smaps\n# 瑙傚療闅忔椂闂村闀縗nwatch -n 5 'ps -o pid,rss,vsz,cmd -p <PID>'\n# 鐢╲algrind妫€娴嬫硠婕?寮€鍙戠幆澧?\nvalgrind --leak-check=full --show-leak-kinds=all ./app\n```\n\n## 鍦烘櫙3: 纾佺洏IO鐡堕\n```bash\niostat -x 1  # %util鎺ヨ繎100%鈫掔鐩樼摱棰圽n# 鍝釜杩涚▼瀵艰嚧鐨処O\niotop -o\n# 杩借釜IO绯荤粺璋冪敤\nstrace -c -p <PID>  # 缁熻绯荤粺璋冪敤娆℃暟\n```\n\n## 鍦烘櫙4: 缃戠粶寤惰繜\n```bash\n# 杩炴帴鐘舵€佺粺璁nss -s\n# TIME_WAIT鍫嗙Н(>1000)\nss -tan state time-wait | wc -l\n# 鏌ョ湅缃戠粶鍚炲悙\nnload / iftop\n# TCP閲嶄紶缁熻\nnetstat -s | grep retransmit\n```\n\n## 绠€鏄撳帇鍔涙祴璇昞n```bash\n# CPU鍘嬪姏\nstress --cpu 4 --timeout 60s\n# 鍐呭瓨鍘嬪姏\nstress --vm 2 --vm-bytes 1G --timeout 60s\n# 鐩戞帶鍚屾椂杩愯\nvmstat 1 &\n```\n\n---\n*鏉ユ簮: Linux Performance (Brendan Gregg), Linux man-pages*"
})

RESOURCES.append({
    "title":"瀹炴搷妗堜緥-SQL娉ㄥ叆鏀诲嚮涓庨槻寰″疄楠?,
    "description":"Web瀹夊叏鍔ㄦ墜瀹為獙锛氬湪DVWA闈跺満鐜涓疄璺礢QL娉ㄥ叆鏀诲嚮涓庨槻寰★紝娑电洊鑱斿悎鏌ヨ娉ㄥ叆銆佸竷灏旂洸娉ㄣ€佹椂闂寸洸娉ㄣ€佸爢鍙犳敞鍏ワ紝浠ュ強鍙傛暟鍖栨煡璇€佽緭鍏ラ獙璇併€乄AF缁曡繃绛夐槻寰℃妧鏈€?,
    "course":"鏁版嵁搴撳師鐞?,"chapter":"鏁版嵁搴撳畨鍏?,"difficulty":"INTERMEDIATE","type":"PRACTICE",
    "tags":["SQL娉ㄥ叆","瀹夊叏","闃插尽","瀹炴搷","OWASP"],
    "source_url":"https://owasp.org/www-project-top-ten/",
    "content":"# 瀹炴搷妗堜緥-SQL娉ㄥ叆鏀诲嚮涓庨槻寰″疄楠孿n\n## 娉曞緥澹版槑\n鏈疄楠屼粎渚涘凡鑾锋巿鏉冪殑瀹夊叏娴嬭瘯鍜屾暀鑲茬洰鐨勪娇鐢ㄣ€俓n\n## 鐜鎼缓\n```bash\ndocker run -d -p 80:80 vulnerables/web-dvwa\n# 璁块棶 http://localhost/setup.php 鍒濆鍖朶n```\n\n## 鏀诲嚮1: 鑱斿悎鏌ヨ娉ㄥ叆\n```sql\n-- 姝ｅ父: SELECT * FROM users WHERE id='1'\n-- 娉ㄥ叆: 1' UNION SELECT user(),database(),version() -- \n```\n\n## 鏀诲嚮2: 甯冨皵鐩叉敞\n```sql\n-- 鍒ゆ柇鏁版嵁搴撳悕闀垮害\n1' AND LENGTH(database())=4 --   (杩斿洖姝ｅ父鈫掗暱搴︿负4)\n-- 閫愬瓧绗︾寽瑙ｆ暟鎹簱鍚峔n1' AND SUBSTRING(database(),1,1)='d' --\n```\n\n## 鏀诲嚮3: 鏃堕棿鐩叉敞\n```sql\n-- 鏃犲洖鏄炬椂鐢ㄦ椂闂村欢杩熷垽鏂璡n1' AND IF(SUBSTRING(database(),1,1)='d', SLEEP(5), 0) --\n```\n\n## 闃插尽1: 鍙傛暟鍖栨煡璇n```python\ncursor.execute(\"SELECT * FROM users WHERE id=%s\", (user_input,))\n```\n\n## 闃插尽2: 杈撳叆楠岃瘉+鏈€灏忔潈闄怽n- 鐧藉悕鍗曟牎楠? 鐢ㄦ埛ID鍙厑璁告暟瀛梊n- 鏁版嵁搴撶敤鎴锋渶灏忔潈闄? 搴旂敤璐︽埛鍙粰SELECT/INSERT/UPDATE/DELETE锛屼笉缁橠DL\n\n## 闃插尽3: ORM妗嗘灦\n浣跨敤SQLAlchemy绛塐RM鑷姩鍙傛暟鍖栨煡璇€備絾浠嶉渶娉ㄦ剰鍘熺敓SQL鐨勪娇鐢ㄣ€俓n\n---\n*鏉ユ簮: OWASP Testing Guide, PortSwigger Web Security Academy*"
})

RESOURCES.append({
    "title":"瀹炴搷妗堜緥-Python鐖櫕浠庨浂鍒颁竴瀹屾暣椤圭洰",
    "description":"鏋勫缓涓€涓畬鏁寸殑Python鐖櫕椤圭洰锛歳equests+BeautifulSoup闈欐€佺埇鍙栥€丼crapy妗嗘灦銆丼elenium鍔ㄦ€佹覆鏌撱€佸弽鐖鎶?User-Agent/浠ｇ悊IP/楠岃瘉鐮佽瘑鍒?銆佹暟鎹竻娲椾笌瀛樺偍銆?,
    "course":"绋嬪簭璁捐","chapter":"鐖櫕瀹炶返","difficulty":"INTERMEDIATE","type":"PRACTICE",
    "tags":["Python","鐖櫕","Scrapy","鏁版嵁閲囬泦","瀹炴搷"],
    "source_url":"https://docs.scrapy.org/en/latest/intro/tutorial.html",
    "content":"# 瀹炴搷妗堜緥-Python鐖櫕浠庨浂鍒颁竴瀹屾暣椤圭洰\n\n## 瀹為獙鐩爣\n鐖彇涔︾睄淇℃伅缃戠珯鐨勬暟鎹紝瀛樺偍鍒癈SV鍜屾暟鎹簱銆俓n\n## 闃舵1: 闈欐€佺埇鍙朶n```python\nimport requests\nfrom bs4 import BeautifulSoup\n\nurl = \"http://books.toscrape.com\"\nresp = requests.get(url, headers={\\\"User-Agent\\\": \\\"Mozilla/5.0\\\"})\nsoup = BeautifulSoup(resp.text, 'html.parser')\n\nbooks = []\nfor article in soup.select('article.product_pod'):\n    title = article.h3.a['title']\n    price = article.select_one('p.price_color').text\n    books.append({'title': title, 'price': price})\n```\n\n## 闃舵2: Scrapy妗嗘灦\n```bash\nscrapy startproject bookscraper\n# bookscraper/spiders/books.py\n```\nItem Pipeline: 娓呮礂浠锋牸瀛楃涓测啋瀛樺叆CSV/鏁版嵁搴撯啋鍘婚噸妫€鏌n\n## 闃舵3: 鍔ㄦ€佹覆鏌揬n```python\nfrom selenium import webdriver\nfrom selenium.webdriver.common.by import By\n\ndriver = webdriver.Chrome()\ndriver.get('https://example.com')\nelements = driver.find_elements(By.CSS_SELECTOR, '.item')\n```\n\n## 鍙嶇埇瀵规姉\n- User-Agent杞崲姹燶n- 寤惰繜(闅忔満sleep)\n- 浠ｇ悊IP姹燶n- Cookie绠＄悊\n- 楠岃瘉鐮? OCR(Tesseract)鎴栨墦鐮佸钩鍙癨n\n## 鍚堣瑕佹眰\n- 閬靛畧robots.txt\n- 涓嶇埇鍙栦釜浜轰俊鎭痋n- 涓嶇粫杩囦粯璐瑰\n- 棰戠巼鎺у埗涓嶈繃杞界洰鏍囨湇鍔″櫒\n\n---\n*鏉ユ簮: Scrapy瀹樻柟鏂囨。, Python requests鏂囨。*"
})

RESOURCES.append({
    "title":"瀹炴搷妗堜緥-绠楁硶鍙鍖栭」鐩疄璺?,
    "description":"鏋勫缓绠楁硶鍙鍖朩eb搴旂敤锛氫娇鐢≒ython+Tkinter鎴朒TML5 Canvas瀹炵幇鎺掑簭绠楁硶銆佽矾寰勬悳绱?BFS/DFS/Dijkstra/A*)銆侀€掑綊鍒嗗舰鐨勪氦浜掑紡鍙鍖栵紝鍚鑹茬紪鐮併€侀€熷害鎺у埗銆佹殏鍋?缁х画鍔熻兘銆?,
    "course":"绠楁硶璁捐涓庡垎鏋?,"chapter":"绠楁硶鍙鍖?,"difficulty":"INTERMEDIATE","type":"PRACTICE",
    "tags":["绠楁硶","鍙鍖?,"Python","Tkinter","瀹炴搷"],
    "source_url":"https://visualgo.net/",
    "content":"# 瀹炴搷妗堜緥-绠楁硶鍙鍖栭」鐩疄璺礬n\n## 鎺掑簭绠楁硶鍙鍖朶n```python\nimport tkinter as tk\nimport random, time\n\nclass SortVisualizer:\n    def __init__(self, root, n=50):\n        self.canvas = tk.Canvas(root, width=800, height=400)\n        self.canvas.pack()\n        self.data = [random.randint(1, 400) for _ in range(n)]\n        self.bars = []\n        bar_width = 800 / n\n        for i, val in enumerate(self.data):\n            x0 = i * bar_width; y0 = 400 - val\n            bar = self.canvas.create_rectangle(\n                x0, y0, x0+bar_width-1, 400, fill='steelblue')\n            self.bars.append(bar)\n\n    def swap_bars(self, i, j):\n        self.data[i], self.data[j] = self.data[j], self.data[i]\n        # 閲嶇粯鏌卞瓙\n        bar_w = 800 / len(self.data)\n        for idx in (i, j):\n            val = self.data[idx]\n            self.canvas.coords(self.bars[idx],\n                idx*bar_w, 400-val, idx*bar_w+bar_w-1, 400)\n        self.canvas.update()\n        time.sleep(0.01)\n```\n\n## 鍏抽敭璁捐鐐筡n- 姣忔浜ゆ崲鍚庤皟鐢╟anvas.update()閲嶇粯\n- sleep鎺у埗鍔ㄧ敾閫熷害\n- 鐢ㄤ笉鍚岄鑹叉爣璁帮細姣旇緝涓?绾?銆佸凡鎺掑簭(缁?銆佸熀鍑嗗厓绱?榛?\n- 鍔犳帶浠讹細閫熷害婊戝潡銆佹暟鎹噺閫夋嫨銆佺畻娉曢€夋嫨涓嬫媺妗哱n\n## 鎵╁睍: 璺緞鎼滅储鍙鍖朶n- 缃戞牸鍦板浘: 澧欏(榛?銆佽捣鐐?缁?銆佺粓鐐?绾?\n- BFS: 鐢ㄦ贰钃濊壊鏍囪宸茶闂甛n- Dijkstra/A*: 鐢ㄩ鑹叉繁娴呰〃绀鸿窛绂籠n- 鎵惧埌璺緞鍚庣敤閲戣壊楂樹寒\n\n---\n*鏉ユ簮: VisuAlgo, Algorithm Visualizer椤圭洰*"
})

# 鈹€鈹€ 5 more CODE 鈹€鈹€
RESOURCES.append({
    "title":"缂栫▼鎸戞垬-鎿嶄綔绯荤粺璋冨害绠楁硶妯℃嫙瀹炵幇",
    "description":"鐢≒ython妯℃嫙瀹炵幇鎿嶄綔绯荤粺杩涚▼璋冨害绠楁硶锛欶CFS銆丼JF銆佷紭鍏堢骇璋冨害銆丷ound Robin銆丮LFQ澶氱骇鍙嶉闃熷垪銆傚寘鍚繘绋嬬敓鎴愬櫒銆佽皟搴﹀櫒妗嗘灦銆佺敇鐗瑰浘鍙鍖栥€佸钩鍧囩瓑寰呮椂闂?鍛ㄨ浆鏃堕棿缁熻銆?,
    "course":"鎿嶄綔绯荤粺","chapter":"CPU璋冨害","difficulty":"INTERMEDIATE","type":"CODE",
    "tags":["鎿嶄綔绯荤粺","璋冨害绠楁硶","妯℃嫙","Python","浠ｇ爜"],
    "source_url":"https://pages.cs.wisc.edu/~remzi/OSTEP/",
    "content": "# 鎿嶄綔绯荤粺璋冨害绠楁硶妯℃嫙瀹炵幇\n\n```python\nfrom collections import deque\nfrom dataclasses import dataclass\nfrom typing import List, Optional\nimport random\n\n@dataclass\nclass Process:\n    pid: int\n    arrival: int\n    burst: int\n    priority: int = 0\n    remaining: int = 0\n    start_time: Optional[int] = None\n    finish_time: Optional[int] = None\n\n    def __post_init__(self):\n        self.remaining = self.burst\n\ndef generate_processes(n=10, max_arrival=20, max_burst=10) -> List[Process]:\n    procs = []\n    for i in range(n):\n        procs.append(Process(\n            pid=i+1,\n            arrival=random.randint(0, max_arrival),\n            burst=random.randint(1, max_burst),\n            priority=random.randint(1, 5)\n        ))\n    return sorted(procs, key=lambda p: p.arrival)\n\ndef fcfs(processes: List[Process]):\n    \"\"\"鍏堟潵鍏堟湇鍔"\"\"\n    time = 0\n    timeline = []\n    for p in processes:\n        if time < p.arrival:\n            time = p.arrival\n        p.start_time = time\n        time += p.burst\n        p.finish_time = time\n        timeline.append((p.pid, p.start_time, p.finish_time))\n    return timeline\n\ndef sjf(processes: List[Process]):\n    \"\"\"鏈€鐭綔涓氫紭鍏?闈炴姠鍗?\"\"\"\n    time, done = 0, 0\n    n = len(processes)\n    arrived = []\n    timeline = []\n    i = 0\n    while done < n:\n        while i < n and processes[i].arrival <= time:\n            arrived.append(processes[i]); i += 1\n        if not arrived:\n            time = processes[i].arrival; continue\n        arrived.sort(key=lambda p: p.burst, reverse=True)\n        p = arrived.pop()\n        p.start_time = time; time += p.burst; p.finish_time = time\n        timeline.append((p.pid, p.start_time, p.finish_time))\n        done += 1\n    return timeline\n\ndef rr(processes: List[Process], quantum: int = 3):\n    \"\"\"鏃堕棿鐗囪疆杞琝"\"\"\n    time, done, n = 0, 0, len(processes)\n    queue = deque()\n    timeline = []\n    remaining = {p.pid: p.burst for p in processes}\n    i = 0\n    while done < n:\n        while i < n and processes[i].arrival <= time:\n            queue.append(processes[i]); i += 1\n        if not queue:\n            time = processes[i].arrival; continue\n        p = queue.popleft()\n        if p.start_time is None:\n            p.start_time = time\n        run = min(quantum, remaining[p.pid])\n        timeline.append((p.pid, time, time+run))\n        time += run\n        remaining[p.pid] -= run\n        while i < n and processes[i].arrival <= time:\n            queue.append(processes[i]); i += 1\n        if remaining[p.pid] > 0:\n            queue.append(p)\n        else:\n            p.finish_time = time; done += 1\n    return timeline\n\ndef print_stats(processes):\n    total_wait = total_turnaround = 0\n    for p in processes:\n        tat = p.finish_time - p.arrival  # 鍛ㄨ浆鏃堕棿\n        wt = tat - p.burst                 # 绛夊緟鏃堕棿\n        total_wait += wt; total_turnaround += tat\n    n = len(processes)\n    print(f\"Avg Waiting Time: {total_wait/n:.2f}\")\n    print(f\"Avg Turnaround Time: {total_turnaround/n:.2f}\")\n\nif __name__ == '__main__':\n    procs = generate_processes(8, 15, 10)\n    print(\"=== FCFS ===\"); fcfs(procs); print_stats(procs)\n```\n\n---\n*鏉ユ簮: Operating System Concepts, OSTEP*"
})

RESOURCES.append({
    "title":"缂栫▼鎸戞垬-璁捐妯″紡鍦ㄧ湡瀹為」鐩腑鐨勫簲鐢?,
    "description":"灏嗚璁℃ā寮忓簲鐢ㄤ簬鐪熷疄Python椤圭洰鐨勪唬鐮佺ず渚嬶細浣跨敤绛栫暐妯″紡瀹炵幇鏀粯绯荤粺銆佽瀵熻€呮ā寮忓疄鐜颁簨浠剁郴缁熴€佸伐鍘傛ā寮忓垱寤烘棩蹇楀鐞嗗櫒銆佸崟渚嬫ā寮忕鐞嗘暟鎹簱杩炴帴姹犮€傛瘡涓ā寮忓惈瀹屾暣鍙繍琛屼唬鐮併€?,
    "course":"杞欢宸ョ▼","chapter":"璁捐妯″紡瀹炶返","difficulty":"INTERMEDIATE","type":"CODE",
    "tags":["璁捐妯″紡","Python","椤圭洰瀹炶返","浠ｇ爜"],
    "source_url":"https://python-patterns.guide/",
    "content":"# 璁捐妯″紡鍦ㄧ湡瀹為」鐩腑鐨勫簲鐢╘n\n## 绛栫暐妯″紡: 鏀粯绯荤粺\n```python\nfrom abc import ABC, abstractmethod\n\nclass PaymentStrategy(ABC):\n    @abstractmethod\n    def pay(self, amount: float) -> bool: ...\n\nclass CreditCardPayment(PaymentStrategy):\n    def pay(self, amount):\n        print(f\"Paying ${amount:.2f} via Credit Card\")\n        return True\n\nclass PayPalPayment(PaymentStrategy):\n    def pay(self, amount):\n        print(f\"Paying ${amount:.2f} via PayPal\")\n        return True\n\nclass WeChatPayment(PaymentStrategy):\n    def pay(self, amount):\n        print(f\"Paying ${amount:.2f} via WeChat Pay\")\n        return True\n\nclass ShoppingCart:\n    def __init__(self, payment: PaymentStrategy):\n        self._items = []\n        self._payment = payment\n\n    def add_item(self, name, price):\n        self._items.append((name, price))\n\n    def set_payment(self, payment: PaymentStrategy):\n        self._payment = payment\n\n    def checkout(self):\n        total = sum(p for _, p in self._items)\n        return self._payment.pay(total)\n\n# 浣跨敤\ncart = ShoppingCart(CreditCardPayment())\ncart.add_item(\"Book\", 39.99)\ncart.add_item(\"Pen\", 2.50)\ncart.checkout()  # 鐢ㄤ俊鐢ㄥ崱\ncart.set_payment(PayPalPayment())  # 鍒囨崲鍒癙ayPal\ncart.checkout()\n```\n\n## 瑙傚療鑰呮ā寮? 浜嬩欢绯荤粺\n```python\nclass EventManager:\n    def __init__(self, *event_names):\n        self._listeners = {name: [] for name in event_names}\n\n    def subscribe(self, event, listener):\n        self._listeners[event].append(listener)\n\n    def notify(self, event, data=None):\n        for listener in self._listeners.get(event, []):\n            listener(data)\n\n# 浣跨敤\nclass OrderService:\n    def __init__(self):\n        self.events = EventManager('order_created', 'order_cancelled')\n\n    def create_order(self, data):\n        # 鍒涘缓璁㈠崟閫昏緫...\n        self.events.notify('order_created', data)\n\nservice = OrderService()\nservice.events.subscribe('order_created', lambda d: print(f\"Email sent: {d}\"))\nservice.events.subscribe('order_created', lambda d: print(f\"SMS sent: {d}\"))\n```\n\n---\n*鏉ユ簮: Design Patterns (GoF), Python Patterns Guide*"
})

RESOURCES.append({
    "title":"缂栫▼鎸戞垬-鑷畾涔夌紪绋嬭瑷€瑙ｉ噴鍣?,
    "description":"鐢≒ython瀹炵幇涓€涓糠浣犵紪绋嬭瑷€瑙ｉ噴鍣細璇嶆硶鍒嗘瀽鍣?Tokenizer)鈫掗€掑綊涓嬮檷瑙ｆ瀽鍣?Parser)鈫扐ST姹傚€煎櫒(Evaluator)銆傛敮鎸佸彉閲忚祴鍊笺€佺畻鏈繍绠椼€乮f-else鏉′欢銆亀hile寰幆銆佸嚱鏁板畾涔変笌璋冪敤銆?,
    "course":"缂栬瘧鍘熺悊","chapter":"瑙ｉ噴鍣ㄥ疄璺?,"difficulty":"ADVANCED","type":"CODE",
    "tags":["缂栬瘧鍘熺悊","瑙ｉ噴鍣?,"Python","AST","浠ｇ爜"],
    "source_url":"https://craftinginterpreters.com/",
    "content":"# 鑷畾涔夌紪绋嬭瑷€瑙ｉ噴鍣╘n\n## 璇█璇硶\n```\n// 鍙橀噺\nx = 10\ny = x + 5 * 2\n\n// 鏉′欢\nif (y > 10) { print(y) } else { print(0) }\n\n// 寰幆\nwhile (x > 0) { x = x - 1; print(x) }\n\n// 鍑芥暟\nfn add(a, b) { return a + b }\nprint(add(3, 4))\n```\n\n## Token绫诲瀷\n```python\nfrom enum import Enum\nclass TokenType(Enum):\n    NUMBER = 1; IDENT = 2; PLUS = 3; MINUS = 4\n    STAR = 5; SLASH = 6; ASSIGN = 7\n    LPAREN = 8; RPAREN = 9; LBRACE = 10; RBRACE = 11\n    IF = 12; ELSE = 13; WHILE = 14; FN = 15\n    RETURN = 16; SEMI = 17; PRINT = 18\n    EQ = 19; GT = 20; LT = 21; EOF = 22\n```\n\n## AST鑺傜偣\n```python\nclass AST: pass\nclass Number(AST):\n    def __init__(self, val): self.val = val\nclass BinOp(AST):\n    def __init__(self, op, left, right):\n        self.op = op; self.left = left; self.right = right\nclass Assign(AST):\n    def __init__(self, name, expr):\n        self.name = name; self.expr = expr\nclass IfStmt(AST):\n    def __init__(self, cond, then_body, else_body=None):\n        self.cond = cond; self.then_body = then_body\n        self.else_body = else_body or []\nclass WhileStmt(AST):\n    def __init__(self, cond, body):\n        self.cond = cond; self.body = body\nclass FnDef(AST):\n    def __init__(self, name, params, body):\n        self.name = name; self.params = params; self.body = body\nclass FnCall(AST):\n    def __init__(self, name, args):\n        self.name = name; self.args = args\n```\n\n## 鏍稿績鏋舵瀯\n```\nSource Code -> Tokenizer -> Token Stream\nToken Stream -> Parser -> AST\nAST -> Evaluator -> Output\n```\n\n## 瀹炵幇瑕佺偣\n- 閫掑綊涓嬮檷瑙ｆ瀽锛氭瘡涓娉曡鍒欎竴涓猵arse鏂规硶\n- 杩愮畻绗︿紭鍏堢骇锛氶€氳繃parseExpr(浼樺厛绾?閫掑綊瀹炵幇\n- 鐜(浣滅敤鍩?锛氱敤dict閾惧疄鐜帮紝鍐呭眰鐜parent鎸囧悜澶栧眰\n- 闂寘锛氬嚱鏁板璞′繚瀛樺畾涔夋椂鐨勭幆澧冨紩鐢╘n\n---\n*鏉ユ簮: Crafting Interpreters (Robert Nystrom), Let's Build a Simple Interpreter*"
})

RESOURCES.append({
    "title":"缂栫▼鎸戞垬-LeetCode楂橀棰楶ython绮捐В",
    "description":"LeetCode楂橀闈㈣瘯棰楶ython瑙ｆ硶鍚堥泦锛屽惈20閬撶粡鍏搁鐩殑澶氳В娉曞姣?鏆村姏鈫掍紭鍖栤啋鏈€浼?銆佸鏉傚害鍒嗘瀽銆佸父瑙佸彉浣撳拰鏄撻敊鐐广€傝鐩栨暟缁?瀛楃涓?閾捐〃/鏍?DP/鍥炴函鏍稿績棰樺瀷銆?,
    "course":"绠楁硶璁捐涓庡垎鏋?,"chapter":"闈㈣瘯绠楁硶","difficulty":"INTERMEDIATE","type":"CODE",
    "tags":["LeetCode","闈㈣瘯","Python","绠楁硶","浠ｇ爜"],
    "source_url":"https://leetcode.com/problemset/",
    "content":"# LeetCode楂橀棰楶ython绮捐В\n\n## 1. 涓ゆ暟涔嬪拰 (Two Sum)\n```python\ndef twoSum(nums, target):\n    seen = {}\n    for i, n in enumerate(nums):\n        if target - n in seen:\n            return [seen[target-n], i]\n        seen[n] = i\n# O(n) 涓€娆￠亶鍘?+ 鍝堝笇琛╘n```\n\n## 2. 鏈€闀挎棤閲嶅瀛愪覆\n```python\ndef lengthOfLongestSubstring(s):\n    seen = {}\n    left = best = 0\n    for right, ch in enumerate(s):\n        if ch in seen and seen[ch] >= left:\n            left = seen[ch] + 1\n        seen[ch] = right\n        best = max(best, right - left + 1)\n    return best\n# 婊戝姩绐楀彛 O(n)\n```\n\n## 3-20 绮捐В閫熸煡\n| # | 棰樼洰 | 鏍稿績 |\n|---|------|------|\n| 3 | LRU Cache | OrderedDict鎴栧搱甯?鍙屽悜閾捐〃 |\n| 4 | 鎺ラ洦姘?| 鍙屾寚閽?鍗曡皟鏍?DP |\n| 5 | 鍚堝苟K鏈夊簭閾捐〃 | 鏈€灏忓爢O(N log K) |\n| 6 | 鏈€澶у瓙鏁扮粍鍜?| Kadane O(n) |\n| 7 | 宀涘笨鏁伴噺 | DFS/BFS娣规病 |\n| 8 | 浜屽弶鏍戝眰搴忛亶鍘?| BFS闃熷垪 |\n| 9 | 鍏ㄦ帓鍒?| 鍥炴函+used鏁扮粍 |\n| 10 | 涔板崠鑲＄エ鏈€浣虫椂鏈?| 涓€娆￠亶鍘嗚窡韪渶浣庝环 |\n| 11 | 鐜舰閾捐〃 | Floyd蹇參鎸囬拡 |\n| 12 | 鏈夋晥鐨勬嫭鍙?| 鏍堝尮閰?|\n| 13 | 鍚堝苟涓や釜鏈夊簭閾捐〃 | 鍙屾寚閽?鍝ㄥ叺鑺傜偣 |\n| 14 | 鐖ゼ姊?| DP: dp[i]=dp[i-1]+dp[i-2] |\n| 15 | 浜屽弶鏍戞渶澶ф繁搴?| 閫掑綊max(left,right)+1 |\n| 16 | 缈昏浆浜屽弶鏍?| 閫掑綊浜ゆ崲宸﹀彸 |\n| 17 | 瀵圭О浜屽弶鏍?| 閫掑綊check(p.left,q.right) |\n| 18 | 浜屽弶鎼滅储鏍戦獙璇?| 鍖洪棿(min,max)楠岃瘉 |\n| 19 | 鎵撳鍔垗 | dp[i]=max(dp[i-1],dp[i-2]+nums[i]) |\n| 20 | 闆堕挶鍏戞崲 | 瀹屽叏鑳屽寘DP |\n\n---\n*鏉ユ簮: LeetCode, 鍓戞寚Offer, 浠ｇ爜闅忔兂褰?"
})

RESOURCES.append({
    "title":"缂栫▼鎸戞垬-缃戠粶缂栫▼涓嶴ocket閫氫俊瀹炴垬",
    "description":"Python Socket缃戠粶缂栫▼瀹屾暣浠ｇ爜绀轰緥锛歍CP/UDP瀹㈡埛绔笌鏈嶅姟绔€丠TTP鏈嶅姟鍣ㄤ粠闆跺疄鐜般€乄ebSocket瀹炴椂閫氫俊銆佺畝鍗曡亰澶╁搴旂敤銆傚惈select/epoll IO澶氳矾澶嶇敤鍜宎syncio鐗堟湰瀵规瘮銆?,
    "course":"璁＄畻鏈虹綉缁?,"chapter":"缃戠粶缂栫▼","difficulty":"ADVANCED","type":"CODE",
    "tags":["Python","Socket","缃戠粶缂栫▼","TCP","浠ｇ爜"],
    "source_url":"https://docs.python.org/3/howto/sockets.html",
    "content":"# 缃戠粶缂栫▼涓嶴ocket閫氫俊瀹炴垬\n\n## TCP Echo Server\n```python\nimport socket\n\ndef tcp_echo_server(host='0.0.0.0', port=9000):\n    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:\n        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)\n        s.bind((host, port))\n        s.listen(5)\n        print(f\"Listening on {host}:{port}\")\n        while True:\n            conn, addr = s.accept()\n            with conn:\n                data = conn.recv(1024)\n                conn.sendall(data)  # echo back\n\nif __name__ == '__main__':\n    tcp_echo_server()\n```\n\n## 浠庨浂瀹炵幇HTTP Server\n```python\nimport socket\n\nHTTP_RESPONSE = b\"\"\"\\\\\nHTTP/1.1 200 OK\\\\r\\\\n\\\nContent-Type: text/html\\\\r\\\\n\\\nContent-Length: 46\\\\r\\\\n\\\nConnection: close\\\\r\\\\n\\\n\\\\r\\\\n\\\n<html><body><h1>Hello World</h1></body></html>\"\"\"\n\ndef http_server(port=8080):\n    with socket.socket() as s:\n        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)\n        s.bind(('', port)); s.listen(10)\n        print(f\"HTTP Server on port {port}\")\n        while True:\n            conn, addr = s.accept()\n            with conn:\n                request = conn.recv(4096)\n                print(request.decode().split('\\\\r\\\\n')[0])\n                conn.sendall(HTTP_RESPONSE)\n```\n\n## IO澶氳矾澶嶇敤 (select)\n```python\nimport select, socket\n\ndef select_server(port=9001):\n    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)\n    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)\n    server.bind(('', port)); server.listen(10)\n    server.setblocking(False)  # 闈為樆濉瀄n\n    inputs = [server]\n    while inputs:\n        readable, _, _ = select.select(inputs, [], [])\n        for s in readable:\n            if s is server:\n                conn, addr = s.accept()\n                conn.setblocking(False)\n                inputs.append(conn)\n            else:\n                data = s.recv(1024)\n                if data:\n                    s.sendall(data)\n                else:\n                    inputs.remove(s); s.close()\n```\n\n## 绠€鍗曡亰澶╁\n```python\n# 鏈嶅姟绔箍鎾? 缁存姢clients鍒楄〃, 鏀跺埌娑堟伅鍙戞墍鏈変汉(闄ゅ彂閫佽€?\n# 瀹㈡埛绔? recv绾跨▼+send绾跨▼ 鍚屾椂杩愯\n```\n\n---\n*鏉ユ簮: Python Socket HOWTO, Beej's Guide to Network Programming*"
})

print(f"Defined {len(RESOURCES)} supplementary resources")

# 鈹€鈹€ Import pipeline 鈹€鈹€
def connect_db(): return psycopg2.connect(**DB_CONFIG)
def connect_minio(): return Minio(MINIO_CONFIG["endpoint"], access_key=MINIO_CONFIG["access_key"], secret_key=MINIO_CONFIG["secret_key"], secure=MINIO_CONFIG["secure"])
def ensure_bucket(c,b):
    if not c.bucket_exists(b): c.make_bucket(b)
def upload_file(c,b,r):
    sn=r["title"].replace("/","-").replace(" ","_")
    ok=f"resources/{sn}.md"; cb=r["content"].encode("utf-8")
    d=BytesIO(cb); c.put_object(b,ok,d,len(cb),content_type="text/markdown")
    return ok,len(cb)
def gen_emb(ts,d=RUNTIME_CONFIG.embedding_dimension):
    inp=[{"text":t} for t in ts]
    resp=MultiModalEmbedding.call(model=RUNTIME_CONFIG.embedding_model_name,input=inp,dimension=d,output_type="dense")
    if resp.status_code!=200: raise RuntimeError(f"API error: {resp.code} {resp.message}")
    return [e["embedding"] for e in sorted(resp.output.get("embeddings",[]),key=lambda x:x.get("index",0))]
def emb_str(v): return "["+",".join(str(x) for x in v)+"]"

def main():
    dry="--dry-run" in sys.argv
    print(f"Supplement: {len(RESOURCES)} resources")
    if dry:
        for r in RESOURCES: print(f"  [{r['type']:8s}] {r['title']}")
        return
    m=connect_minio(); ensure_bucket(m,BUCKET); c=connect_db()
    try:
        with c:
            with c.cursor() as cur:
                oi={}
                for i,r in enumerate(RESOURCES):
                    ok,sb=upload_file(m,BUCKET,r)
                    oid=str(uuid.uuid4())
                    cur.execute("INSERT INTO storage.resource_object (id,provider,bucket_name,object_key,file_name,mime_type,size_bytes,access_mode,storage_url) VALUES (%s,'RUSTFS',%s,%s,%s,'text/markdown',%s,'PRESIGNED',%s)",(oid,BUCKET,ok,f"{r['title'].replace('/','-')}.md",sb,f"minio://{BUCKET}/{ok}"))
                    oi[r["title"]]=oid
                print(f"Uploaded {len(RESOURCES)} to MinIO")
                ri = {}
                for r in RESOURCES:
                    lid = str(uuid.uuid4())
                    cur.execute("INSERT INTO app.learning_resource (id,title,domain,resource_type,difficulty_level,source_kind,access_scope,summary_text,tags,metadata_json,storage_object_id,status) VALUES (%s,%s,'COMPUTER_SCIENCE',%s::app.resource_type,%s::app.difficulty_level,'IMPORTED'::app.source_kind,'GLOBAL'::app.access_scope,%s,%s,%s,%s,'ACTIVE')",(lid,r["title"],r["type"],r["difficulty"],r["description"],json.dumps(r["tags"],ensure_ascii=False),json.dumps({"course":r["course"],"chapter":r["chapter"],"source_url":r["source_url"]},ensure_ascii=False),oi.get(r["title"])))
                    ri[r["title"]] = lid
                ri2 = {}
                for r in RESOURCES:
                    rd = str(uuid.uuid4())
                    cur.execute("INSERT INTO rag.resource_document (id,resource_id,title,domain,resource_type,difficulty_level,source_kind,source_ref,summary_text,access_scope,metadata_json) VALUES (%s,%s,%s,'COMPUTER_SCIENCE',%s::app.resource_type,%s::app.difficulty_level,'IMPORTED'::app.source_kind,%s,%s,'GLOBAL'::app.access_scope,%s)",(rd,ri[r["title"]],r["title"],r["type"],r["difficulty"],r["source_url"],r["description"],json.dumps({"course":r["course"],"chapter":r["chapter"]},ensure_ascii=False)))
                    ri2[r["title"]] = rd
                print(f"Created {len(RESOURCES)} DB entries")
                # Vectorize
                descs=[r["description"] for r in RESOURCES]; failed=0
                for bs in range(0,len(RESOURCES),5):
                    batch=RESOURCES[bs:bs+5]; bd=descs[bs:bs+5]
                    try: embs=gen_emb(bd)
                    except Exception as e:
                        print(f"Batch [{bs+1}] err: {e}")
                        embs=[];
                        for d in bd:
                            try: embs.extend(gen_emb([d]))
                            except: embs.append(None); failed+=1
                            time.sleep(0.5)
                    for j,r in enumerate(batch):
                        ev=embs[j] if j<len(embs) and embs[j] is not None else None
                        if ev is None: continue
                        cur.execute("INSERT INTO rag.resource_chunk (document_id,resource_id,chunk_no,content,embedding,token_count,domain,resource_type,difficulty_level,access_scope,quality_score,metadata_json) VALUES (%s,%s,1,%s,%s,%s,'COMPUTER_SCIENCE',%s::app.resource_type,%s::app.difficulty_level,'GLOBAL'::app.access_scope,0.90,%s)",(ri2[r["title"]],ri[r["title"]],r["description"],emb_str(ev),int(len(r["description"])/1.5),r["type"],r["difficulty"],json.dumps({"course":r["course"],"chapter":r["chapter"]},ensure_ascii=False)))
                    print(f"Vectorized [{min(bs+5,len(RESOURCES))}/{len(RESOURCES)}]")
                    time.sleep(0.3)
        if failed: print(f"Warning: {failed} failed")
        print(f"Done. {len(RESOURCES)} imported.")
    finally: c.close()

if __name__=="__main__": main()

