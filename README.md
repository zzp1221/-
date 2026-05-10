# 智学引擎 Zhixue Engine

基于大语言模型的多智能体个性化学习资源生成与学习系统。

## 核心功能

**智能辅导** — 15+ 专业 Agent 协同工作，支持多轮对话、SSE 流式逐字渲染、长会话记忆压缩

**RAG 知识检索** — 三通道混合检索（向量相似度 + 关键词匹配 + 知识图谱遍历），覆盖 14 门计算机学科、642+ 知识块，hits@3 ≥ 90%

**多格式资源生成** — 文档 / PPT / 阅读材料 / 思维导图 / 代码示例 / 数字人视频（6 种格式）

**学习画像** — 用户能力雷达图、薄弱点追踪，每次辅导/练习后自动更新

**学习路径规划** — 基于评估结果自动生成个性化学习计划

**练习与评测** — 自动出题、评分、反馈

## 技术架构

```
┌──────────────┐     ┌──────────────────┐     ┌──────────────────┐
│   Frontend   │────▶│   Java Backend   │────▶│  Python AI Agent │
│  React + Vite │     │  Spring Boot 3.3  │     │  FastAPI + LangGraph │
│  Port 80     │     │  Port 8081       │     │  Port 8000       │
└──────────────┘     └──────────────────┘     └──────────────────┘
                              │                         │
                    ┌─────────┼─────────┐       ┌──────┴──────┐
                    │         │         │       │  LLM Providers │
               PostgreSQL   MongoDB   Redis    │ DashScope /  │
               + pgvector   对话/消息  缓存     │ MiMo / Spark │
               Port 5432   Port 27017 Port 6379 └─────────────┘
```

| 层 | 技术栈 | 端口 |
|---|---|---|
| 前端 | TypeScript, React 18, Vite 5, Tailwind CSS 4, Nginx | 80 |
| 后端 | Java 21, Spring Boot 3.3, Spring Security (JWT), Maven | 8081 |
| AI Agent | Python 3.11, FastAPI, LangGraph, LangChain, DashScope | 8000 |
| 向量库 | PostgreSQL 16 + pgvector (1024 维 IVFFlat 索引) | 5432 |
| 文档库 | MongoDB 7 (对话历史、消息、流事件) | 27017 |
| 缓存 | Redis 7 (限流、幂等、缓存, AOF 持久化) | 6379 |

## 多智能体系统

系统通过 Supervisor 模式编排 15+ 专业 Agent，根据服务类型自动路由到对应的 Agent 链：

| 路由 | Agent 链 | 说明 |
|---|---|---|
| 智能辅导 | query_rewrite → retrieval → tutor → profile | 多轮对话辅导，自动更新画像 |
| 资源生成 | query_rewrite → retrieval → {生成 Agent} | 根据资源类型动态选择生成器 |
| 视频生成 | query_rewrite → retrieval → video_generator | 脚本生成 → TTS → 浏览器端 DH Live 渲染 |
| 练习评判 | practice → judge → profile | 自动出题、评分、反馈 |
| 路径规划 | path_planning | 基于评估生成学习计划 |
| 学习评估 | evaluation → path_planning | 综合评估 + 路径调整 |

支持 3 家 LLM 提供商，可按 Agent 组件独立配置模型：

- **DashScope / 百炼** — OpenAI 兼容接口
- **小米 MiMo** — 支持 PPTX 直出
- **讯飞星火**

## RAG 知识库

### 知识覆盖

14 门计算机学科，642+ 知识块：

信息安全、分布式系统、操作系统、数据库原理、数据结构、离散数学、程序设计、算法设计与分析、编译原理、计算机图形学、计算机组成原理、计算机网络、软件工程、视频资源

### 向量化流程

知识库采用两阶段离线导入流程：

```
wiki/*.md ──①──▶ rag.wiki_page ──②──▶ rag.knowledge_document + rag.knowledge_chunk
   │              (结构化存储)              (1024 维向量)
   │
   └── rag.wiki_link (知识图谱: WIKILINK / SHARED_TAG / SHARED_SOURCE)
```

**阶段一：结构化导入** (`python-agent/knowledge/import_wiki_to_db.py`)
- 解析 `wiki/` 目录下的 Markdown 文件（含 YAML frontmatter）
- 写入 `rag.wiki_page`（标题、正文、学科、难度、标签）
- 自动提取 `[[wikilink]]` 双链，构建 `rag.wiki_link` 知识图谱
- 同步填充 `rag.term_lexicon` 术语词典（用于关键词检索分词）

**阶段二：向量化** (`python-agent/knowledge/vectorize_wiki.py`)
- 从 `rag.wiki_page` 读取未向量化的页面
- 调用 DashScope `qwen3-vl-embedding` 模型生成 1024 维稠密向量
- 批量写入 `rag.knowledge_document` + `rag.knowledge_chunk`
- 每个 chunk 包含：content、embedding (VECTOR(1024))、domain、difficulty、quality_score

**预置数据**：`vector_data.dump`（9.6MB pg_dump）包含全部已向量化的知识块，首次启动时由 `restore_vector_data.sh` 自动恢复，无需重新调用 Embedding API。

### 检索架构

三通道混合检索 + RRF 融合排序：

```
用户查询
  │
  ├─ Channel A: GrepSearcher ─── 关键词匹配（FMM 分词 + 术语词典）
  │
  ├─ Channel B: VectorSearcher ─ 语义相似度（pgvector cosine, IVFFlat 索引）
  │   └── 同时搜索 knowledge_chunk + resource_chunk
  │
  ├─ Channel C: GraphExpander ── 知识图谱扩展（从 A/B 的 top 结果出发，沿 wiki_link 扩展）
  │
  └─ RRFFusion ─── 加权 RRF 融合，输出最终排序
```

