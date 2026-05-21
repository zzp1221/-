# 智学引擎 ZhiXue Engine

基于大语言模型的多智能体个性化学习资源生成与学习系统。

## 核心功能

**智能辅导** — 17 个注册 Agent 协同工作，支持多轮对话、SSE 流式逐字渲染、图片上传分析、深度推理模式、长会话记忆压缩

**RAG 知识检索** — 四通道混合检索（短语优先 grep + 向量语义 + 知识图谱遍历 + 可选联网搜索），覆盖 20 门计算机学科、986+ 知识块，hits@3 100%

**多格式资源生成** — 文档 / 思维导图 / 幻灯片(PPTX) / 代码示例 / 练习题 / 数字人视频（6 种格式可多选），LangGraph ResourceBundle 编排

**学习画像** — 6 维度能力雷达图、薄弱点追踪、行为趋势分析，每次辅导/练习/评测后自动更新

**学习路径规划** — 基于评估结果自动生成个性化学习计划

**练习与评测** — 自动出题、评分、反馈，客观题字符串比对 + 主观题可选本地 GGUF 模型评分

**错题本** — SM-2 间隔重复算法驱动的错题管理与复习调度，数据库触发器自动收录错题

## 技术架构

```
                              ┌──────────────────────────┐
                              │       用户浏览器             │
                              │   React 18 + TypeScript    │
                              │   + Tailwind CSS 4         │
                              └──────────┬───────────────┘
                                         │ HTTP / SSE (流式)
                              ┌──────────┴───────────────┐
                              │    Nginx (反向代理 + SPA)   │
                              │    Port 80                │
                              └──────────┬───────────────┘
                                         │
            ┌────────────────────────────┼────────────────────────────┐
            │                            │                            │
            ▼                            ▼                            ▼
┌───────────────────────┐  ┌───────────────────────┐  ┌───────────────────────┐
│    Java Backend (BFF)  │  │   Python AI Agent     │  │       数据层            │
│    Spring Boot 3.3     │  │   FastAPI + SSE       │  │                       │
│    Port 8081           │  │   Port 8000           │  │ PostgreSQL 16+pgvector │
│                        │  │                       │  │ Port 5432              │
│  ┌──────────────────┐  │  │  ┌─────────────────┐  │  │                       │
│  │ 六边形架构        │  │  │  │ Supervisor 编排  │  │  │ MongoDB 7             │
│  │ JWT 认证/鉴权     │  │  │  │ 17 Agent 注册表  │  │  │ Port 27017            │
│  │ 任务编排/状态机   │  │  │  │ RAG 四通道检索   │  │  │                       │
│  │ SSE 代理/幂等     │  │  │  │ LLM 多Provider   │  │  │ Redis 7               │
│  │ 限流/审计/错题本  │  │  │  │ 资源生成流水线   │  │  │ Port 6379             │
│  └──────────────────┘  │  │  │  │ Agent 运行时内核 │  │  │                       │
│                        │  │  │  └─────────────────┘  │  │                       │
└───────────┬────────────┘  └───────────┬───────────────┘  └───────────────────────┘
            │                           │
            └───────────┬───────────────┘
                        │ X-Zhixue-Internal-Token (内部通信)
                        │ Redis Streams (SmartEngine 任务队列)
```

| 层 | 技术栈 | 端口 |
|---|---|---|
| 前端 | TypeScript, React 18, Vite 5, Tailwind CSS 4, Nginx | 80 |
| 后端 BFF | Java 21, Spring Boot 3.3, Spring Security (JWT), Maven | 8081 |
| AI Agent | Python 3.11, FastAPI, LangChain/LangGraph, SSE-Starlette | 8000 |
| 向量库 | PostgreSQL 16 + pgvector (1024 维 IVFFlat 索引) | 5432 |
| 文档库 | MongoDB 7 (对话历史、消息、流事件) | 27017 |
| 缓存 | Redis 7 Alpine (限流、幂等、缓存, AOF 持久化) | 6379 |

