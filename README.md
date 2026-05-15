# 智学引擎 Zhixue Engine

基于大语言模型的多智能体个性化学习资源生成与学习系统。

## 核心功能

**智能辅导** — 16 个专业 Agent 协同工作，支持多轮对话、SSE 流式逐字渲染、长会话记忆压缩

**RAG 知识检索** — 三通道混合检索（短语优先 grep + 向量语义 + 知识图谱遍历），覆盖 20 门计算机学科、986+ 知识块，hits@3 100%

**多格式资源生成** — 文档 / 课件 / 阅读材料 / 思维导图 / 代码示例 / 数字人视频（6 种格式）

**学习画像** — 用户能力雷达图、薄弱点追踪，每次辅导/练习后自动更新

**学习路径规划** — 基于评估结果自动生成个性化学习计划

**练习与评测** — 自动出题、评分、反馈，客观题字符串比对 + 主观题本地 GGUF 模型评分

## 技术架构

```
┌──────────────┐     ┌──────────────────┐     ┌──────────────────┐
│   Frontend   │────▶│   Java Backend   │────▶│  Python AI Agent │
│  React + Vite │     │  Spring Boot 3.3  │     │  FastAPI + SSE   │
│  Port 80     │     │  Port 8081       │     │  Port 8000       │
└──────────────┘     └──────────────────┘     └──────────────────┘
                             │                         │
                   ┌─────────┼─────────┐       ┌──────┴──────┐
                   │         │         │       │  LLM Providers │
              PostgreSQL   MongoDB   Redis    │ OpenAI Compatible /│
              + pgvector   对话/消息  缓存     │ MiMo / Spark     │
              Port 5432   Port 27017 Port 6379 └─────────────┘
```

| 层 | 技术栈 | 端口 |
|---|---|---|
| 前端 | TypeScript, React 18, Vite, Tailwind CSS 4, Nginx | 80 |
| 后端 | Java 21, Spring Boot 3.3, Spring Security (JWT), Maven | 8081 |
| AI Agent | Python 3.11, FastAPI, SSE 流式, DashScope Embedding | 8000 |
| 向量库 | PostgreSQL 16 + pgvector (1024 维 IVFFlat 索引) | 5432 |
| 文档库 | MongoDB 7 (对话历史、消息、流事件) | 27017 |
| 缓存 | Redis 7 (限流、幂等、缓存, AOF 持久化) | 6379 |

## Agent 运行时内核（参考 Claude Code 设计）

本项目的 Agent 运行时内核（`python-agent/src/ai_modules/runtime/`）在架构理念上参考了 Claude Code 的 agent 执行机制。Claude Code 作为一个成功的 AI 编程助手，其 **Agent Loop → 工具调用 → Hook 拦截 → 权限检查 → 上下文压缩 → 故障恢复** 的设计模式已被验证为构建可靠 Agent 系统的有效范式。

### 参考对照

| 智学引擎模块 | Claude Code 对应机制 | 设计思路 |
|---|---|---|
| `AgentCoreLoop` | Agent tool-use loop | LLM 推理 → 工具调用 → 结果注入 → 再推理，max_iterations 限制，无 tool_calls 则返回最终答案 |
| `ToolRegistry` | Tool 注册与发现 | 按 name 注册工具，按 agent_level 过滤可见工具集，生成 OpenAI function-calling schema |
| `HookChain` | Hooks 系统 | 工具执行前后的拦截链，可修改输入参数、拒绝执行、校验输出结果 |
| `PermissionPolicy` | Permission 系统 | allow/deny 规则匹配 + 数值级别检查 (READ_ONLY → FULL_ACCESS)，类似 Claude Code 的权限分级 |
| `ConversationCompactor` | Context compaction | Token 预算估计 + 历史对话自动摘要 + 保留最近 N 轮，解决长会话上下文窗口问题 |
| `ContextSnapshot` | System prompt 构建 | 聚合运行时上下文（用户画像、学习进度、知识薄弱点）注入 Agent prompt |
| `RecoveryEngine` | 错误处理与重试 | 按 failure_type 分类重试策略（Timeout 1次, RateLimit 2次），支持 fallback |

### 独创机制