### 向量存储表结构

| 表 | 用途 | 向量列 |
|---|---|---|
| `rag.knowledge_chunk` | 知识库 chunk（wiki 导入） | `embedding VECTOR(1024)` |
| `rag.resource_chunk` | 生成资源 chunk（运行时写入） | `embedding VECTOR(1024)` |
| `rag.user_profile_vector` | 用户学习画像向量 | `embedding VECTOR(1024)` |

三张表均使用 IVFFlat 索引（`vector_cosine_ops`, lists=100）加速近似最近邻搜索。

## 快速开始

### 环境要求

- Docker 24+ & Docker Compose v2.20+
- 至少一个 LLM API Key（DashScope / MiMo / Spark）

### Docker Compose 一键启动

```bash
# 1. 克隆并配置环境变量
git clone <repo-url> && cd <repo>
cp .env.example .env
# 编辑 .env，设置至少一个 LLM API Key

# 2. 构建 Java 后端
cd project && mvn package -DskipTests && cd ..

# 3. 启动全部服务
docker compose up -d --build

# 4. 等待健康检查通过（约 30-60 秒）
curl -s http://localhost:8081/actuator/health   # Java 后端
curl -s http://localhost:8000/health             # Python Agent
# 浏览器打开 http://localhost 访问前端
```

首次启动时，PostgreSQL 容器会自动执行：
1. `init.sql` — 建表、建索引、建枚举
2. `restore_vector_data.sh` — 从 `vector_data.dump` 恢复预置向量数据（642 知识块 + 资源 chunk）

### 本地开发

```bash
# 仅启动数据层
docker compose up -d postgres mongo redis

# 前端（热重载，端口 5173）
cd frontend && pnpm install && pnpm dev

# Java 后端
cd project && mvn spring-boot:run

# Python Agent
cd python-agent
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn server:app --host 0.0.0.0 --port 8000 --reload
```

### 重新向量化知识库

如需更新知识库内容后重新生成向量：

```bash
cd python-agent/knowledge

# 1. 导入 wiki markdown → PostgreSQL (rag.wiki_page)
python import_wiki_to_db.py

# 2. 生成 1024 维向量 → rag.knowledge_chunk
python vectorize_wiki.py

# 可选参数：
#   --dry-run     预览，不写入
#   --limit N     仅处理前 N 条
#   --incremental 增量模式，跳过已向量化页面
```

## 测试

```bash
# 端到端测试
pytest tests/ -v

# Python Agent 单元测试
cd python-agent && pytest tests/ -v

# Java 后端测试
cd project && mvn test

# 前端类型检查 + 构建
cd frontend && npx tsc --noEmit && npx vite build
```

## 项目结构

```
├── frontend/                # React 前端
│   └── src/
│       ├── api/             # API 调用 & SSE 客户端
│       ├── components/      # UI 组件 (MarkdownRenderer, MermaidDiagram, RadarChart, VideoCard...)
│       └── pages/           # 页面 (对话、智能引擎、学习工作室)
│
├── project/                 # Java Spring Boot 后端 (Clean Architecture)
│   └── src/main/java/com/project/
│       ├── api/             # REST 控制器
│       ├── application/     # 业务逻辑 (编排器, SSE emitter, 任务状态机, 限流, 幂等)
│       ├── domain/          # 实体与仓库 (User, Task, Conversation, Profile, Artifact)
│       └── infrastructure/  # HTTP 客户端 (Java → Python Agent 通信)
│
├── python-agent/            # Python AI Agent
│   ├── server.py            # FastAPI 入口 + SSE 流式端点
│   ├── src/ai_modules/
│   │   ├── agents/          # 15+ 专业 Agent (tutor, retrieval, generation, judge, profile...)
│   │   ├── llms/            # 多 LLM 提供商适配 (DashScope, MiMo, Spark)
│   │   ├── retrieval/       # 三通道混合检索 (vector + grep + graph + RRF)
│   │   ├── memory/          # 对话记忆 (摘要压缩) & 学习画像
│   │   ├── generation/      # 内容生成链 (6 种资源格式)
│   │   └── prompts/         # Agent 提示词模板
│   └── knowledge/           # 知识库导入 & 向量化脚本
│
├── wiki/                    # 知识库源文件 (14 门计算机学科 Markdown)
├── contracts/               # SSE 事件 JSON Schema 契约
├── migrations/              # 数据库迁移脚本
├── tests/                   # 端到端测试
├── docs/                    # 文档
├── docker-compose.yml       # 6 服务编排
├── init.sql                 # PostgreSQL 完整 DDL
└── vector_data.dump         # 预置向量数据 (pg_dump)
```

## 安全与可靠性

- **JWT 认证** — Access Token 2h / Refresh Token 7d
- **滑动窗口限流** — 按用户 + 按 IP 双维度
- **幂等控制** — Redis 幂等键，防止重复提交
- **内容安全审查** — SafetyAgent 对生成内容进行合规检查
- **SSE 任务取消** — 支持客户端主动取消长任务
- **沙箱文件清理** — 生成文件 2h TTL，30min 定时清扫

## 文档

- [部署指南](docs/DEPLOYMENT.md) — 完整的生产环境部署文档
- [实验日志](docs/experiment_log.md) — 改动记录与验证结果
- [SSE 事件协议](contracts/sse-events.schema.json) — 流式通信 JSON Schema