> 详细架构设计见 [系统架构文档](docs/architecture.md)

## 多智能体系统

系统通过 Supervisor 模式编排 17 个注册 Agent，根据服务类型自动路由到对应的 Agent 链：

| 服务类型 | Agent 链 | 说明 |
|---|---|---|
| 智能辅导 (TUTORING) | query_rewrite → retrieval → [image_analysis] → [tutor \| deep_reasoning] → profile | QueryClassifier 动态选择：寒暄短路 / 普通辅导 / 深度推理 |
| 深度推理 | query_rewrite → retrieval → image_analysis → deep_reasoning → profile | 四步推理：分析→推理→自审→最终回答 |
| 资源生成 | query_rewrite → retrieval → resource_bundle | LangGraph 并发 fan-out 生成多资源，统一 provenance、质量与安全闸门 |
| 视频生成 | query_rewrite → retrieval → video_generator | 脚本 → TTS → 浏览器端 DH Live WASM 渲染 |
| 练习评判 | practice → judge → profile | 自动出题、评分、反馈，错题触发器自动收录错题本 |
| 路径规划 | path_planning | 基于画像生成个性化学习计划 |
| 学习评测 | evaluation | 4 维度交互式评估 |
| 画像构建 | tutor → profile | 从对话/练习/评测信号构建多维度画像 |
| 资源推送 | resource_push | 匹配已有学习资源 + Tavily 搜索 |

支持 3 家 LLM 提供商，**14 个 Agent 组件可独立配置模型**：

| Provider | 厂商 | 主模型 | 说明 |
|----------|------|--------|------|
| OpenAI Compatible | 阿里云百炼 / DeepSeek | qwen3.6-plus | 默认，支持 Embedding |
| MiMo | 小米 | mimo-v2-omni | 支持 PPTX 直出 |
| Spark | 讯飞 | 4.0Ultra | 兼容接口 |

## Agent 运行时内核

本项目的 Agent 运行时内核 (`python-agent/src/ai_modules/runtime/`) 在架构理念上参考了 Claude Code 的 Agent 执行机制：

| 智学引擎模块 | 职责 | 设计思路 |
|---|---|---|
| `AgentCoreLoop` | LLM 推理 → 工具调用 → 结果注入 → 再推理 | 最多 4 轮迭代，无 tool_calls 则输出最终答案 |
| `ToolRegistry` | 按 name 注册工具，生成 OpenAI function-calling schema | 按 agent_level 过滤可见工具集 |
| `HookChain` | 工具执行前后的拦截链 | 可修改输入参数、拒绝执行、校验输出结果 |
| `PermissionPolicy` | allow/deny 规则匹配 + 数值级别检查 | READ_ONLY → FULL_ACCESS 四级权限 |
| `ConversationCompactor` | Token 预算估计 + 对话摘要 + 保留最近 N 轮 | 1200 token 预算，解决长会话上下文窗口问题 |
| `ContextSnapshot` | 聚合用户画像、学习进度、知识薄弱点 | 注入 Agent prompt 作为运行时上下文 |
| `RecoveryEngine` | 按 failure_type 分类重试 + 降级 | Timeout 1次, RateLimit 2次, Retrieval 1次 |

**独创机制**:

