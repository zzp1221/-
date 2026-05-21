# 智学引擎部署指南

最后更新：2026-05-20

本文面向从代码仓库全新部署的同学。默认部署使用 Docker Compose，包含前端、Java 控制平面、Python Agent、PostgreSQL、MongoDB、Redis 六个服务。

> 当前联调/演示环境是热更新环境：只允许 `docker cp` 同步文件，禁止 `docker compose build`、`docker compose up --build`、`--force-recreate` 和重建容器。本文中的 build/recreate 命令只适用于全新部署、空环境初始化或明确维护窗口。

## 1. 环境要求

- Docker 24+
- Docker Compose v2.20+
- Git
- 至少一个 OpenAI-compatible LLM API Key
- 可选：Embedding API Key，用于向量检索；不配置时部分 RAG 能力会降级或失败

Java 后端镜像已改为 Docker 多阶段构建，不再要求宿主机预先安装 Maven 或手动生成 `target/*.jar`。

## 2. 拉取代码

```bash
git clone <repo-url> zhixue-engine
cd zhixue-engine
```

## 3. 配置环境变量

复制示例文件：

```bash
cp .env.example .env
```

Windows PowerShell 可用：

```powershell
Copy-Item .env.example .env
```

至少修改以下变量，不能保留占位值：

```env
POSTGRES_PASSWORD=replace-with-a-strong-postgres-password
APP_JWT_SECRET=replace-with-a-random-secret-at-least-32-bytes
PYTHON_AGENT_INTERNAL_TOKEN=replace-with-a-random-shared-internal-token
AI_OPENAI_COMPATIBLE_API_KEY=replace-with-openai-compatible-api-key
EMBEDDING_API_KEY=replace-with-embedding-api-key
```

生成本地随机值的例子：

```bash
openssl rand -base64 32
```

PowerShell 可用：

```powershell
[Convert]::ToBase64String((1..32 | ForEach-Object { Get-Random -Maximum 256 }))
```

说明：

- `APP_JWT_SECRET` 用于签发登录 JWT，至少 32 字节。
- `PYTHON_AGENT_INTERNAL_TOKEN` 是 Java 与 Python Agent 内部接口共享密钥，两个服务必须一致。
- `POSTGRES_PASSWORD` 首次启动后会写入 `./data/postgres`，后续修改需要同步修改数据库密码或清空数据目录重建。
- Postgres、Mongo、Redis 的宿主机端口默认只绑定 `127.0.0.1`，不会暴露到局域网。

## 4. 启动标准部署

```bash
docker compose up -d --build
```

该命令会构建镜像并创建容器；已有演示环境不要执行。

查看状态：

```bash
docker compose ps
```

预期服务：

- `zhixue-frontend`
- `zhixue-app`
- `zhixue-python-agent`
- `zhixue-postgres`
- `zhixue-mongo`
- `zhixue-redis`

首次启动会自动执行：

- `init.sql`：创建 PostgreSQL schema、表、索引、枚举和 RLS 策略
- `restore_vector_data.sh`：从 `vector_data.dump` 恢复预置向量数据
- `mongo-init.js`：初始化 MongoDB collection 和索引

## 5. 验证部署

```bash
curl -s http://localhost:8081/api/health
curl -s http://localhost:8000/health
curl -I http://localhost/
```

预期：

- Java `/api/health` 返回 `{"status":"UP"}`
- Python `/health` 返回 `status: ok`
- 前端首页 HTTP 200

浏览器访问：

```text
http://localhost/
```

## 6. 可选：本地 Judge 模型

本地主观题 Judge 使用 GGUF 模型，默认关闭，不影响标准部署。

准备模型：

```bash
mkdir -p models
# 将 judge_model.gguf 放到 ./models/judge_model.gguf
```

全新部署时启动 overlay：

```bash
docker compose -f docker-compose.yml -f docker-compose.local-judge.yml up -d --build
```

overlay 会强制：