- **KnowledgeGuardHook**: 知识库守卫钩子，拦截所有 `generate_*` 工具调用，自动检索知识依据；无证据则拒绝生成，从源头防止 LLM 幻觉
- **Supervisor 路由编排**: 根据 `serviceType` + `resourceType` 动态解析 Agent 链，支持 `{generation_agent}` 动态槽位
- **工具输出智能压缩**: 字符串/列表/字典三级截断，防止工具返回内容撑爆上下文窗口

> 详细设计见 [系统架构文档](docs/architecture.md) 第七章。

## 多智能体系统

系统通过 Supervisor 模式编排 16 个专业 Agent，根据服务类型自动路由到对应的 Agent 链：

| 路由 | Agent 链 | 说明 |
|---|---|---|
| 智能辅导 | query_rewrite → retrieval → image_analysis → tutor → profile | 多轮对话辅导，自动更新画像 |
| 资源生成 | query_rewrite → retrieval → {生成 Agent} | 根据资源类型动态选择生成器 |
| 视频生成 | query_rewrite → retrieval → video_generator | 脚本生成 → TTS → 浏览器端 DH Live 渲染 |
| 练习评判 | practice → judge → profile | 自动出题、评分、反馈 |
| 路径规划 | path_planning | 基于评估生成学习计划 |
| 学习评估 | evaluation | 综合评估 |
| 画像构建 | tutor → profile | 对话中构建用户画像 |
| 资源推送 | resource_push | 匹配现成学习资源 |

支持 3 家 LLM 提供商，**可按 Agent 组件独立配置模型**：

- **OpenAI 兼容接口** — 百炼 / DeepSeek / 通用 OpenAI Compatible
- **小米 MiMo** — 支持 PPTX 直出
- **讯飞星火**

## RAG 知识库

### 知识覆盖

20 门计算机学科，986+ 知识块：

操作系统、数据结构、计算机网络、计算机组成原理、编译原理、数据库原理、软件工程、算法设计与分析、程序设计、离散数学、人工智能、机器学习、信息安全、分布式系统、计算机图形学、C语言深入、Go语言、Rust语言、Java深入、JavaScript/TypeScript、Python深入、程序设计语言原理

### 向量化流程

知识库采用两阶段离线导入流程：

```
wiki/*.md ──①──▶ rag.wiki_page ──②──▶ rag.knowledge_document + rag.knowledge_chunk
   │              (结构化存储)              (1024 维向量)
   │
   └── rag.wiki_link (知识图谱: WIKILINK / SHARED_TAG / SHARED_SOURCE / COMMUNITY)
```

**阶段一：结构化导入** (`python-agent/knowledge/import_wiki_to_db.py`)
- 解析 Markdown（含 YAML frontmatter），写入 `rag.wiki_page`
- 自动提取 `[[wikilink]]` 双链，构建 `rag.wiki_link` 知识图谱
- 同步填充 `rag.term_lexicon` 术语词典（用于 FMM 分词）
- 支持 `--incremental` 增量模式，跳过已存在页面

**阶段二：向量化** (`python-agent/knowledge/vectorize_wiki.py`)
- 仅向量化知识文档的**标题**（title embeddings 远优于 content embeddings）
- 调用 DashScope `qwen3-vl-embedding` 模型生成 1024 维稠密向量
- 批量写入 `rag.knowledge_document` + `rag.knowledge_chunk`
- 支持 `--incremental` 增量模式，只处理未向量化页面

**预置数据**：`vector_data.dump`（~11.5MB pg_dump）包含全部已向量化的知识块和资源，首次启动时自动恢复，无需重新调用 Embedding API。

### 检索架构

三通道混合检索 + RRF 融合排序：

```
用户查询
  │
  ├─ Channel A: GrepSearcher ─── 短语优先匹配（完整查询 → FMM术语 → Token回退）
  │   └── 同义词扩展 (rag.synonym_group)
  │
  ├─ Channel B: VectorSearcher ─ 语义相似度（pgvector cosine, IVFFlat 索引）
  │   └── 同时搜索 knowledge_chunk + resource_chunk
  │
  ├─ Channel C: GraphExpander ── 知识图谱扩展（从 A/B 的 top 结果出发，沿 wiki_link 扩展）
  │
  └─ RRFFusion ─── 加权 RRF 融合，输出最终排序
```