- **KnowledgeGuardHook**: 拦截所有 `generate_*` 工具调用，自动检索知识依据；无证据则拒绝生成，从源头防止 LLM 幻觉
- **ResourceBundleWorkflow**: LangGraph StateGraph 编排 6 种资源类型的并发 fan-out 生成，统一 provenance gate 和 quality gate
- **Skill 系统** (参考 [sanyuan-skills](https://github.com/sanyuan0704/sanyuan-skills)): Agent prompt 通过 `skills/{agent}/SKILL.md` 文件管理 (YAML frontmatter + Markdown body)，运行时注入 `{{snapshot_context}}` 学生画像上下文
- **QueryClassifier 动态路由**: 4 种输入模式 (寒暄/承接/明确问题/模糊话题) 自动分类，寒暄短路回复不消耗 LLM

## RAG 知识库

### 知识覆盖

20 门计算机学科，986+ 知识块：

操作系统、数据结构、计算机网络、计算机组成原理、编译原理、数据库原理、软件工程、算法设计与分析、程序设计、离散数学、人工智能、机器学习、信息安全、分布式系统、计算机图形学、C语言深入、Go语言、Rust语言、Java深入、JavaScript/TypeScript、Python深入、程序设计语言原理

### 向量化流程

```
wiki/*.md ──①──▶ rag.wiki_page ──②──▶ rag.knowledge_document + rag.knowledge_chunk
   │              (结构化存储)              (1024 维向量 + IVFFlat 索引)
   │
   └── rag.wiki_link (知识图谱: WIKILINK / SHARED_TAG / SHARED_SOURCE / COMMUNITY)
```

**阶段一：结构化导入** (`python-agent/knowledge/import_wiki_to_db.py`)
- 解析 Markdown（含 YAML frontmatter），写入 `rag.wiki_page`
- 自动提取 `[[wikilink]]` 双链，构建 `rag.wiki_link` 知识图谱
- 同步填充 `rag.term_lexicon` 术语词典（用于 FMM 分词）

**阶段二：向量化** (`python-agent/knowledge/vectorize_wiki.py`)
- 向量化知识文档**标题**（title embeddings 远优于 content embeddings）
- DashScope `qwen3-vl-embedding` → 1024 维稠密向量
- 批量写入 `rag.knowledge_document` + `rag.knowledge_chunk`

**预置数据**: `vector_data.dump` (~11.5MB pg_dump) 首次启动自动恢复，无需重新调用 Embedding API

### 检索架构

四通道混合检索 + RRF 融合排序（参考 [Karpathy LLM Wiki 方法论与三通道混合检索实践](https://www.cnblogs.com/jtuki/p/19861920)）：

```
用户查询
  │
  ├─ FMM 分词 (rag.term_lexicon 术语词典)
  │
  ├─ Channel A: GrepSearcher ─── 权重 3.0 ─── 短语优先匹配 → FMM术语 → Token回退
  │   └── 同义词扩展 (rag.synonym_group)
  │
  ├─ Channel B: VectorSearcher ── 权重 5.0 ─── pgvector cosine 相似度 (IVFFlat)
  │   └── 同时搜索 knowledge_chunk + resource_chunk
  │
  ├─ Channel C: GraphExpander ─── 权重 0.5 ─── 从 top 结果出发沿 wiki_link 扩展 1-hop
  │
  ├─ Channel D: TavilySearcher ── 权重 1.5 ─── 可选联网搜索
  │
  └─ 加权 RRF 融合 ─── k=60, 词组匹配 1.5x priority boost
```

> 核心发现：在中文技术术语检索中，字面匹配 (grep) 优于语义相似度 (向量)。

## 本地 Judge 模型

Judge Agent 的客观题判分已改为字符串比对（零 LLM 调用），主观题评估支持本地 GGUF 模型：

| 项目 | 值 |
|------|-----|
| 基座模型 | Qwen3-0.6B |
| 训练数据 | Wiki 知识点 × 3 种答案变体 |
| 训练方式 | SFT (1495 样本) + GRPO (200 组) |
| 模型格式 | GGUF Q8_0 |
| 模型大小 | 610MB |
| 推理引擎 | llama-cpp-python |
| 推理速度 | ~3s/次（CPU） |
| Docker 启用方式 | 叠加 `docker-compose.local-judge.yml` |
| 模型放置路径 | `./models/judge_model.gguf` |

本地 Judge 是可选部署，不会影响默认云端 API 部署路径：

```bash
mkdir -p models
# 将 judge_model.gguf 放到 ./models/judge_model.gguf

docker compose -f docker-compose.yml -f docker-compose.local-judge.yml up -d --build
```

> 当前联调/演示环境禁止重建容器；已有容器切换本地 Judge 需要单独安排维护窗口。

## 快速开始

### 环境要求

- Docker 24+ & Docker Compose v2.20+
- 至少一个 LLM API Key（OpenAI 兼容格式）

完整部署步骤见 [部署指南](docs/deployment.md)。Java 后端镜像会在 Docker 构建阶段自动编译，不需要先在宿主机执行 Maven 打包。

### Docker Compose 一键启动

```bash
# 1. 克隆并配置环境变量
git clone <repo-url> && cd zhixue-engine
cp .env.example .env
# 编辑 .env，至少设置 POSTGRES_PASSWORD、APP_JWT_SECRET、PYTHON_AGENT_INTERNAL_TOKEN 和一个 LLM API Key

# 2. 启动全部服务
docker compose up -d --build

# 3. 等待健康检查通过（约 30-60 秒）
curl -s http://localhost:8081/actuator/health   # Java 后端
curl -s http://localhost:8000/health             # Python Agent
# 浏览器打开 http://localhost 访问前端
```

首次启动时，PostgreSQL 容器自动执行：
1. `init.sql` — 建表、建索引、建枚举、RLS（3 个 Schema, 25+ 表）
2. `restore_vector_data.sh` — 从 `vector_data.dump` 恢复预置向量数据

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
├── frontend/                    # React 前端
│   ├── Dockerfile               # 多阶段构建 (node:20-alpine → nginx:1.27-alpine)
│   ├── nginx.conf               # SPA 路由 + API 代理 + SSE 透传 (30min 长连接)
│   ├── public/dh_live/          # DH Live WASM SDK (浏览器端数字人渲染)
│   └── src/
│       ├── api/                 # API 调用 & SSE 流式客户端
│       ├── components/          # UI 组件 (MarkdownRenderer, MermaidDiagram, RadarChart...)
│       └── pages/               # 页面 (Q&A对话、引擎服务、错题本、学习画像)
│
├── project/                     # Java Spring Boot 后端 (六边形架构)
│   ├── Dockerfile               # 多阶段构建 (Maven + Eclipse Temurin 21)
│   └── src/main/java/com/project/
│       ├── api/                 # REST 控制器 (Auth, Conversation, SmartEngine, Profile, Artifact, Mistake)
│       ├── application/         # 业务逻辑 (编排器, SSE emitter, 任务状态机, 限流, 幂等, SM-2)
│       ├── domain/              # 实体与 Repository (User, Task, Conversation, Profile, Artifact, Audit)
│       ├── infrastructure/      # HTTP 客户端 (Java → Python Agent 通信)
│       └── security/            # JWT 认证, 内部 Token 验证
│
├── python-agent/                # Python AI Agent (Supervisor 模式)
│   ├── server.py                # FastAPI 入口 + SSE 流式端点 + Lifespan 管理
│   ├── src/ai_modules/
│   │   ├── supervisor.py        # Agent 编排器 (路由解析 → Agent 链执行)
│   │   ├── agents/              # 17 个注册 Agent
│   │   ├── runtime/             # Agent 运行时内核
│   │   │   ├── agent_core_loop.py           # 工具调用执行循环
│   │   │   ├── tool_registry.py             # 工具注册表
│   │   │   ├── hook_chain.py                # 前置/后置钩子链
│   │   │   ├── hooks/knowledge_guard.py     # 知识守卫钩子 (幻觉防护)
│   │   │   ├── permission_policy.py         # 权限策略
│   │   │   ├── context_snapshot.py          # 上下文快照
│   │   │   ├── conversation_compactor.py    # 对话压缩器
│   │   │   ├── recovery_engine.py           # 故障恢复引擎
│   │   │   └── resource_bundle_workflow.py  # LangGraph 多资源生成编排
│   │   ├── retrieval/           # 四通道混合检索 (grep + vector + graph + web + RRF)
│   │   ├── llms/                # 多 LLM 提供商适配 + 本地 GGUF 评估器
│   │   ├── memory/              # 对话记忆 & 学习画像
│   │   ├── generation/          # 内容生成链 (资源正文与文件产物)
│   │   └── prompts/             # Agent 提示词模板
│   ├── skills/                  # Agent Skill 定义 (SKILL.md, 参考 sanyuan-skills)
│   ├── knowledge/               # 知识库导入 & 向量化脚本
│   ├── retrieval/               # 检索模块 (grep/vector/graph/RRF)
│   ├── recommendation/          # 学习资源推荐引擎
│   └── scripts/                 # 训练数据生成 & 模型训练脚本
│
├── wiki/                        # 知识库源文件 (20 门计算机学科, 986+ 知识块)
├── contracts/                   # SSE 事件 JSON Schema 契约
├── migrations/                  # 数据库迁移脚本
├── docs/                        # 文档 (架构文档、部署文档、技术报告、实验日志)
├── tests/                       # 端到端测试
├── docker-compose.yml           # 6 服务编排
├── docker-compose.local-judge.yml # 可选本地 GGUF Judge overlay
├── init.sql                     # PostgreSQL 完整 DDL (3 Schema, 25+ 表, RLS, pgvector 索引)
└── vector_data.dump             # 预置向量数据 (pg_dump, ~11.5MB)
```

## 安全与可靠性

- **JWT 认证** — Access Token 2h / Refresh Token 7d, HMAC-SHA256
- **滑动窗口限流** — 按用户 (60 req/min) + 按 IP (100 req/min) 双层 Redis Lua
- **幂等控制** — Idempotency-Key (Redis SETNX, 24h TTL)，防止重复提交
- **内容安全审查** — SafetyAgent 对生成内容进行合规检查
- **幻觉防护** — KnowledgeGuardHook 生成前强制检索知识依据
- **SSE 任务取消** — Redis + 文件系统双通道取消标记，支持跨 Worker
- **沙箱文件清理** — 生成文件 2h TTL，30min 定时清扫
- **RLS 行级安全** — PostgreSQL 24 张表启用三级访问控制 (GLOBAL/USER/COURSE)
- **内部通信保护** — X-Zhixue-Internal-Token (timing-safe 比较)
- **Redis 降级** — 限流/幂等/缓存在 Redis 不可用时自动切换到 InMemory 实现

## 参考资料

本项目在设计与实现过程中参考了以下开源项目和技术文章：

| 参考来源 | 本项目对应模块 |
|----------|----------------|
| [用 Karpathy LLM Wiki 方法论，为 AI Agent 系统构建结构化知识层](https://www.cnblogs.com/jtuki/p/19861920) | RAG 四通道混合检索架构、RRF 融合权重设计、FMM 分词策略 |
| [sanyuan-skills (Claude Code 自定义技能)](https://github.com/sanyuan0704/sanyuan-skills) | Agent Skill 系统 (SKILL.md 文件格式、prompt 工程化管理) |
| [DH_live (浏览器端数字人)](https://github.com/kleinlee/DH_live) | 浏览器端 DH Live WASM 视频渲染、postMessage 通信协议 |
| Claude Code Agent 运行时架构 | AgentCoreLoop、ToolRegistry、HookChain、PermissionPolicy、RecoveryEngine |

> 详细参考说明见 [项目技术报告](docs/teacher_guide.md) 开头的"参考资料与设计来源"章节。完整架构设计见 [系统架构文档](docs/architecture.md)。

## 开源许可

本项目使用了 [DH_live](https://github.com/kleinlee/DH_live) 开源项目，该项目基于 [MIT License](https://opensource.org/licenses/MIT) 许可。