```env
ENABLE_LOCAL_JUDGE=true
LOCAL_JUDGE_MODEL_PATH=/app/models/judge_model.gguf
UVICORN_WORKERS=1
```

单 worker 是为了避免多个 Uvicorn worker 重复加载 GGUF 模型。

## 7. 常用运维命令

```bash
docker compose logs -f
docker compose logs -f app
docker compose logs -f python-agent
docker compose restart app python-agent
```

当前热更新环境不要执行 `docker compose down`、`docker compose up --build` 或 `docker compose up --force-recreate`。如需同步代码：

```bash
# 前端：本地构建后覆盖 nginx 静态目录
cd frontend && npx tsc --noEmit && npx vite build
docker cp dist/. zhixue-frontend:/usr/share/nginx/html/
docker exec zhixue-frontend nginx -s reload

# Python：只复制改动的 .py/skill 文件到 /app 对应路径
docker cp python-agent/src/ai_modules/runtime/resource_bundle_workflow.py zhixue-python-agent:/app/src/ai_modules/runtime/resource_bundle_workflow.py
docker restart zhixue-python-agent

# Java：如确需更新后端，先本地打包，再覆盖 jar 并重启 app 容器
cd project && mvn.cmd -q -DskipTests package
docker cp target/zhixue-control-plane-0.0.1-SNAPSHOT.jar zhixue-app:/app/app.jar
docker restart zhixue-app
```

全新部署或维护窗口中，保留数据并重新应用端口绑定/环境变量可使用：

```bash
docker compose up -d --force-recreate
```

清空全部容器和数据卷/目录前请先备份，仅全新初始化或明确维护窗口使用：

```bash
docker compose down -v
```

本项目的数据主要落在：

```text
./data/postgres
./data/mongo
./data/redis
./data/logs
./data/sandbox-temp
```

## 8. 本地开发

只启动依赖服务：

```bash
docker compose up -d postgres mongo redis
```

前端：

```bash
cd frontend
pnpm install
pnpm dev
```

Java：

```bash
cd project
mvn spring-boot:run
```

Python Agent：

```bash
cd python-agent
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.template .env
uvicorn server:app --reload --port 8000
```

Windows 激活虚拟环境：

```powershell
.\.venv\Scripts\Activate.ps1
```

## 9. 故障排查

`POSTGRES_PASSWORD must be configured`：

- `.env` 不存在或未配置 `POSTGRES_PASSWORD`。
- 执行 `cp .env.example .env` 后填写真实强密码。

`APP_JWT_SECRET must be configured`：

- `.env` 未配置 JWT secret，或长度不足。
- 使用随机 32 字节以上字符串。

`PYTHON_AGENT_INTERNAL_TOKEN must be configured`：

- `.env` 缺少 Java/Python internal token。
- 标准部署只需要在根目录 `.env` 配置一次，Compose 会注入两个服务。

Python Agent 调 LLM 失败：

- 检查 `AI_OPENAI_COMPATIBLE_API_KEY` 和 `AI_OPENAI_COMPATIBLE_BASE_URL`。
- 如使用 DashScope embedding，检查 `EMBEDDING_API_KEY` 或 `DASHSCOPE_API_KEY`。

端口仍显示 `0.0.0.0:5432`：

- 说明容器是旧端口配置创建的。
- 当前热更新环境不要重建数据服务容器；记录风险并等待维护窗口。
- 维护窗口中可执行 `docker compose up -d --force-recreate postgres mongo redis` 重新创建数据服务容器。

## 10. 安全检查清单

- 不提交真实 `.env`。
- 不保留示例占位值或 `123456`。
- `APP_JWT_SECRET`、`PYTHON_AGENT_INTERNAL_TOKEN` 使用不同随机值。
- 生产环境只开放前端入口，Java/Python 端口按需限制来源。
- 数据库端口默认只绑定 `127.0.0.1`；如部署在服务器，仍建议使用防火墙限制。
