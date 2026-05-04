"""
Create real downloadable resource files with educational content,
upload to MinIO, and register in PostgreSQL.
Content sourced from official documentation and standard CS curriculum.
"""
import sys
import os
import uuid
import json
import hashlib
import time
from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path

import psycopg2
from minio import Minio
from dashscope import MultiModalEmbedding
from settings_helper import configure_dashscope_api_key

RUNTIME_CONFIG = configure_dashscope_api_key()


# 鈹€鈹€ Config 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€
DB_CONFIG = RUNTIME_CONFIG.postgres.model_dump()
MINIO_CONFIG = RUNTIME_CONFIG.minio.model_dump(exclude={"bucket"})
BUCKET = RUNTIME_CONFIG.minio.bucket
NOW = "2026-05-02"

# 鈹€鈹€ Educational Content 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€
# Each resource: (title, description, course, chapter, difficulty, type, tags, source_url, file_content)
# type: READING, MINDMAP, PRACTICE

RESOURCES = []

# 鈹€鈹€ Lecture Notes / Readings (READING type) 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€
RESOURCES.append({
    "title": "Linux鍛戒护琛屽畬鍏ㄦ寚鍗?,
    "description": "Linux鍛戒护琛屾牳蹇冨懡浠ゅ畬鍏ㄦ寚鍗楋紝娑电洊鏂囦欢鎿嶄綔銆佽繘绋嬬鐞嗐€佹潈闄愭帶鍒躲€佺閬撲笌閲嶅畾鍚戙€丼hell鑴氭湰鍩虹锛屾簮鑷狦NU Coreutils鍜孡inux man-pages瀹樻柟鏂囨。銆?,
    "course": "鎿嶄綔绯荤粺", "chapter": "Linux鍩虹", "difficulty": "BASIC",
    "type": "READING",
    "tags": ["Linux", "鍛戒护琛?, "Shell", "Bash"],
    "source_url": "https://www.gnu.org/software/coreutils/manual/",
    "content": """# Linux鍛戒护琛屽畬鍏ㄦ寚鍗?
## 1. 鏂囦欢涓庣洰褰曟搷浣?- `ls -la` 鈥?鍒楀嚭鐩綍鎵€鏈夋枃浠?鍚殣钘?锛?l闀挎牸寮? -a鏄剧ず闅愯棌
- `cd <dir>` 鈥?鍒囨崲鐩綍锛宍cd -` 杩斿洖涓婁竴娆＄洰褰?- `pwd` 鈥?鎵撳嵃褰撳墠宸ヤ綔鐩綍
- `cp <src> <dst>` 鈥?澶嶅埗鏂囦欢锛宍cp -r` 閫掑綊澶嶅埗鐩綍
- `mv <src> <dst>` 鈥?绉诲姩/閲嶅懡鍚?- `rm <file>` 鈥?鍒犻櫎鏂囦欢锛宍rm -rf <dir>` 閫掑綊寮哄埗鍒犻櫎鐩綍(鍗遍櫓!)
- `mkdir -p <path>` 鈥?鍒涘缓鐩綍(鍚埗鐩綍)
- `find <dir> -name "*.py"` 鈥?鎸夊悕绉版煡鎵炬枃浠?
## 2. 鏂囦欢鍐呭鏌ョ湅
- `cat <file>` 鈥?杈撳嚭鏂囦欢鍏ㄩ儴鍐呭
- `less <file>` 鈥?鍒嗛〉鏌ョ湅(涓婁笅缈婚〉,/鎼滅储,q閫€鍑?
- `head -n 20 <file>` 鈥?鏌ョ湅鍓?0琛?- `tail -f <file>` 鈥?瀹炴椂璺熻釜鏂囦欢灏鹃儴(鏃ュ織鐩戞帶)
- `grep -r "pattern" <dir>` 鈥?閫掑綊鎼滅储鏂囨湰
- `wc -l <file>` 鈥?缁熻琛屾暟

## 3. 鏉冮檺绠＄悊
- `chmod 755 <file>` 鈥?璁剧疆鏉冮檺(rwxr-xr-x)
  - r=4, w=2, x=1, 涓変綅鍒嗗埆浠ｈ〃owner/group/others
- `chown user:group <file>` 鈥?鏀瑰彉鎵€鏈夎€?- `umask 022` 鈥?榛樿鏉冮檺鎺╃爜

## 4. 绠￠亾涓庨噸瀹氬悜
- `cmd1 | cmd2` 鈥?绠￠亾锛歝md1鐨勮緭鍑轰綔涓篶md2鐨勮緭鍏?- `cmd > file` 鈥?閲嶅畾鍚戣緭鍑?瑕嗙洊)
- `cmd >> file` 鈥?閲嶅畾鍚戣緭鍑?杩藉姞)
- `cmd < file` 鈥?浠庢枃浠惰鍙栬緭鍏?- `cmd 2>&1` 鈥?灏唖tderr閲嶅畾鍚戝埌stdout

## 5. 杩涚▼绠＄悊
- `ps aux` 鈥?鍒楀嚭鎵€鏈夎繘绋?- `top` / `htop` 鈥?瀹炴椂杩涚▼鐩戞帶
- `kill -9 <pid>` 鈥?寮哄埗缁堟杩涚▼
- `&` 鈥?鍚庡彴杩愯锛宍jobs`鏌ョ湅鍚庡彴浠诲姟锛宍fg` 璋冨洖鍓嶅彴
- `nohup cmd &` 鈥?鍚庡彴杩愯涓斾笉鍙楃粓绔叧闂奖鍝?
## 6. 纾佺洏涓庣綉缁?- `df -h` 鈥?纾佺洏浣跨敤鎯呭喌(浜虹被鍙)
- `du -sh <dir>` 鈥?鐩綍澶у皬姹囨€?- `netstat -tlnp` 鈥?鏌ョ湅鐩戝惉绔彛
- `ss -tlnp` 鈥?鐜颁唬鏇夸唬netstat
- `curl -X GET <url>` 鈥?HTTP璇锋眰
- `wget <url>` 鈥?涓嬭浇鏂囦欢

## 7. Shell鑴氭湰鍩虹
```bash
#!/bin/bash
# 鍙橀噺
NAME="world"
echo "Hello, $NAME"

# 鏉′欢鍒ゆ柇
if [ -f "$FILE" ]; then
    echo "File exists"
fi

# 寰幆
for i in {1..10}; do
    echo "Number: $i"
done

# 鍑芥暟
myfunc() {
    local var=$1
    echo "Arg: $var"
}
```

---
*鏉ユ簮: GNU Coreutils Manual, Linux man-pages, Bash Reference Manual*
"""
})

RESOURCES.append({
    "title": "Python铏氭嫙鐜涓庡寘绠＄悊瀹屽叏鎸囧崡",
    "description": "Python venv/virtualenv/pip/conda鐜绠＄悊涓庡寘绠＄悊鏈€浣冲疄璺碉紝鍩轰簬Python瀹樻柟鏂囨。鍜孭yPA鎸囧崡銆?,
    "course": "绋嬪簭璁捐", "chapter": "Python宸ュ叿閾?, "difficulty": "BASIC",
    "type": "READING",
    "tags": ["Python", "venv", "pip", "铏氭嫙鐜"],
    "source_url": "https://docs.python.org/3/tutorial/venv.html",
    "content": """# Python铏氭嫙鐜涓庡寘绠＄悊瀹屽叏鎸囧崡

## 1. 铏氭嫙鐜姒傚康
铏氭嫙鐜鏄疨ython椤圭洰闅旂鐨勪緷璧栫┖闂淬€備笉鍚岄」鐩彲瀹夎涓嶅悓鐗堟湰鐨勫悓涓€搴撹€屼笉鍐茬獊銆?
## 2. venv (Python 3.3+ 鍐呯疆)
```bash
# 鍒涘缓铏氭嫙鐜
python -m venv myenv

# 婵€娲?Linux/Mac)
source myenv/bin/activate

# 婵€娲?Windows)
myenv\\Scripts\\activate

# 閫€鍑?deactivate
```

## 3. pip 鍖呯鐞?```bash
# 瀹夎鍖?pip install requests
pip install requests==2.28.0  # 鎸囧畾鐗堟湰
pip install "requests>=2.28,<3.0"  # 鐗堟湰鑼冨洿

# 浠庢枃浠跺畨瑁?pip install -r requirements.txt

# 瀵煎嚭渚濊禆
pip freeze > requirements.txt

# 鍗歌浇
pip uninstall requests

# 鏌ョ湅宸插畨瑁?pip list
pip show requests  # 璇︾粏淇℃伅
```

## 4. requirements.txt vs pyproject.toml
- `requirements.txt`: 绠€鍗曚緷璧栧垪琛?閫傚悎搴旂敤)
- `pyproject.toml`: 鐜颁唬Python椤圭洰鍏冩暟鎹拰渚濊禆澹版槑(閫傚悎搴?
- `pip-tools` (pip-compile): 浠巔yproject.toml鐢熸垚閿佸畾渚濊禆

## 5. 渚濊禆閿佸畾
```bash
# pip-tools宸ヤ綔娴?pip install pip-tools
pip-compile pyproject.toml  # 鐢熸垚requirements.txt
pip-compile --upgrade pyproject.toml  # 鍗囩骇鎵€鏈変緷璧?pip-sync requirements.txt  # 鍚屾鐜鍒伴攣瀹氱増鏈?```

## 6. 鏈€浣冲疄璺?- 姣忎釜椤圭洰涓€涓櫄鎷熺幆澧?- 灏唙env鐩綍鍔犲叆`.gitignore`
- 鎻愪氦`requirements.txt`(閿佸畾鐗堟湰)鍜宍pyproject.toml`(瀹芥澗鐗堟湰)
- 浣跨敤`pip install -e .`浠ュ彲缂栬緫妯″紡瀹夎鏈湴鍖?- 鐢熶骇鐜浣跨敤Docker鎴朇I鐜绠＄悊渚濊禆

## 7. 甯歌闂
- **ModuleNotFoundError**: 妫€鏌ヨ櫄鎷熺幆澧冩槸鍚︽縺娲?鍖呮槸鍚﹀凡瀹夎
- **鐗堟湰鍐茬獊**: 浣跨敤`pip check`妫€鏌ヤ緷璧栧啿绐?- **鏉冮檺閿欒**: 涓嶈鐢╯udo pip install, 浣跨敤铏氭嫙鐜

---
*鏉ユ簮: Python Packaging User Guide (packaging.python.org), Python瀹樻柟鏂囨。*
"""
})

RESOURCES.append({
    "title": "Git宸ヤ綔娴佷笌鏈€浣冲疄璺?,
    "description": "Git鍒嗗竷寮忕増鏈帶鍒剁殑鏍稿績宸ヤ綔娴併€佸垎鏀瓥鐣ャ€佹彁浜よ鑼冦€佸悎骞朵笌鍙樺熀鎿嶄綔璇﹁В锛屽熀浜嶱ro Git瀹樻柟鏂囨。銆?,
    "course": "杞欢宸ョ▼", "chapter": "鐗堟湰鎺у埗", "difficulty": "BASIC",
    "type": "READING",
    "tags": ["Git", "鐗堟湰鎺у埗", "鍒嗘敮", "GitHub"],
    "source_url": "https://git-scm.com/book/en/v2",
    "content": """# Git宸ヤ綔娴佷笌鏈€浣冲疄璺?
## 1. Git鏍稿績姒傚康
- **宸ヤ綔鍖?Working Directory)**: 褰撳墠缂栬緫鐨勬枃浠?- **鏆傚瓨鍖?Staging Area/Index)**: `git add`鍚庣殑鐘舵€?- **鏈湴浠撳簱(Local Repo)**: `git commit`鍚庣殑鎻愪氦鍘嗗彶
- **杩滅▼浠撳簱(Remote Repo)**: `git push`鎺ㄩ€佸埌鐨勬湇鍔″櫒

## 2. 鍩烘湰鎿嶄綔
```bash
git init                    # 鍒濆鍖栦粨搴?git clone <url>             # 鍏嬮殕杩滅▼浠撳簱
git add <file>              # 娣诲姞鍒版殏瀛樺尯
git commit -m "message"     # 鎻愪氦
git push origin main        # 鎺ㄩ€佸埌杩滅▼
git pull origin main        # 鎷夊彇杩滅▼鏇存柊
git status                  # 鏌ョ湅褰撳墠鐘舵€?git log --oneline --graph   # 鏌ョ湅鎻愪氦鍘嗗彶
```

## 3. 鍒嗘敮绠＄悊
```bash
git branch <name>           # 鍒涘缓鍒嗘敮
git checkout <name>         # 鍒囨崲鍒嗘敮
git checkout -b <name>      # 鍒涘缓骞跺垏鎹?git merge <name>            # 鍚堝苟鍒嗘敮鍒板綋鍓?git rebase main             # 灏嗗綋鍓嶅垎鏀彉鍩哄埌main
git branch -d <name>        # 鍒犻櫎鍒嗘敮
```

## 4. 甯歌宸ヤ綔娴?- **GitHub Flow**: main + feature鍒嗘敮, PR review, 鍚堝苟鍚庨儴缃?- **Git Flow**: main/develop/feature/release/hotfix, 閫傚悎瀹氭湡鍙戝竷
- **Trunk-Based**: 鐭垎鏀?棰戠箒鍚堝苟鍒癿ain, 閰嶅悎feature flags

## 5. 鎻愪氦瑙勮寖(Conventional Commits)
```
<type>(<scope>): <description>

feat(auth): add login with JWT
fix(db): fix connection pool leak
docs(api): update endpoint docs
refactor(core): extract validation logic
test(auth): add login test cases
```

## 6. 鏈€浣冲疄璺?- 鎻愪氦鍓峘git diff --staged`瀹℃煡鍙樻洿
- 灏忎笖涓撴敞鐨勬彁浜?涓€浣嶄富棰樹竴涓彁浜?
- 鏈夋剰涔夌殑鎻愪氦淇℃伅(WHAT + WHY)
- 鐢╜.gitignore`鎺掗櫎鏋勫缓浜х墿鍜屾晱鎰熸枃浠?- 瀹氭湡`git fetch`淇濇寔杩滅▼鍒嗘敮淇℃伅鏇存柊
- 瑙ｅ喅鍚堝苟鍐茬獊鍚庤繍琛屾祴璇?
## 7. 甯哥敤鍦烘櫙
```bash
# 鎾ら攢宸ヤ綔鍖轰慨鏀?git checkout -- <file>
# 鎾ら攢鏆傚瓨
git reset HEAD <file>
# 淇敼鏈€鍚庝竴娆℃彁浜?git commit --amend
# 涓存椂淇濆瓨宸ヤ綔
git stash
git stash pop
# 鏌ョ湅璋佹敼浜嗘煇琛?git blame <file>
```

---
*鏉ユ簮: Pro Git (Scott Chacon), GitHub Docs, Conventional Commits Spec*
"""
})

RESOURCES.append({
    "title": "姝ｅ垯琛ㄨ揪寮忓畬鍏ㄦ暀绋?,
    "description": "姝ｅ垯琛ㄨ揪寮忚娉曞ぇ鍏ㄤ笌瀹炴垬绀轰緥锛屾兜鐩栧熀纭€鍏冨瓧绗︺€侀噺璇嶃€佸垎缁勩€佸墠鍚庢煡鎵俱€佸洖婧帶鍒讹紝鍩轰簬PCRE瑙勮寖鍜孧DN鏂囨。銆?,
    "course": "绋嬪簭璁捐", "chapter": "瀛楃涓插鐞?, "difficulty": "INTERMEDIATE",
    "type": "READING",
    "tags": ["姝ｅ垯琛ㄨ揪寮?, "Regex", "瀛楃涓?, "妯″紡鍖归厤"],
    "source_url": "https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Regular_expressions",
    "content": """# 姝ｅ垯琛ㄨ揪寮忓畬鍏ㄦ暀绋?
## 1. 鍩虹鍏冨瓧绗?| 绗﹀彿 | 鍚箟 | 绀轰緥 |
|------|------|------|
| `.` | 鍖归厤浠绘剰鍗曞瓧绗?闄ゆ崲琛? | `h.t` 鍖归厤 hat, hit, h3t |
| `\\d` | 鏁板瓧 [0-9] | `\\d{3}` 鍖归厤 123 |
| `\\w` | 鍗曡瘝瀛楃 [a-zA-Z0-9_] | `\\w+` 鍖归厤涓€涓瘝 |
| `\\s` | 绌虹櫧瀛楃 | `a\\sb` 鍖归厤 a b |
| `\\D` | 闈炴暟瀛?| |
| `\\W` | 闈炲崟璇嶅瓧绗?| |
| `\\S` | 闈炵┖鐧藉瓧绗?| |

## 2. 閲忚瘝
| 绗﹀彿 | 鍚箟 |
|------|------|
| `*` | 0娆℃垨澶氭(璐績) |
| `+` | 1娆℃垨澶氭(璐績) |
| `?` | 0娆℃垨1娆?|
| `{n}` | 鎭板ソn娆?|
| `{n,}` | 鑷冲皯n娆?|
| `{n,m}` | n鍒癿娆?|
| `*?`, `+?` | 闈炶椽蹇冨尮閰?|

## 3. 瀛楃绫讳笌閿氱偣
- `[abc]` 鍖归厤a銆乥鎴朿
- `[^abc]` 鍖归厤闈瀉銆乥銆乧鐨勫瓧绗?- `[a-z]` 鑼冨洿
- `^` 琛岄, `$` 琛屽熬
- `\\b` 鍗曡瘝杈圭晫, `\\B` 闈炲崟璇嶈竟鐣?
## 4. 鍒嗙粍涓庢崟鑾?- `(pattern)` 鎹曡幏缁? 鍙€氳繃`\\1`鍙嶅悜寮曠敤
- `(?:pattern)` 闈炴崟鑾风粍
- `(?<name>pattern)` 鍛藉悕缁?- `|` 鎴?鍒嗘敮

## 5. 甯哥敤绀轰緥
```python
import re
# 閭
re.match(r'^[\\w.-]+@[\\w.-]+\\.\\w+$', email)
# 鎵嬫満鍙?涓浗)
re.match(r'^1[3-9]\\d{9}$', phone)
# URL
re.match(r'^https?://[\\w.-]+(:\\d+)?(/.*)?$', url)
# IP鍦板潃
re.match(r'^(\\d{1,3}\\.){3}\\d{1,3}$', ip)
# HTML鏍囩鎻愬彇
re.findall(r'<([a-z]+)[^>]*>', html)
```

## 6. 鎬ц兘娉ㄦ剰浜嬮」
- 閬垮厤鐏鹃毦鎬у洖婧?catastrophic backtracking)
  - 鍗遍櫓妯″紡: `(a+)+b` 瀵?`aaaaaaaaac` 闇€瑕佹寚鏁版椂闂?- 浣跨敤鍘熷瓙缁勬垨鎵€鏈夋牸閲忚瘝闃叉杩囧害鍥炴函
- 瀵圭畝鍗曞尮閰嶄紭鍏堢敤瀛楃涓叉柟娉?startswith/contains)

---
*鏉ユ簮: MDN Regular Expressions Guide, PCRE Documentation*
"""
})

# 鈹€鈹€ Code Examples 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€
RESOURCES.append({
    "title": "缁忓吀鎺掑簭绠楁硶Python瀹炵幇",
    "description": "7绉嶇粡鍏告帓搴忕畻娉曠殑Python瀹炵幇涓庡姣斿垎鏋愶紝鍖呭惈鍐掓场銆侀€夋嫨銆佹彃鍏ャ€佸笇灏斻€佸綊骞躲€佸揩閫熴€佸爢鎺掑簭锛岄檮澶嶆潅搴﹀垎鏋愬拰娴嬭瘯鐢ㄤ緥銆?,
    "course": "绠楁硶璁捐涓庡垎鏋?, "chapter": "鎺掑簭绠楁硶", "difficulty": "INTERMEDIATE",
    "type": "READING",
    "tags": ["鎺掑簭", "Python", "绠楁硶瀹炵幇"],
    "source_url": "https://docs.python.org/3/howto/sorting.html",
    "content": '''"""缁忓吀鎺掑簭绠楁硶鐨凱ython瀹炵幇涓庡姣斿垎鏋?""
from typing import List, Any
import random
import time


def bubble_sort(arr: List[Any]) -> List[Any]:
    """鍐掓场鎺掑簭 O(n^2) 绋冲畾 鍘熷湴"""
    n = len(arr)
    for i in range(n):
        swapped = False
        for j in range(n - 1 - i):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                swapped = True
        if not swapped:
            break  # 宸叉湁搴?鎻愬墠閫€鍑?    return arr


def selection_sort(arr: List[Any]) -> List[Any]:
    """閫夋嫨鎺掑簭 O(n^2) 涓嶇ǔ瀹?鍘熷湴 浜ゆ崲娆℃暟鏈€灏?<=n-1)"""
    n = len(arr)
    for i in range(n):
        min_idx = i
        for j in range(i + 1, n):
            if arr[j] < arr[min_idx]:
                min_idx = j
        arr[i], arr[min_idx] = arr[min_idx], arr[i]
    return arr


def insertion_sort(arr: List[Any]) -> List[Any]:
    """鎻掑叆鎺掑簭 O(n^2) 绋冲畾 鍘熷湴 杩戜箮鏈夊簭鏃禣(n)"""
    for i in range(1, len(arr)):
        key = arr[i]
        j = i - 1
        while j >= 0 and arr[j] > key:
            arr[j + 1] = arr[j]
            j -= 1
        arr[j + 1] = key
    return arr


def merge_sort(arr: List[Any]) -> List[Any]:
    """褰掑苟鎺掑簭 O(n log n) 绋冲畾 闇€O(n)杈呭姪绌洪棿"""
    if len(arr) <= 1:
        return arr
    mid = len(arr) // 2
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])
    # 鍚堝苟
    result = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            result.append(left[i]); i += 1
        else:
            result.append(right[j]); j += 1
    result.extend(left[i:])
    result.extend(right[j:])
    return result


def quick_sort(arr: List[Any]) -> List[Any]:
    """蹇€熸帓搴?O(n log n)骞冲潎 涓嶇ǔ瀹?鍘熷湴"""
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    return quick_sort(left) + middle + quick_sort(right)


def heap_sort(arr: List[Any]) -> List[Any]:
    """鍫嗘帓搴?O(n log n) 涓嶇ǔ瀹?鍘熷湴"""
    import heapq
    # 浣跨敤Python鍐呯疆heapq(鏈€灏忓爢)
    result = []
    for x in arr:
        heapq.heappush(result, x)
    return [heapq.heappop(result) for _ in range(len(result))]


def shell_sort(arr: List[Any]) -> List[Any]:
    """甯屽皵鎺掑簭 O(n log n)~O(n^2) 涓嶇ǔ瀹?鍘熷湴 鎻掑叆鎺掑簭鐨勬敼杩?""
    n = len(arr)
    gap = n // 2
    while gap > 0:
        for i in range(gap, n):
            temp = arr[i]
            j = i
            while j >= gap and arr[j - gap] > temp:
                arr[j] = arr[j - gap]
                j -= gap
            arr[j] = temp
        gap //= 2
    return arr


# 鈹€鈹€ 娴嬭瘯涓庡姣?鈹€鈹€
if __name__ == "__main__":
    algorithms = {
        "Bubble": bubble_sort,
        "Selection": selection_sort,
        "Insertion": insertion_sort,
        "Shell": shell_sort,
        "Merge": merge_sort,
        "Quick": quick_sort,
        "Heap": heap_sort,
    }

    # 姝ｇ‘鎬ф祴璇?    test_data = [64, 34, 25, 12, 22, 11, 90]
    expected = sorted(test_data)
    for name, fn in algorithms.items():
        result = fn(test_data.copy())
        assert result == expected, f"{name} failed: {result}"
    print("All algorithms pass correctness test.")

    # 鎬ц兘娴嬭瘯
    N = 5000
    data = [random.randint(0, 10000) for _ in range(N)]
    print(f"\\nPerformance test (n={N}):")
    for name, fn in algorithms.items():
        arr = data.copy()
        start = time.perf_counter()
        fn(arr)
        elapsed = time.perf_counter() - start
        print(f"  {name:10s}: {elapsed:.4f}s")
'''
})

RESOURCES.append({
    "title": "璁捐妯″紡Python瀹炵幇绀轰緥",
    "description": "6绉嶅父鐢ㄨ璁℃ā寮忕殑Python瀹炵幇锛屽寘鍚崟渚嬨€佸伐鍘傘€佽瀵熻€呫€佺瓥鐣ャ€佽楗板櫒銆佷唬鐞嗘ā寮忥紝甯︾被鍨嬫敞瑙ｅ拰鐢ㄦ硶绀轰緥銆?,
    "course": "绋嬪簭璁捐", "chapter": "璁捐妯″紡", "difficulty": "INTERMEDIATE",
    "type": "READING",
    "tags": ["璁捐妯″紡", "Python", "GoF"],
    "source_url": "https://python-patterns.guide/",
    "content": '''"""6绉嶅父鐢ㄨ璁℃ā寮忕殑Python瀹炵幇"""
from abc import ABC, abstractmethod
from typing import Dict, List, Any
import threading


# 鈹€鈹€ 1. 鍗曚緥妯″紡 (Singleton) 鈹€鈹€
class Singleton:
    """绾跨▼瀹夊叏鐨勫崟渚嬫ā寮?""
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                # 鍙岄噸妫€鏌?                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance


# 鈹€鈹€ 2. 宸ュ巶鏂规硶 (Factory Method) 鈹€鈹€
class Product(ABC):
    @abstractmethod
    def operation(self) -> str: ...

class ConcreteProductA(Product):
    def operation(self) -> str:
        return "Product A"

class ConcreteProductB(Product):
    def operation(self) -> str:
        return "Product B"

class Creator(ABC):
    @abstractmethod
    def factory_method(self) -> Product: ...

    def some_operation(self) -> str:
        product = self.factory_method()
        return f"Creator: {product.operation()}"

class ConcreteCreatorA(Creator):
    def factory_method(self) -> Product:
        return ConcreteProductA()


# 鈹€鈹€ 3. 瑙傚療鑰呮ā寮?(Observer) 鈹€鈹€
class Observer(ABC):
    @abstractmethod
    def update(self, message: str) -> None: ...

class Subject:
    def __init__(self):
        self._observers: List[Observer] = []

    def attach(self, observer: Observer) -> None:
        self._observers.append(observer)

    def detach(self, observer: Observer) -> None:
        self._observers.remove(observer)

    def notify(self, message: str) -> None:
        for observer in self._observers:
            observer.update(message)

class ConcreteObserver(Observer):
    def __init__(self, name: str):
        self.name = name

    def update(self, message: str) -> None:
        print(f"{self.name} received: {message}")


# 鈹€鈹€ 4. 绛栫暐妯″紡 (Strategy) 鈹€鈹€
class Strategy(ABC):
    @abstractmethod
    def execute(self, data: List[int]) -> List[int]: ...

class QuickSortStrategy(Strategy):
    def execute(self, data: List[int]) -> List[int]:
        return sorted(data)  # 绠€鍖?
class ReverseSortStrategy(Strategy):
    def execute(self, data: List[int]) -> List[int]:
        return sorted(data, reverse=True)

class Context:
    def __init__(self, strategy: Strategy):
        self._strategy = strategy

    def set_strategy(self, strategy: Strategy) -> None:
        self._strategy = strategy

    def execute_strategy(self, data: List[int]) -> List[int]:
        return self._strategy.execute(data)


# 鈹€鈹€ 5. 瑁呴グ鍣ㄦā寮?(Decorator) 鈹€鈹€
class Component(ABC):
    @abstractmethod
    def operation(self) -> str: ...

class ConcreteComponent(Component):
    def operation(self) -> str:
        return "ConcreteComponent"

class Decorator(Component):
    def __init__(self, component: Component):
        self._component = component

    def operation(self) -> str:
        return self._component.operation()

class LoggingDecorator(Decorator):
    def operation(self) -> str:
        print(f"[LOG] Calling operation()")
        return super().operation()

class TimingDecorator(Decorator):
    def operation(self) -> str:
        import time
        start = time.time()
        result = super().operation()
        print(f"[TIME] {time.time() - start:.4f}s")
        return result


# 鈹€鈹€ 6. 浠ｇ悊妯″紡 (Proxy) 鈹€鈹€
class Subject_Interface(ABC):
    @abstractmethod
    def request(self) -> str: ...

class RealSubject(Subject_Interface):
    def request(self) -> str:
        return "RealSubject: handling request"

class Proxy(Subject_Interface):
    def __init__(self):
        self._real_subject = None

    def request(self) -> str:
        # 寤惰繜鍒濆鍖?铏氭嫙浠ｇ悊)
        if self._real_subject is None:
            self._real_subject = RealSubject()

        # 璁块棶鎺у埗(淇濇姢浠ｇ悊)
        print("[Proxy] Logging before request")
        result = self._real_subject.request()
        print("[Proxy] Logging after request")
        return result


if __name__ == "__main__":
    # 鍗曚緥娴嬭瘯
    s1 = Singleton(); s2 = Singleton()
    assert s1 is s2
    print("Singleton: OK")

    # 宸ュ巶娴嬭瘯
    creator = ConcreteCreatorA()
    print(creator.some_operation())

    # 瑙傚療鑰呮祴璇?    subject = Subject()
    subject.attach(ConcreteObserver("Obs1"))
    subject.attach(ConcreteObserver("Obs2"))
    subject.notify("Event happened!")

    # 绛栫暐娴嬭瘯
    ctx = Context(QuickSortStrategy())
    print(ctx.execute_strategy([3, 1, 2]))
    ctx.set_strategy(ReverseSortStrategy())
    print(ctx.execute_strategy([3, 1, 2]))

    # 瑁呴グ鍣ㄦ祴璇?    component = LoggingDecorator(TimingDecorator(ConcreteComponent()))
    print(component.operation())

    # 浠ｇ悊娴嬭瘯
    proxy = Proxy()
    print(proxy.request())
    print("All patterns tested!")
'''
})

# 鈹€鈹€ Practice Problem Sets 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€
RESOURCES.append({
    "title": "鏁版嵁缁撴瀯缁忓吀涔犻闆嗭紙闄勮瑙ｏ級",
    "description": "20閬撴暟鎹粨鏋勭粡鍏镐範棰橈紝娑电洊鏁扮粍銆侀摼琛ㄣ€佹爤銆侀槦鍒椼€佹爲銆佸浘銆佸搱甯岃〃锛屾瘡閬撻闄勮缁嗚В绛斿拰澶嶆潅搴﹀垎鏋愩€?,
    "course": "鏁版嵁缁撴瀯", "chapter": "缁煎悎缁冧範", "difficulty": "INTERMEDIATE",
    "type": "READING",
    "tags": ["鏁版嵁缁撴瀯", "涔犻", "闈㈣瘯"],
    "source_url": "https://leetcode.com/problemset/",
    "content": """# 鏁版嵁缁撴瀯缁忓吀涔犻闆?
## 鏁扮粍涓庡瓧绗︿覆
### 1. 涓ゆ暟涔嬪拰 (Two Sum)
缁欏畾鏁扮粍nums鍜岀洰鏍囧€紅arget锛屾壘鍑哄拰涓簍arget鐨勪袱涓暟鐨勪笅鏍囥€?- 瑙ｆ硶: 鍝堝笇琛?O(n), 杈规壂鎻忚竟妫€鏌arget-nums[i]鏄惁鍦ㄥ搱甯岃〃涓?- 鍏抽敭: 涓€娆￠亶鍘? 鍊尖啋绱㈠紩鏄犲皠

### 2. 鏈€闀挎棤閲嶅瀛愪覆
缁欏畾瀛楃涓瞫锛屾壘鍑烘渶闀跨殑涓嶅惈閲嶅瀛楃鐨勫瓙涓查暱搴︺€?- 瑙ｆ硶: 婊戝姩绐楀彛 O(n), 宸﹀彸鎸囬拡+鍝堝笇闆嗗悎
- 鍏抽敭: 閬囧埌閲嶅瀛楃鏃跺乏鎸囬拡璺冲埌閲嶅瀛楃鐨勪笅涓€涓綅缃?
### 3. 鍚堝苟涓や釜鏈夊簭鏁扮粍
- 瑙ｆ硶: 浠庡悗寰€鍓嶅～鍏?O(m+n), 鍙屾寚閽堟瘮杈冭緝澶у厓绱?- 鍏抽敭: 鍊掑簭閬垮厤瑕嗙洊鏈鐞嗙殑鍏冪礌

## 閾捐〃
### 4. 鍙嶈浆閾捐〃
```python
def reverse(head):
    prev, cur = None, head
    while cur:
        nxt = cur.next
        cur.next = prev
        prev = cur
        cur = nxt
    return prev
```

### 5. 鐜舰閾捐〃妫€娴?- Floyd蹇參鎸囬拡: fast璧?姝low璧?姝? 鐩搁亣鍒欐湁鐜?- 鎵剧幆鍏ュ彛: 鐩搁亣鍚巋ead鍜宻low鍚屾椂鍓嶈繘, 鍐嶆鐩搁亣鐐瑰嵆鍏ュ彛

### 6. 鍚堝苟K涓湁搴忛摼琛?- 瑙ｆ硶1: 浼樺厛闃熷垪(鏈€灏忓爢) O(N log K)
- 瑙ｆ硶2: 鍒嗘不娉曚袱涓ゅ悎骞?O(N log K)
- 鍏抽敭: 缁存姢K涓寚閽堝湪鍫嗕腑

## 鏍堜笌闃熷垪
### 7. 鏈夋晥鐨勬嫭鍙?- 鏍堝瓨鏀惧乏鎷彿, 閬囧彸鎷彿妫€鏌ユ爤椤舵槸鍚﹀尮閰?- O(n), 鏍堜负绌轰笖瀛楃鍧囧鐞嗗畬鈫掓湁鏁?
### 8. 鐢ㄦ爤瀹炵幇闃熷垪
- 涓や釜鏍? push鏍?pop鏍?- push: O(1)鐩存帴鍏ush鏍?- pop: 鑻op鏍堢┖, 灏唒ush鏍堝叏閮ㄥ脊鍑哄帇鍏op鏍?鍧囨憡O(1))

## 鏍?### 9. 浜屽弶鏍戠殑鏈€澶ф繁搴?- 閫掑綊: max(maxDepth(left), maxDepth(right)) + 1
- BFS灞傚簭閬嶅巻: 姣忓眰璁℃暟

### 10. 楠岃瘉浜屽弶鎼滅储鏍?- 涓簭閬嶅巻搴斾负涓ユ牸閫掑搴忓垪
- 鎴栫敤鑼冨洿楠岃瘉: 姣忎釜鑺傜偣鍊煎湪(min, max)鍖洪棿鍐?
### 11. 浜屽弶鏍戠殑灞傚簭閬嶅巻
- BFS闃熷垪: 姣忓眰鍏堣褰曢槦鍒楅暱搴evel_size, 寰幆level_size娆?
### 12. 鏈€杩戝叕鍏辩鍏?LCA)
- 閫掑綊: 鑻oot绛変簬p鎴杚鍒欒繑鍥瀝oot
- 鍒嗗埆鍦ㄥ乏鍙冲瓙鏍戞煡鎵? 鑻ヤ袱杈归兘鎵惧埌鈫抮oot鏄疞CA

## 鍥?### 13. 宀涘笨鏁伴噺
- DFS/BFS閬嶅巻, 姣忔壘鍒颁竴涓?1'璁℃暟+1骞舵饭娌℃暣涓矝灞?- O(m脳n)

### 14. 璇剧▼琛?鎷撴墤鎺掑簭)
- BFS(Kahn): 鍏ュ害琛?闃熷垪, 涓嶆柇绉婚櫎鍏ュ害涓?鐨勮妭鐐?- 鏈€缁堣妭鐐规暟=鎬昏妭鐐规暟鈫掓棤鐜彲瀹屾垚

## 鍝堝笇琛?### 15. LRU缂撳瓨
- 鍝堝笇琛?鍙屽悜閾捐〃: 鍝堝笇琛∣(1)鏌ユ壘, 閾捐〃缁存姢璁块棶椤哄簭
- get: 绉诲埌閾捐〃澶撮儴; put: 鎻掑叆澶撮儴, 瓒呭閲忓垹灏鹃儴

---
*鏉ユ簮: LeetCode, 鍓戞寚Offer, 绠楁硶瀵艰*
"""
})

RESOURCES.append({
    "title": "鍔ㄦ€佽鍒掔粡鍏搁棶棰樼簿璁?,
    "description": "鍔ㄦ€佽鍒掓牳蹇冩€濇兂涓?0閬撶粡鍏镐緥棰樿瑙ｏ紝鍚?-1鑳屽寘銆丩CS銆佺紪杈戣窛绂汇€佺‖甯佹壘闆躲€佺煩闃甸摼涔樸€佹渶闀块€掑瀛愬簭鍒楃瓑銆?,
    "course": "绠楁硶璁捐涓庡垎鏋?, "chapter": "鍔ㄦ€佽鍒?, "difficulty": "ADVANCED",
    "type": "READING",
    "tags": ["鍔ㄦ€佽鍒?, "DP", "绠楁硶"],
    "source_url": "https://cp-algorithms.com/dynamic_programming/intro-to-dp.html",
    "content": """# 鍔ㄦ€佽鍒掔粡鍏搁棶棰樼簿璁?
## DP鏍稿績鎬濇兂
1. 鏈€浼樺瓙缁撴瀯: 闂鏈€浼樿В鍖呭惈瀛愰棶棰樻渶浼樿В
2. 閲嶅彔瀛愰棶棰? 瀛愰棶棰樿澶氭璁＄畻鈫掔紦瀛橀伩鍏嶉噸澶?3. 鐘舵€佸畾涔? 鐢ㄦ渶灏戠殑鍙橀噺鎻忚堪瀛愰棶棰?4. 鐘舵€佽浆绉? dp[curr]濡備綍浠巇p[prev]鎺ㄥ

## 渚嬮1: 0-1鑳屽寘
瀹归噺W, n涓墿鍝?閲嶉噺w[i], 浠峰€紇[i]), 姣忎欢閫夋垨涓嶉€夈€?```
dp[j] = max(dp[j], dp[j-w[i]] + v[i])  // j浠庡ぇ鍒板皬
```

## 渚嬮2: 瀹屽叏鑳屽寘
姣忎欢鐗╁搧鏃犻檺鍙栥€?```
dp[j] = max(dp[j], dp[j-w[i]] + v[i])  // j浠庡皬鍒板ぇ
```

## 渚嬮3: 鏈€闀垮叕鍏卞瓙搴忓垪(LCS)
```
if s1[i]==s2[j]:
    dp[i][j] = dp[i-1][j-1] + 1
else:
    dp[i][j] = max(dp[i-1][j], dp[i][j-1])
```

## 渚嬮4: 缂栬緫璺濈
灏唚ord1杞崲涓簑ord2鐨勬渶灏戞搷浣滄暟(鎻掑叆/鍒犻櫎/鏇挎崲)
```
if a[i]==b[j]: dp[i][j]=dp[i-1][j-1]
else: dp[i][j]=1+min(dp[i-1][j],dp[i][j-1],dp[i-1][j-1])
```

## 渚嬮5: 纭竵鎵鹃浂
```python
def coin_change(coins, amount):
    dp = [float('inf')] * (amount + 1)
    dp[0] = 0
    for c in coins:
        for j in range(c, amount + 1):
            dp[j] = min(dp[j], dp[j - c] + 1)
    return dp[amount] if dp[amount] != float('inf') else -1
```

## 渚嬮6: 鏈€闀块€掑瀛愬簭鍒?LIS)
- DP: dp[i]=max(dp[j])+1 (j<i, a[j]<a[i]), O(n虏)
- 璐績+浜屽垎: tails鏁扮粍, O(n log n)
```python
tails = []
for x in nums:
    i = bisect_left(tails, x)
    if i == len(tails): tails.append(x)
    else: tails[i] = x
```

## 渚嬮7: 鏈€澶у瓙鏁扮粍鍜?Kadane)
```python
cur = best = nums[0]
for x in nums[1:]:
    cur = max(x, cur + x)
    best = max(best, cur)
```

## 渚嬮8: 鎵撳鍔垗(House Robber)
```python
dp[i] = max(dp[i-1], dp[i-2] + nums[i])
# 鍘嬬缉: 鍙渶prev2, prev1涓や釜鍙橀噺
```

## 渚嬮9: 鐭╅樀閾句箻
鍖洪棿DP: dp[i][j]=min(dp[i][k]+dp[k+1][j]+p[i-1]p[k]p[j])

## 渚嬮10: 姝ｅ垯琛ㄨ揪寮忓尮閰?```python
# dp[i][j]: s[0:i]涓巔[0:j]鏄惁鍖归厤
if p[j-1]=='*':
    dp[i][j]=dp[i][j-2] or (match(s[i-1],p[j-2]) and dp[i-1][j])
elif match(s[i-1],p[j-1]):
    dp[i][j]=dp[i-1][j-1]
```

## DP瑙ｉ蹇冩硶
1. 鍏堟兂鏆村姏閫掑綊(鑷《鍚戜笅)
2. 璇嗗埆閲嶅彔瀛愰棶棰樷啋鍔犺蹇嗗寲
3. 杞寲涓鸿嚜搴曞悜涓婇€掓帹
4. 浼樺寲绌洪棿(婊氬姩鏁扮粍)

---
*鏉ユ簮: Introduction to Algorithms (CLRS), LeetCode, Codeforces*
"""
})

# 鈹€鈹€ Mind Maps / Knowledge Graphs 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€
RESOURCES.append({
    "title": "鎿嶄綔绯荤粺鐭ヨ瘑浣撶郴鎬濈淮瀵煎浘",
    "description": "鎿嶄綔绯荤粺鏍稿績鐭ヨ瘑浣撶郴鐨勭粨鏋勫寲鎬濈淮瀵煎浘锛屾兜鐩栬繘绋嬬鐞嗐€佸唴瀛樼鐞嗐€佹枃浠剁郴缁熴€両O绯荤粺銆佹閿併€佽櫄鎷熷寲鍏ぇ閮ㄥ垎銆?,
    "course": "鎿嶄綔绯荤粺", "chapter": "缁艰堪", "difficulty": "BASIC",
    "type": "MINDMAP",
    "tags": ["鎿嶄綔绯荤粺", "鎬濈淮瀵煎浘", "鐭ヨ瘑浣撶郴"],
    "source_url": "https://pages.cs.wisc.edu/~remzi/OSTEP/",
    "content": """# 鎿嶄綔绯荤粺鐭ヨ瘑浣撶郴鎬濈淮瀵煎浘

## 涓€銆佽繘绋嬬鐞?(Process Management)
- 杩涚▼姒傚康
  - 杩涚▼vs绾跨▼vs鍗忕▼
  - PCB (杩涚▼鎺у埗鍧?
  - 杩涚▼鐘舵€?(鍒涘缓/灏辩华/杩愯/闃诲/缁堟)
  - 涓婁笅鏂囧垏鎹?- 杩涚▼璋冨害
  - FCFS / SJF / 浼樺厛绾?/ RR
  - MLFQ (澶氱骇鍙嶉闃熷垪)
  - CFS (瀹屽叏鍏钩璋冨害)
  - 瀹炴椂璋冨害 RMS / EDF
- 鍚屾涓庝簰鏂?  - 涓寸晫鍖洪棶棰?  - 淇″彿閲?/ 浜掓枼閿?/ 鑷棆閿?/ RCU
  - 缁忓吀闂: 鐢熶骇鑰呮秷璐硅€?/ 璇昏€呭啓鑰?/ 鍝插瀹跺氨椁?- 姝婚攣
  - 鍥涗釜蹇呰鏉′欢
  - 姝婚攣棰勯槻 vs 姝婚攣閬垮厤(閾惰瀹剁畻娉? vs 姝婚攣妫€娴?- 绾跨▼
  - 鐢ㄦ埛绾х嚎绋?vs 鍐呮牳绾х嚎绋?  - 绾跨▼姹?  - 澶氱嚎绋嬫ā鍨?
## 浜屻€佸唴瀛樼鐞?(Memory Management)
- 鍐呭瓨鍒嗛厤
  - 杩炵画鍒嗛厤(棣栨/鏈€浣?鏈€宸€傞厤) + 澶栭儴纰庣墖
  - 鍒嗛〉(椤佃〃 + TLB + 澶氱骇椤佃〃)
  - 鍒嗘
  - 娈甸〉寮?- 铏氭嫙鍐呭瓨
  - 鎸夐渶璋冮〉 + 缂洪〉涓柇
  - 椤甸潰缃崲: OPT / LRU / CLOCK / 鏀硅繘CLOCK
  - 宸ヤ綔闆嗘ā鍨?/ 鎶栧姩鐨勯伩鍏?  - 鍐欐椂澶嶅埗(COW)
- 鍐呭瓨鏄犲皠mmap
- Buddy System + Slab鍒嗛厤鍣?- NUMA鏋舵瀯

## 涓夈€佹枃浠剁郴缁?(File System)
- 鏂囦欢姒傚康(inode / 鐩綍 / 纭?杞摼鎺?
- 鏂囦欢鍒嗛厤鏂瑰紡(杩炵画/閾炬帴/绱㈠紩)
- 绌洪棽绌洪棿绠＄悊(浣嶅浘/閾捐〃)
- 鐩綍瀹炵幇
- 鏃ュ織鏂囦欢绯荤粺(Journaling / ext4)
- COW鏂囦欢绯荤粺(ZFS / Btrfs)
- 纾佺洏璋冨害(FCFS/SSTF/SCAN/C-SCAN)

## 鍥涖€両O绯荤粺 (IO Systems)
- IO纭欢(璁惧鎺у埗鍣?+ DMA)
- 涓柇澶勭悊(椤跺崐閮?搴曞崐閮?
- IO澶氳矾澶嶇敤: select / poll / epoll / io_uring
- 闃诲IO vs 闈為樆濉濱O vs 寮傛IO
- 闆舵嫹璐?sendfile / splice)
- 鐢ㄦ埛鎬両O(SPDK/DPDK)

## 浜斻€佽櫄鎷熷寲涓庡鍣?- Hypervisor (Type-1 vs Type-2)
- KVM / QEMU
- Cgroups + Namespaces 鈫?Docker
- 瀹瑰櫒 vs VM瀵规瘮

## 鍏€佹搷浣滅郴缁熺粨鏋?- 瀹忓唴鏍?vs 寰唴鏍?vs 娣峰悎鍐呮牳
- 绯荤粺璋冪敤鏈哄埗
- 鍐呮牳鎬?vs 鐢ㄦ埛鎬?
---
*鏉ユ簮: Operating System Concepts 10th Ed. (Silberschatz), OSTEP (Arpaci-Dusseau), Linux鍐呮牳鏂囨。*
"""
})

RESOURCES.append({
    "title": "璁＄畻鏈虹綉缁滃崗璁爤鎬濈淮瀵煎浘",
    "description": "璁＄畻鏈虹綉缁淭CP/IP浜斿眰鍗忚鏍堢殑缁撴瀯鍖栨€濈淮瀵煎浘锛屾兜鐩栧簲鐢ㄥ眰銆佷紶杈撳眰銆佺綉缁滃眰銆佹暟鎹摼璺眰銆佺墿鐞嗗眰鐨勬牳蹇冨崗璁笌姒傚康銆?,
    "course": "璁＄畻鏈虹綉缁?, "chapter": "缁艰堪", "difficulty": "BASIC",
    "type": "MINDMAP",
    "tags": ["璁＄畻鏈虹綉缁?, "鎬濈淮瀵煎浘", "TCP/IP", "鍗忚鏍?],
    "source_url": "https://www.rfc-editor.org/",
    "content": """# 璁＄畻鏈虹綉缁淭CP/IP鍗忚鏍堟€濈淮瀵煎浘

## 涓€銆佸簲鐢ㄥ眰 (Application Layer)
- HTTP/HTTPS
  - 鏃犵姸鎬? 璇锋眰-鍝嶅簲妯″瀷
  - HTTP/1.1 (鎸佷箙杩炴帴, 绠＄嚎鍖?
  - HTTP/2 (澶氳矾澶嶇敤, 鏈嶅姟鍣ㄦ帹閫? HPACK)
  - HTTP/3 (QUIC, 0-RTT, 娑堥櫎HOL闃诲)
  - HTTPS = HTTP + TLS 1.3
- DNS
  - 閫掑綊鏌ヨ vs 杩唬鏌ヨ
  - 鏍?TLD/鏉冨▉鏈嶅姟鍣?  - DNS over HTTPS/TLS
- 鐢靛瓙閭欢: SMTP/POP3/IMAP
- 鏂囦欢浼犺緭: FTP/SFTP
- WebSocket (鍏ㄥ弻宸?
- CDN (杈圭紭缂撳瓨)

## 浜屻€佷紶杈撳眰 (Transport Layer)
- TCP
  - 涓夋鎻℃墜 / 鍥涙鎸ユ墜
  - 婊戝姩绐楀彛 + 娴侀噺鎺у埗
  - 鎷ュ鎺у埗: Tahoe鈫扲eno鈫扖UBIC鈫払BR
  - 澶撮儴鏍煎紡 (20+閫夐」瀛楄妭)
- UDP
  - 鏃犺繛鎺? 鏃犳祦鎺? 鏃犳嫢濉炴帶鍒?  - 閫傜敤: DNS, 瀹炴椂闊宠棰? 娓告垙
- QUIC (鍩轰簬UDP)
  - 0-RTT / 澶氳矾澶嶇敤鏃燞OL / 杩炴帴杩佺Щ

## 涓夈€佺綉缁滃眰 (Network Layer)
- IPv4
  - 32浣嶅湴鍧€, 鍒嗙墖
  - CIDR, NAT
- IPv6
  - 128浣嶅湴鍧€, 鏃犲箍鎾?澶氭挱鏇夸唬)
- 璺敱鍗忚
  - IGP: RIP(璺濈鍚戦噺), OSPF(閾捐矾鐘舵€?
  - EGP: BGP(璺緞鍚戦噺, 浜掕仈缃戞牳蹇?
- ICMP (ping, traceroute)
- ARP (IP鈫扢AC鏄犲皠)

## 鍥涖€佹暟鎹摼璺眰 (Data Link Layer)
- 浠ュお缃?(MAC鍦板潃, CSMA/CD)
- 浜ゆ崲鏈哄伐浣滃師鐞?(MAC琛ㄥ涔?
- VLAN (802.1Q)
- PPP / HDLC
- 宸敊妫€娴? CRC, 濂囧伓鏍￠獙

## 浜斻€佺墿鐞嗗眰 (Physical Layer)
- 浼犺緭浠嬭川: 鍙岀粸绾? 鍏夌氦, 鏃犵嚎
- 缂栫爜鏂规: NRZ, 鏇煎交鏂壒缂栫爜
- 甯﹀ vs 鍚炲悙閲?vs 寤惰繜
- 鐗╃悊鎷撴墤: 鎬荤嚎/鏄熷瀷/鐜?缃戠姸

## 鍏抽敭浜ゅ弶姒傚康
- 瀹夊叏: TLS/SSL, VPN(IPSec), 闃茬伀澧?- QoS: DiffServ, IntServ
- 鎬ц兘: 寤惰繜=澶勭悊+鎺掗槦+浼犺緭+浼犳挱, BDP=甯﹀脳RTT

---
*鏉ユ簮: Computer Networking: A Top-Down Approach (Kurose & Ross), RFC documents*
"""
})

# 鈹€鈹€ SQL / Database 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€
RESOURCES.append({
    "title": "SQL鏌ヨ浼樺寲瀹炴垬鎸囧崡",
    "description": "SQL鏌ヨ浼樺寲鏍稿績鎶€宸т笌瀹炴垬妗堜緥锛屾兜鐩栫储寮曚娇鐢ㄣ€丒XPLAIN鍒嗘瀽銆丣OIN浼樺寲銆佸瓙鏌ヨ鏀瑰啓銆佹參鏌ヨ璇婃柇銆?,
    "course": "鏁版嵁搴撳師鐞?, "chapter": "鏌ヨ浼樺寲", "difficulty": "INTERMEDIATE",
    "type": "READING",
    "tags": ["SQL", "鏌ヨ浼樺寲", "绱㈠紩", "EXPLAIN"],
    "source_url": "https://www.postgresql.org/docs/current/performance-tips.html",
    "content": """# SQL鏌ヨ浼樺寲瀹炴垬鎸囧崡

## 1. 浣跨敤EXPLAIN鍒嗘瀽鎵ц璁″垝
```sql
EXPLAIN ANALYZE SELECT ...;
```
鍏虫敞: Seq Scan(鍏ㄨ〃鎵弿)鈫掗渶瑕佺储寮? 楂榬ows浼拌, 楂榓ctual time

## 2. 绱㈠紩浼樺寲
- WHERE鏉′欢鍒椼€丣OIN鍏宠仈鍒椼€丱RDER BY鍒楀缓绱㈠紩
- 澶嶅悎绱㈠紩鏈€宸﹀墠缂€鍘熷垯
- 瑕嗙洊绱㈠紩閬垮厤鍥炶〃
- 閬垮厤绱㈠紩鍒椾笂鐨勫嚱鏁板拰璁＄畻
```sql
-- BAD: 绱㈠紩澶辨晥
SELECT * FROM t WHERE DATE(create_time) = '2024-01-01';
-- GOOD:
SELECT * FROM t WHERE create_time >= '2024-01-01'
  AND create_time < '2024-01-02';
```

## 3. JOIN浼樺寲
- 灏忚〃椹卞姩澶ц〃(椹卞姩琛ㄦ斁鍦‵ROM鍚?
- 纭繚JOIN鍒楁湁绱㈠紩
- JOIN浠ｆ浛瀛愭煡璇?IN鈫扟OIN)
- 閬垮厤澶氳〃绗涘崱灏旂Н

## 4. LIMIT澶у亸绉婚噺浼樺寲
```sql
-- BAD: 鎵弿鍓?00000琛屽啀涓㈠純
SELECT * FROM t LIMIT 100000, 20;
-- GOOD: 娓告爣鍒嗛〉(闇€瑕佽嚜澧炰富閿?
SELECT * FROM t WHERE id > 100000 LIMIT 20;
```

## 5. 甯歌鍙嶆ā寮?- SELECT * (杩斿洖涓嶉渶瑕佺殑鍒?
- 鍦╓HERE涓娇鐢∣R (鐢║NION ALL鏇夸唬)
- 瀵瑰ぇ鏁版嵁閲忎娇鐢∟OT IN (鐢↙EFT JOIN ... IS NULL鏇夸唬)
- 闅愬紡绫诲瀷杞崲 (VARCHAR鍒椾笌鏁板瓧姣旇緝)

## 6. 鎵归噺鎿嶄綔
```sql
-- BAD: N娆″線杩?INSERT INTO t VALUES (1), (2), (3);
-- GOOD: 鎵归噺鎻掑叆
INSERT INTO t VALUES (1,'a'), (2,'b'), (3,'c');
-- 鎴栦娇鐢–OPY(PostgreSQL)
```

## 7. 缁熻淇℃伅鏇存柊
```sql
ANALYZE table_name;  -- 鏇存柊缁熻淇℃伅璁╀紭鍖栧櫒鍋氬嚭鏇村ソ鍐崇瓥
```

## 8. 鏁版嵁搴撻厤缃紭鍖?- shared_buffers: 鐗╃悊鍐呭瓨鐨?5%
- effective_cache_size: 鐗╃悊鍐呭瓨鐨?5%
- work_mem: 鎺掑簭/鍝堝笇鎿嶄綔鐨勫唴瀛?- maintenance_work_mem: VACUUM/CREATE INDEX鐨勫唴瀛?
---
*鏉ユ簮: PostgreSQL瀹樻柟鏂囨。, MySQL浼樺寲鎸囧崡, SQL Performance Explained (Winand)*
"""
})

# 鈹€鈹€ System Design 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€
RESOURCES.append({
    "title": "RESTful API璁捐鏈€浣冲疄璺垫竻鍗?,
    "description": "RESTful API璁捐鐨勫畬鏁存鏌ユ竻鍗曪紝娑电洊URL璁捐銆丠TTP鏂规硶銆佺姸鎬佺爜銆佸垎椤点€佺増鏈帶鍒躲€佽璇併€侀敊璇鐞嗙瓑銆?,
    "course": "杞欢宸ョ▼", "chapter": "API璁捐", "difficulty": "BASIC",
    "type": "READING",
    "tags": ["REST", "API", "璁捐瑙勮寖"],
    "source_url": "https://learn.microsoft.com/en-us/azure/architecture/best-practices/api-design",
    "content": """# RESTful API璁捐鏈€浣冲疄璺垫竻鍗?
## URL璁捐
- 浣跨敤鍚嶈瘝澶嶆暟: `/users`, `/articles`
- 灞傜骇鍏崇郴: `/users/{id}/orders`
- 閬垮厤鍔ㄨ瘝: 鐢℉TTP鏂规硶琛ㄨ揪鎿嶄綔
- 浣跨敤kebab-case: `/user-profiles`
- 涓嶄娇鐢ㄦ枃浠舵墿灞曞悕: `/users.json`鈫抈/users`

## HTTP鏂规硶瑙勮寖
- GET: 鑾峰彇璧勬簮(瀹夊叏, 骞傜瓑)
- POST: 鍒涘缓璧勬簮(闈炲箓绛?
- PUT: 瀹屾暣鏇挎崲(骞傜瓑)
- PATCH: 閮ㄥ垎鏇存柊(闈炲箓绛?
- DELETE: 鍒犻櫎(骞傜瓑)

## 鐘舵€佺爜浣跨敤
- 200 OK: 鎴愬姛(GET/PUT/PATCH)
- 201 Created: 鎴愬姛鍒涘缓(POST)
- 204 No Content: 鎴愬姛鍒犻櫎
- 400 Bad Request: 璇锋眰鍙傛暟閿欒
- 401 Unauthorized: 鏈璇?- 403 Forbidden: 宸茶璇佷絾鏃犳潈闄?- 404 Not Found: 璧勬簮涓嶅瓨鍦?- 409 Conflict: 璧勬簮鍐茬獊
- 422 Unprocessable Entity: 璇箟閿欒
- 429 Too Many Requests: 闄愭祦
- 500 Internal Server Error: 鏈嶅姟鍣ㄩ敊璇?
## 鍒嗛〉
```json
{
  "data": [...],
  "pagination": {
    "page": 2,
    "page_size": 20,
    "total_count": 150,
    "total_pages": 8
  },
  "links": {
    "self": "/users?page=2",
    "next": "/users?page=3",
    "prev": "/users?page=1"
  }
}
```

## 鐗堟湰鎺у埗
- URL鐗堟湰: `/v1/users` (鏈€甯哥敤)
- Header鐗堟湰: `Accept: application/vnd.api.v2+json`
- 鍚戝悗鍏煎浼樺厛

## 閿欒鍝嶅簲鏍煎紡
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid email format",
    "details": [
      {
        "field": "email",
        "reason": "Must be a valid email address"
      }
    ]
  }
}
```

## 璁よ瘉
- 浣跨敤Authorization澶? `Bearer <token>`
- OAuth 2.0 + OpenID Connect
- API Key鐢ㄤ簬鏈嶅姟闂撮€氫俊

## 杩囨护涓庢帓搴?- 杩囨护: `/users?role=admin&status=active`
- 鎺掑簭: `/users?sort=-created_at,+name`
- 瀛楁閫夋嫨: `/users?fields=id,name,email`
- 鎼滅储: `/users?q=john`

## 閫熺巼闄愬埗
- 鍝嶅簲澶? `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`
- 鍒嗙骇闄愬埗: 鍖垮悕/璁よ瘉/楂樼骇鐢ㄦ埛涓嶅悓闄愰

---
*鏉ユ簮: Microsoft REST API Guidelines, Google API Design Guide, JSON:API Specification*
"""
})

print(f"Defined {len(RESOURCES)} resources")

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


def upload_resource_file(client: Minio, bucket: str, resource: dict) -> tuple[str, int]:
    """Upload the actual .md content file to MinIO. Returns (object_key, size_bytes)."""
    safe_name = resource["title"].replace("/", "-").replace(" ", "_")
    object_key = f"resources/{safe_name}.md"
    content_bytes = resource["content"].encode("utf-8")
    data = BytesIO(content_bytes)
    md5 = hashlib.md5(content_bytes).hexdigest()
    client.put_object(bucket, object_key, data, len(content_bytes),
                       content_type="text/markdown")
    return object_key, len(content_bytes)


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
    print("Real Educational Resources 鈫?MinIO + PostgreSQL")
    print("=" * 60)

    if dry_run:
        print("\n[DRY RUN] Would create:")
        for r in RESOURCES:
            print(f"  [{r['type']:8s}] {r['title']}")
        return

    minio = connect_minio()
    ensure_bucket(minio, BUCKET)

    conn = connect_db()

    try:
        with conn:
            with conn.cursor() as cur:
                # Step 1: Upload to MinIO and create storage.resource_object
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
                    if (i + 1) % 5 == 0:
                        print(f"  MinIO upload [{i + 1}/{len(RESOURCES)}]")

                print(f"  Uploaded {len(RESOURCES)} .md files to MinIO")

                # Step 2: Create app.learning_resource entries
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

                # Step 3: Create rag.resource_document entries 鈥?embed the description
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

                # Step 4: Vectorize descriptions
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
        print(f"\nDone. {len(RESOURCES)} real resources imported with .md files in MinIO.")

    finally:
        conn.close()


if __name__ == "__main__":
    main()