## 本地 Judge 模型

Judge Agent 的客观题判分已改为字符串比对（零 LLM 调用），主观题评估支持本地 GGUF 模型：

| 项目 | 值 |
|------|-----|
| 基座模型 | Qwen3-0.6B |
| 训练数据 | Wiki 知识点 x 3 种答案变体 |
| 训练方式 | SFT (1495 样本) + GRPO (200 组) |
| 模型格式 | GGUF Q8_0 |
| 模型大小 | 610MB |
| 推理引擎 | llama-cpp-python |
| 推理速度 | ~3s/次（CPU） |
| 启用方式 | `.env` 中 `ENABLE_LOCAL_JUDGE=true` |

## 快速开始

### 环境要求

- Docker 24+ & Docker Compose v2.20+
- 至少一个 LLM API Key（OpenAI 兼容格式）

### Docker Compose 一键启动

```bash
# 1. 克隆并配置环境变量
git clone <repo-url> && cd zhixue-engine
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
1. `init.sql` — 建表、建索引、建枚举、RLS
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
├── frontend/                # React 前端
│   ├── Dockerfile           # 多阶段构建 (node → nginx:1.27-alpine)
│   ├── nginx.conf           # SPA 路由 + API 代理 + SSE 透传
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
│   │   ├── supervisor.py    # Agent 编排器 (路由解析 → Agent 链执行)
│   │   ├── agents/          # 16 个专业 Agent
│   │   ├── runtime/         # Agent 运行时内核 (参考 Claude Code 设计)
│   │   │   ├── agent_core_loop.py       # 工具调用执行循环
│   │   │   ├── tool_registry.py         # 工具注册表
│   │   │   ├── hook_chain.py            # 前置/后置钩子链
│   │   │   ├── permission_policy.py     # 权限策略
│   │   │   ├── context_snapshot.py      # 上下文快照
│   │   │   ├── conversation_compactor.py # 对话压缩器
│   │   │   ├── recovery_engine.py       # 故障恢复引擎
│   │   │   └── hooks/knowledge_guard.py # 知识守卫钩子
│   │   ├── retrieval/       # 三通道混合检索 (grep + vector + graph + RRF)
│   │   ├── llms/            # 多 LLM 提供商适配 + 本地 GGUF 评估器
│   │   ├── memory/          # 对话记忆 & 学习画像
│   │   ├── generation/      # 内容生成链 (6 种资源格式)
│   │   └── prompts/         # Agent 提示词模板
│   ├── knowledge/           # 知识库导入 & 向量化脚本
│   ├── retrieval/           # 检索模块 (grep/vector/graph/RRF)
│   ├── recommendation/      # 学习资源推荐引擎
│   └── scripts/             # 训练数据生成 & 模型训练脚本
│
├── wiki/                    # 知识库源文件 (20 门学科 Markdown)
├── contracts/               # SSE 事件 JSON Schema 契约
├── migrations/              # 数据库迁移脚本
├── tests/                   # 端到端测试
├── docker-compose.yml       # 6 服务编排
├── init.sql                 # PostgreSQL 完整 DDL
└── vector_data.dump         # 预置向量数据 (pg_dump)
```

## 安全与可靠性

- **JWT 认证** — Access Token 2h / Refresh Token 7d
- **滑动窗口限流** — 按用户 + 按 IP 双维度
- **幂等控制** — Redis 幂等键，防止重复提交
- **内容安全审查** — SafetyAgent 对生成内容进行合规检查
- **SSE 任务取消** — 文件系统标记，支持跨 worker 取消长任务
- **沙箱文件清理** — 生成文件 2h TTL，30min 定时清扫
- **RLS 行级安全** — PostgreSQL 策略，数据级隔离
- **知识守卫钩子** — 生成前强制检索知识依据，防止幻觉


## 开源许可

本项目使用了 [DH_live](https://github.com/DeepTechLab/DH_live) 开源项目，该项目基于 [MIT License](https://opensource.org/licenses/MIT) 许可。
