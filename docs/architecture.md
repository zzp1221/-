# 智学引擎 (ZhiXue Engine) — 系统架构文档

> 最后更新: 2026-05-20

## 目录

1. [架构总览](#一架构总览)
2. [部署拓扑](#二部署拓扑)
3. [前端架构](#三前端架构)
4. [Java 后端架构](#四java-后端架构)
5. [Python AI Agent 架构](#五python-ai-agent-架构)
6. [数据架构](#六数据架构)
7. [Agent 运行时内核](#七agent-运行时内核)
8. [通信协议](#八通信协议)
9. [安全架构](#九安全架构)
10. [部署架构](#十部署架构)

---

## 一、架构总览

智学引擎采用 **前后端分离 + 微服务三层架构**，通过 Docker Compose 一键部署 6 个容器。架构风格上，Java 后端遵循六边形架构 (Hexagonal Architecture)，Python AI Agent 采用 Supervisor 模式编排 17 个专业化 Agent。

```
                              ┌──────────────────────────┐
                              │      用户浏览器              │
                              │  React 18 + TypeScript    │
                              │  + Tailwind CSS 4         │
                              └──────────┬───────────────┘
                                         │ HTTP / SSE
                              ┌──────────┴───────────────┐
                              │   Nginx (反向代理 + SPA)    │
                              │   Port 80                 │
                              └──────────┬───────────────┘
                                         │
                 ┌───────────────────────┼───────────────────────┐
                 │                       │                       │
                 ▼                       ▼                       ▼
    ┌────────────────────┐  ┌────────────────────┐  ┌────────────────────┐
    │   Java BFF         │  │  Python AI Agent    │  │   数据层             │
    │   Spring Boot 3.3  │  │  FastAPI + SSE      │  │                    │
    │   Port 8081        │  │  Port 8000          │  │ PostgreSQL 16       │
    │                    │  │                     │  │ + pgvector          │
    │ ┌────────────────┐ │  │ ┌─────────────────┐ │  │ Port 5432           │
    │ │ 认证/鉴权 (JWT) │ │  │ │ Supervisor 编排  │ │  │                    │
    │ │ 任务编排/状态机 │ │  │ │ 17 Agent 注册    │ │  │ MongoDB 7           │
    │ │ SSE 代理/幂等   │ │  │ │ RAG 三通道检索   │ │  │ Port 27017          │
    │ │ 限流/审计       │ │  │ │ LLM 多Provider   │ │  │                    │
    │ └────────────────┘ │  │ │ 资源生成流水线   │ │  │ Redis 7             │
    └────────┬───────────┘  │ └─────────────────┘ │  │ Port 6379           │
             │              └──────────┬──────────┘  └────────────────────┘
             │                         │                      │
             │     X-Zhixue-Internal-Token (内部通信)          │
             └─────────────────────────┘                      │
                                                               │
            Redis Streams (SmartEngine 任务队列) ←─────────────┘
```

### 技术栈速查

| 层 | 语言/框架 | 关键依赖 | 端口 |
|---|---|---|---|
| 前端 | TypeScript, React 18, Vite 5, Tailwind CSS 4 | react-router-dom, recharts, mermaid, framer-motion, DH Live WASM | 80 (Nginx) |
| 后端 BFF | Java 21, Spring Boot 3.3.12, Maven | Spring Security, Spring Data JPA/MongoDB/Redis, jjwt, SpringDoc | 8081 |
| AI Agent | Python 3.11, FastAPI | LangChain, LangGraph, DashScope, SSE-Starlette, OpenTelemetry | 8000 |
| 向量库 | PostgreSQL 16 + pgvector | IVFFlat 索引, 1024 维 | 5432 |
| 文档库 | MongoDB 7 | TTL 索引 | 27017 |
| 缓存 | Redis 7 Alpine | AOF 持久化, Lua 脚本 | 6379 |

### 架构风格

| 组件 | 架构风格 | 核心理念 |
|------|---------|---------|
| Java 后端 | 六边形架构 (Ports & Adapters) | 领域逻辑与基础设施解耦，接口/实现可替换 |
| Python Agent | Supervisor + Agent 注册表 | 集中路由编排，Agent 专业化分工，链式执行 |
| Agent 运行时 | Claude Code 启发式内核 | AgentCoreLoop → ToolRegistry → HookChain → 容错降级 |
| 前端 | 单页应用 (SPA) | 懒加载路由，sessionStorage 会话管理，SSE 流式渲染 |

---

## 二、部署拓扑

### 2.1 Docker Compose 服务拓扑

```
zhixue-net (bridge network)
│
├── frontend (zhixue-frontend:local)
│   ├── Nginx 1.27 Alpine
│   ├── React SPA 静态资源
│   ├── API 反向代理 → app:8081
│   └── SSE 透传 (30min 超时, 无缓冲)
│
├── app (zhixue-java-app:local)
│   ├── Eclipse Temurin 21 JRE
│   ├── Spring Boot 3.3.12
│   ├── 依赖: postgres, mongo, redis, python-agent
│   └── Actuator 健康检查: /actuator/health
│
├── python-agent (zhixue-python-agent:local)
│   ├── Python 3.11 Slim
│   ├── Uvicorn + FastAPI
│   ├── 依赖: postgres, mongo, redis
│   ├── Redis Streams Worker (SmartEngine 任务消费)
│   └── 沙箱清理循环 (30min 间隔, 2h TTL)
│
├── postgres (pgvector/pgvector:pg16)
│   ├── Port 5432 → 127.0.0.1
│   ├── 启动时自动执行 init.sql + restore_vector_data.sh
│   └── 健康检查: pg_isready
│
├── mongo (mongo:7)
│   ├── Port 27017 → 127.0.0.1
│   ├── 启动时自动执行 mongo-init.js
│   └── 健康检查: mongosh --eval "db.adminCommand('ping')"
│
└── redis (redis:7-alpine)
    ├── Port 6379 → 127.0.0.1
    ├── AOF 持久化
    └── 健康检查: redis-cli ping
```

### 2.2 可选本地 Judge 覆盖

`docker-compose.local-judge.yml` 仅覆盖 `python-agent` 服务：
- 安装 `llama-cpp-python`
- 挂载 `./models` → `/app/models` (只读)
- 设置 `ENABLE_LOCAL_JUDGE=true`
- Worker 缩减为 1（避免多 worker 重复加载模型）

---

## 三、前端架构

### 3.1 技术选型

| 技术 | 版本 | 选用理由 |
|------|------|---------|
| React | 18 | 成熟 UI 框架，生态丰富 |
| TypeScript | 5.6 | 类型安全，减少运行时错误 |
| Vite | 5 | ESBuild 预构建，HMR 极速 |
| Tailwind CSS | 4 | 原子化 CSS，开发效率高 |
| React Router | 7 | 客户端路由，懒加载支持 |
| Framer Motion | 12 | 声明式动画 |
| Recharts | 3 | React 原生图表 |
| Mermaid | 11 | 文本到图表渲染 |
| React Markdown | 9 | GFM 渲染 + 代码高亮 |

### 3.2 路由结构

```
/ (Q&A 对话辅导)
├── 聊天界面: 文字输入 + 图片上传
├── SSE 流式逐字渲染
├── 深度推理模式切换
├── 联网搜索开关
└── Markdown 渲染: 公式/代码/Mermaid 图

/engine (引擎服务)
├── 资源生成: 6 种格式多选 (文档/思维导图/幻灯片/代码/练习题/视频)
├── 路径规划: 个性化学习计划
├── 学习评测: 4 维度交互式评估
└── 任务状态机: SSE 进度监控 + 结果展示

/mistakes (错题本)
├── 错题列表: 按状态/难度/知识点筛选
├── SM-2 复习会话: 逐题质量评分 (0-5)
└── 错题统计

/profile (学习画像)
├── 6 维度雷达图
├── 薄弱点排名
├── 14 天行为趋势柱状图
└── 偏好分析
```

### 3.3 组件树

```
App
├── Layout
│   ├── Sidebar (桌面端) / MobileNav (移动端)
│   │   ├── NavLinks
│   │   ├── ConversationList
│   │   └── AuthModal (登录/注册)
│   ├── ThemeToggle (暗色/亮色模式)
│   └── <Outlet /> (页面内容)
│
├── LearningStudioDemoPage (首页 + 引擎)
│   ├── QnaChatView (对话面板)
│   │   ├── MessageList (虚拟滚动)
│   │   │   ├── MarkdownRenderer
│   │   │   │   ├── CodeBlock (语法高亮)
│   │   │   │   └── MermaidDiagram (图表)
│   │   │   └── VideoCard (数字人视频)
│   │   └── InputArea (文字 + 图片上传)
│   ├── ServiceDynamicForm (引擎服务表单)
│   └── TaskResultPanel (任务结果)
│       ├── ResourceFileList (生成资源)
│       ├── QuestionBatchView (练习题)
│       └── JudgeResultView (批改结果)
│
├── MistakeBookPage
│   ├── MistakeFilter (状态/难度/知识点)
│   ├── MistakeList
│   └── ReviewSession (SM-2 评分)
│
└── ProfilePage
    ├── RadarChart (6 维度)
    ├── ScoreProgressBar (技能掌握)
    ├── WeakPointList (薄弱点)
    └── BehaviorTrendChart (14 天趋势)
```

### 3.4 关键实现

**SSE 流式客户端** (`src/api/sse.ts`):

不依赖浏览器原生 `EventSource`，基于 `fetch` + `ReadableStream` 实现：

```
fetch(url, { signal })
  └── response.body.getReader()
      └── 逐 chunk 解析 SSE 帧
          ├── event: → 更新当前事件类型
          ├── data: → 累积 JSON payload
          └── 空行 → 触发事件回调
              ├── 429/5xx → 指数退避重试
              └── 网络断开 → 自动重连
```

**浏览器端视频渲染** (`src/utils/browserVideoRenderer.ts`):

```
Python Agent 生成 TTS 音频
  → postMessage({ type: 'render', audioUrl, avatarConfig })
  → 隐藏 iframe (DH Live WASM SDK)
  → WASM 音频驱动口型同步 + 视频合成
  → postMessage({ type: 'complete', blobUrl })
  → 前端展示 Blob URL (无需服务端 GPU)
```

**会话管理** (`src/pages/LearningStudioDemoPage.utils.ts`):

- `sessionStorage` 持久化会话快照（切换对话不丢失状态）
- per-conversation 消息缓存（切换回来无需重新加载）
- 草稿保存（输入框内容不丢失）
- 对话切换检测（避免新消息写入错误对话）

---

## 四、Java 后端架构

### 4.1 六边形架构 (Hexagonal Architecture)

```
                    ┌──────────────────────────┐
                    │     入站适配器 (Inbound)    │
                    │   api/ — REST Controllers │
                    │   api/common/ — 健康检查    │
                    └────────────┬─────────────┘
                                 │
                    ┌────────────┴─────────────┐
                    │     应用服务层 (Application) │
                    │                            │
                    │  SmartEngineOrchestrator   │ ← 任务编排主入口
                    │  TaskStateMachineService   │ ← 状态机
                    │  SseEmitterService         │ ← SSE 订阅管理
                    │  SmartEngineQueueService   │ ← Redis Streams 队列
                    │  ConversationService       │ ← 对话管理
                    │  MistakeBookService        │ ← 错题本 SM-2
                    │  UserProfileQueryService   │ ← 画像查询
                    │  UserProfileAnalyticsService│ ← 行为分析
                    │  AuditService              │ ← 审计日志
                    │  RateLimiter (接口)        │ ← 限流
                    │  IdempotencyService (接口)  │ ← 幂等
                    └────────────┬─────────────┘
                                 │
         ┌───────────────────────┼───────────────────────┐
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐  ┌─────────────────────┐  ┌─────────────────┐
│  领域层 (Domain) │  │ 出站适配器 (Outbound) │  │ 横切关注点       │
│                 │  │                     │  │                 │
│ domain/user/    │  │ infrastructure/     │  │ security/       │
│ domain/task/    │  │  python/            │  │  JwtProvider    │
│ domain/conversation/│ │  HttpStreaming-    │  │  JwtAuthFilter  │
│ domain/profile/ │  │  PythonAgentClient  │  │  InternalToken  │
│ domain/artifact/│  │  HttpPythonConv-    │  │  Verifier       │
│ domain/audit/   │  │  MessageClient      │  │                 │
│ domain/video/   │  │                     │  │ infrastructure/ │
│                 │  │ infrastructure/     │  │  ratelimit/     │
│                 │  │  ratelimit/         │  │  IpRateLimit    │
│                 │  │  RateLimitFilter    │  │  Filter         │
└─────────────────┘  └─────────────────────┘  └─────────────────┘
```

### 4.2 包结构与职责

```
com.project/
├── api/                          # 入站适配器
│   ├── auth/                     # POST /api/auth/register|login|logout, GET /me
│   │   └── dto/                  # LoginRequest, RegisterRequest, AuthResponse
│   ├── conversation/             # POST/GET /api/conversations, SSE streaming
│   │   └── dto/
│   ├── smartengine/              # POST /api/smart-engine/submit|tasks/{id}|stream|cancel
│   │   ├── dto/
│   │   └── SmartEngineInternalController  # /internal/* (Python Agent → Java)
│   ├── profile/                  # GET /api/users/{id}/profile/*
│   │   └── dto/
│   ├── artifact/                 # GET /api/assets/download/{token}
│   ├── mistake/                  # GET/PATCH /api/mistakes, POST /api/mistakes/review
│   │   └── dto/
│   └── common/                   # /api/health, GlobalExceptionHandler
│
├── application/                  # 应用服务层
│   ├── auth/          AuthService
│   ├── conversation/  ConversationService, ConversationImageService
│   ├── smartengine/   SmartEngineOrchestratorService, TaskStateMachineService
│   │                  SmartEngineQueueService, SseEmitterService
│   ├── profile/       UserProfileQueryService, UserProfileAnalyticsService
│   ├── mistake/       MistakeBookService
│   ├── artifact/      ArtifactDownloadService
│   ├── audit/         AuditService
│   ├── ratelimit/     RateLimiter(接口), RedisSlidingWindowRateLimiter, InMemory*
│   └── idempotency/   IdempotencyService(接口), RedisIdempotencyService, InMemory*
│
├── domain/                       # 领域实体 + Repository
│   ├── user/           UserAccount, UserAccountRepository
│   ├── task/           SmartEngineTask, SmartEngineTaskEvent, TaskStatus(enum)
│   ├── conversation/   QnaSession, ConversationMode(enum)
│   ├── profile/        UserProfileCurrent, UserProfileSnapshot
│   ├── artifact/       GeneratedArtifact, ResourceType(enum)
│   ├── audit/          AuditLog
│   └── video/          VideoGenerationTask
│
├── infrastructure/               # 出站适配器
│   ├── python/          HttpStreamingPythonAgentClient (SSE client)
│   │                    HttpPythonConversationMessageClient
│   └── ratelimit/       IpRateLimitFilter, RateLimitFilter
│
├── security/                     # 安全
│   ├── JwtProvider               # JWT 签发/验证 (HMAC-SHA)
│   ├── JwtAuthenticationFilter   # 无状态 JWT Bearer 认证
│   ├── AuthenticatedUserResolver # 当前用户注入
│   ├── InternalTokenVerifier     # Timing-safe 内部 Token 比对
│   └── RestAuthenticationEntryPoint # 401/403 处理
│
└── config/                       # Spring 配置
    ├── SecurityConfiguration     # SecurityFilterChain
    ├── AppProperties             # @ConfigurationProperties("app")
    ├── CorsConfiguration
    ├── TaskExecutionConfiguration # Virtual Threads Executor
    └── OpenApiConfiguration      # SpringDoc
```

### 4.3 安全过滤链

```
HTTP Request
  │
  ├── IpRateLimitFilter (IP 级, 100 req/min 滑动窗口)
  │
  ├── JwtAuthenticationFilter (无状态 Bearer Token 验证)
  │   ├── /api/auth/**, /actuator/**, /internal/** → 跳过
  │   └── 其他 → 解析 JWT → 设置 SecurityContext
  │
  ├── RateLimitFilter (用户级, 60 req/min 滑动窗口)
  │   └── 通过 AnonymousAuthenticationFilter 后的 authenticated principal
  │
  └── Controller
      └── /internal/** → InternalTokenVerifier 验证 X-Zhixue-Internal-Token
```

### 4.4 任务编排流程

```
用户提交 SmartEngine 任务
  │
  ├── 1. SmartEngineController.submit()
  │     ├── Idempotency-Key 检查 (Redis SETNX)
  │     ├── 创建 SmartEngineTask (status=ACCEPTED)
  │     └── 发布到 Redis Streams
  │
  ├── 2. Python Agent SmartEngineStreamWorker 消费
  │     └── 调用 Supervisor 执行 Agent 链
  │
  ├── 3. Python Agent → Java /internal/smart-engine/tasks/{id}/started
  │     └── TaskStateMachineService 更新 status=RUNNING
  │
  ├── 4. Python Agent → Java /internal/smart-engine/tasks/{id}/events (多次)
  │     ├── TaskStateMachineService 记录 SmartEngineTaskEvent
  │     └── SseEmitterService 广播给 SSE 订阅者
  │
  └── 5. 终态: done / error / worker-failed
        └── TaskStateMachineService 更新 status 并清理 SSE 订阅
```

### 4.5 Redis Streams 任务队列

```
Python Agent (消费者)
  │
  ├── XREADGROUP BLOCK 5000 python-agent-consumer-group > (新消息)
  │
  ├── 处理任务 (Supervisor Agent 链)
  │
  └── XACK (确认消费)
      ├── 成功 → Java /internal/.../events (done)
      └── 失败 → Java /internal/.../worker-failed

取消机制:
  Java SET zhixue:cancel:{taskId} = "1"
  Python Agent 在工具调用前检查 cancel key
```

---

## 五、Python AI Agent 架构

### 5.1 整体架构

```
FastAPI Server (server.py)
│
├── POST /internal/smart-engine/stream (SSE)
│   │
│   ├── SmartEngineStreamWorker (Redis Streams 消费者)
│   │
│   └── PythonAgentSupervisor (supervisor.py)
│       │
│       ├── route_template = supervisor_routes.json[serviceType]
│       │
│       ├── Agent Chain 执行
│       │   ├── agent_1.run(context)  ──→ SSE events
│       │   ├── agent_2.run(context)  ──→ SSE events
│       │   └── ...
│       │
│       └── 终态 event (done / error)
│
├── POST /internal/conversations/{id}/messages
│   └── ConversationMessageStore (MongoDB)
│
├── GET /internal/conversations/{id}/messages
│   └── ConversationMessageStore (MongoDB)
│
└── Lifespan
    ├── SmartEngineStreamWorker.start() (后台 asyncio task)
    └── SandboxCleanupLoop (30min 间隔, 2h TTL)
```

### 5.2 Supervisor 路由编排

9 种服务类型通过 `supervisor_routes.json` 映射到 Agent 链：

| 服务类型 | Agent 链 | 说明 |
|----------|---------|------|
| TUTORING | query_rewrite → retrieval → [image_analysis] → [tutor \| deep_reasoning] → profile | QueryClassifier 动态选择策略 |
| RESOURCE_GENERATION | query_rewrite → retrieval → resource_bundle | 多资源类型 LangGraph 并发 fan-out 生成 |
| RESOURCE_PUSH | resource_push | 匹配已有资源 + Tavily 搜索 |
| VIDEO_GENERATION | query_rewrite → retrieval → video_generator | 脚本 → TTS → 渲染 |
| PRACTICE_JUDGE | practice → judge → profile | 出题 → 批改 → 更新画像 |
| PATH_PLANNING | path_planning | 个性化学习路径 |
| EVALUATION | evaluation | 4 维度交互式评测 |
| LEARNING_EVALUATION | evaluation | 同上 |
| PROFILE_BUILD | tutor → profile | 异步画像构建 |

### 5.3 17 个注册 Agent

```
agent_registry = {
    "query_rewrite":    QueryRewriteAgent      # 查询改写 (LLM + direct fallback)
    "retrieval":        RetrievalAgent         # 三通道混合检索
    "tutor":            TutorAgent             # 苏格拉底式辅导 (3 种策略)
    "deep_reasoning":   DeepReasoningAgent     # 四步推理流水线
    "practice":         PracticeAgent          # 练习题生成 (单选 + 简答)
    "judge":            JudgeAgent             # 批改评分 (客观匹配 + 主观 LLM/GGUF)
    "profile":          ProfileAgent           # 学习画像构建
    "evaluation":       EvaluationAgent        # 4 维度学习评测
    "path_planning":    PathPlanningAgent      # 学习路径规划
    "resource_push":    ResourcePushAgent      # 资源推送
    "image_analysis":   ImageAnalysisAgent     # 图片内容分析
    "document":         DocumentGeneratorAgent # 文档生成
    "mindmap":          MindMapGeneratorAgent  # Mermaid 思维导图
    "slides":           SlideGeneratorAgent    # PPTX 生成
    "reading":          ReadingGeneratorAgent  # 阅读材料
    "code":             CodeGeneratorAgent     # 代码案例
    "video":            VideoGenerationAgent   # 数字人视频
}
```

### 5.4 QueryClassifier 辅导路由

TutorAgent 的入口不是固定路由，而是通过 QueryClassifier 动态决策：

```
用户消息
  │
  ├── 寒暄/闲聊 (greeting/small_talk)
  │   └── 直接回复 (无检索、无画像)
  │
  ├── 承接上一轮 (follow_up)
  │   └── tutor (无检索)
  │
  ├── 明确问题 + 深度推理模式
  │   └── query_rewrite → retrieval → deep_reasoning → profile
  │
  ├── 明确问题 (普通)
  │   └── query_rewrite → retrieval → tutor → profile
  │
  ├── 模糊话题
  │   └── query_rewrite → retrieval → tutor → profile
  │
  └── 含图片
      └── image_analysis (优先) → 按文字类型路由
```

### 5.5 ResourceBundleWorkflow (Graph 编排)

资源生成不再是简单的 Agent 串行调用，而是通过 LangGraph 构建的有向无环图 (DAG)：

```
ResourceBundleWorkflow (LangGraph StateGraph)
│
├── node: query_rewrite
│   └── QueryRewriteAgent: 改写用户查询
│
├── node: retrieval
│   └── RetrievalAgent: 四通道检索
│
├── node: resource_selector
│   └── 解析用户选择的 resourceTypes[]
│
├── fan-out 并发资源节点
│   ├── document_agent   → DocumentGeneratorAgent
│   ├── mindmap_agent    → MindMapGeneratorAgent
│   ├── slides_agent     → SlideGeneratorAgent
│   ├── code_case_agent  → CodeGeneratorAgent
│   ├── practice_agent   → PracticeAgent
│   └── video_agent      → VideoGenerationAgent
│
├── custom stream bridge
│   └── 资源节点实时透传 progress/resource_file/question_batch
│
└── node: bundle_synthesizer
    └── 汇总通过 provenance gate 的产物；部分失败 → PARTIAL_FAILED
```

### 5.6 RAG 三通道混合检索

```
用户查询
  │
  ├── 1. FMM 分词 (Forward Maximum Matching)
  │      └── 使用 rag.term_lexicon 术语词典
  │
  ├── 2. 四通道并行检索
  │   │
  │   ├── Channel A: GrepSearcher (权重 3.0)
  │   │   ├── 完整查询词组匹配
  │   │   ├── FMM 术语匹配
  │   │   ├── 单 Token 回退匹配
  │   │   └── 同义词扩展 (rag.synonym_group)
  │   │   └── 优势: 中文技术术语精确匹配
  │   │
  │   ├── Channel B: VectorSearcher (权重 5.0)
  │   │   ├── DashScope qwen3-vl-embedding (1024 维)
  │   │   ├── pgvector cosine 相似度
  │   │   ├── IVFFlat 索引 (100 lists)
  │   │   └── 同时搜索 knowledge_chunk + resource_chunk
  │   │
  │   ├── Channel C: GraphExpander (权重 0.5)
  │   │   ├── 从 A/B top-K 结果出发
  │   │   ├── 沿 wiki_link 扩展 1-hop 邻居
  │   │   └── 按 link_type 加权 (WIKILINK > SHARED_TAG > COMMUNITY)
  │   │
  │   └── Channel D: TavilySearcher (权重 1.5, 可选)
  │       └── Tavily Search API 联网搜索
  │
  ├── 3. 加权 RRF 融合
  │      score(doc) = Σ weight_ch × priority_boost / (k + rank_ch(doc) + 1)
  │      k = 60
  │      词组匹配: priority_boost = 1.5x
  │
  └── 4. 结果去重 + Top-K 截断
         └── 返回给 Agent 作为检索上下文
```

### 5.7 LLM 多 Provider 架构

```
LLMComponentOverride (14 个槽位)
│
├── tutor_llm           ├── practice_llm        ├── judge_llm
├── profile_llm         ├── evaluation_llm      ├── retrieval_llm
├── generation_llm      ├── planning_llm        ├── query_rewrite_llm
├── review_llm          ├── safety_llm          ├── path_planning_llm
├── resource_push_llm   └── conversation_summary_llm
│
└── Provider 解析
    │
    ├── openai_compatible (DashScope / DeepSeek / 通用)
    │   └── OpenAI-compatible API → Chat Completion + Embedding
    │
    ├── mimo (小米 MiMo)
    │   └── MiMo-v2-omni → Chat + PPTX 直出
    │
    └── spark (讯飞星火)
        └── 4.0Ultra → Chat Completion
```

### 5.8 Skill 系统

Agent 的 system prompt 不硬编码在 Python 代码中，而是通过 SKILL.md 文件管理：

```
skills/
├── tutor/SKILL.md         # name: tutor, description: "苏格拉底式辅导..."
├── profile/SKILL.md       # name: profile, description: "学习画像分析..."
├── practice/SKILL.md      # name: practice, description: "练习题生成..."
├── judge/SKILL.md         # name: judge, description: "批改评分..."
├── evaluation/SKILL.md    # name: evaluation, description: "学习评测..."
├── path_planning/SKILL.md # name: path_planning, description: "路径规划..."
└── query_rewrite/SKILL.md # name: query_rewrite, description: "查询改写..."
```

每个 SKILL.md 结构：

```markdown
---
name: tutor
description: 苏格拉底式辅导 Agent，根据学生画像选择教学策略
version: "1.0"
---

# 角色
你是一位耐心的计算机科学教师...

## 教学策略
...

## 学生画像上下文
{{snapshot_context}}
```

运行时 `SkillLoader` 加载文件，解析 YAML frontmatter，将 `{{snapshot_context}}` 替换为实时学生画像上下文。Prompt 迭代独立于代码变更。

---

## 六、数据架构

### 6.1 PostgreSQL (pgvector)

**3 个 Schema**:

```
app (业务数据, 13 表)
├── users                        # 用户账号
├── qna_session                  # 对话会话 (元数据)
├── qna_message_ref              # 消息引用
├── smart_engine_session         # 引擎会话
├── smart_engine_task            # 引擎任务 (核心)
├── smart_engine_task_event      # 任务事件 (SSE 回放)
├── user_profile_current         # 当前画像
├── user_profile_snapshot        # 画像快照 (版本化)
├── learner_feature              # 学习特征 (多维度 + 生命周期)
├── learning_plan / learning_plan_snapshot
├── generated_artifact           # 生成产物 (下载 Token)
├── assessment_result            # 评测结果
├── practice_set / practice_item / practice_submission  # 练习/批改
├── tutoring_session             # 辅导会话
├── mistake_record / mistake_review_session / mistake_review_result  # 错题本
└── audit_log                    # 审计日志

rag (知识库, 10 表)
├── wiki_page                    # Wiki 页面 (Markdown)
├── wiki_link                    # 知识图谱边
├── wiki_page_graph_features     # 图特征 (PageRank, degree)
├── term_lexicon                 # 术语词典 (FMM 分词)
├── synonym_group                # 同义词组
├── knowledge_document           # 知识文档 (标题向量, 1024 维)
├── knowledge_chunk              # 知识块 (内容向量, 1024 维)
├── resource_document            # 资源文档
├── resource_chunk               # 资源块
└── video_generation_task        # 视频生成任务

storage (1 表)
└── resource_object              # 资源对象存储
```

**向量索引**: 2 个 IVFFlat 索引，1024 维，100 lists：

```sql
CREATE INDEX idx_knowledge_chunk_embedding
  ON rag.knowledge_chunk
  USING ivfflat (embedding vector_cosine_ops)
  WITH (lists = 100);

CREATE INDEX idx_resource_chunk_embedding
  ON rag.resource_chunk
  USING ivfflat (embedding vector_cosine_ops)
  WITH (lists = 100);
```

**行级安全 (RLS)**: 24 张表启用 RLS，基于 `app.current_user_uuid()` 会话变量实现三级别访问控制 (GLOBAL / USER / COURSE)。

### 6.2 MongoDB

```
zhixue (数据库)
├── conversation_threads         # 对话线程
│   └── JSON Schema 验证 (mode: QNA | SMART_ENGINE)
├── conversation_messages        # 对话消息
│   └── 字段: role, content, references, confidence, safety
└── conversation_stream_events   # SSE 流事件
    └── TTL 索引: expiresAt → 自动清理过期事件
```

### 6.3 Redis

| 用途 | 键模式 | 数据结构 | TTL |
|------|--------|---------|-----|
| 用户级限流 | `rate_limit:user:{userId}` | Sorted Set (滑动窗口) | 窗口大小 |
| IP 级限流 | `rate_limit:ip:{ip}` | Sorted Set (滑动窗口) | 窗口大小 |
| 任务幂等 | `idempotency:{key}` | String (SETNX) | 24h |
| LLM 结果缓存 | `llm_cache:{hash}` | String (JSON) | 300s |
| 检索结果缓存 | `retrieval_cache:{hash}` | String (JSON) | 60s |
| SmartEngine 队列 | `zhixue:smart-engine:stream` | Stream | — |
| SmartEngine 消费者组 | `python-agent-consumer-group` | Consumer Group | — |
| 任务取消标记 | `zhixue:cancel:{taskId}` | String | 1h |

**Redis 不可用降级**: RateLimiter 和 IdempotencyService 都定义了接口，Redis 不可用时自动切换到 InMemory 实现。

### 6.4 数据流

```
知识导入 (离线):
  wiki/*.md → import_wiki_to_db.py → rag.wiki_page + rag.wiki_link
                                     → vectorize_wiki.py
                                     → rag.knowledge_document + rag.knowledge_chunk
                                     → vector_data.dump (随项目分发)

用户对话 (在线):
  前端 → Nginx → Java BFF → Python Agent
    └── conversation_messages (MongoDB) ← Python Agent 写入
    └── qna_session (PostgreSQL) ← Java BFF 写入
    └── user_profile_current (PostgreSQL) ← ProfileAgent 更新

引擎任务 (在线):
  前端 → Java BFF → Redis Streams → Python Agent Worker
    └── smart_engine_task + smart_engine_task_event (PostgreSQL)
    └── generated_artifact (PostgreSQL) ← 产物下载 Token
```

---

## 七、Agent 运行时内核

Agent 运行时内核 (`python-agent/src/ai_modules/runtime/`) 是每个 Agent 执行其核心逻辑的通用基础设施，架构理念参考了 Claude Code 的 Agent 执行机制。

### 7.1 架构概览

```
Agent.run(context)
  │
  ├── 1. ContextSnapshot.build()          # 构建运行时上下文
  │       ├── 用户画像 (user_profile)
  │       ├── 学习进度 (learning_progress)
  │       ├── 知识薄弱点 (knowledge_gaps)
  │       └── 对话历史 (conversation_history)
  │
  ├── 2. SkillLoader.load(agent_name)     # 加载 Agent prompt
  │       └── SKILL.md → system_prompt (含 {{snapshot_context}} 注入)
  │
  ├── 3. AgentCoreLoop.run()              # 工具调用循环
  │       │
  │       └── for iteration in range(max_iterations=4):
  │           │
  │           ├── LLM 推理 (带 tool definitions)
  │           │
  │           ├── if no tool_calls:
  │           │   └── return 最终答案 (break loop)
  │           │
  │           └── for each tool_call:
  │               │
  │               ├── HookChain.before_execution()
  │               │   └── KnowledgeGuardHook:
  │               │       如果是 generate_* 工具:
  │               │         检索知识依据
  │               │         无证据 → 拒绝执行
  │               │
  │               ├── PermissionPolicy.check()
  │               │   └── agent_level >= tool_required_level?
  │               │
  │               ├── Tool 执行
  │               │   ├── 成功 → 结果注入上下文
  │               │   └── 失败 → RecoveryEngine.retry()
  │               │
  │               └── HookChain.after_execution()
  │                   └── 输出校验: 字符串/列表/字典三级截断
  │
  ├── 4. ConversationCompactor.compact() (按需)
  │       └── Token 预算估计 → LLM 摘要 → 保留最近 N 轮
  │
  └── 5. 返回结果 + SSE events
```

### 7.2 核心模块

| 模块 | 文件 | 职责 |
|------|------|------|
| AgentCoreLoop | `agent_core_loop.py` | LLM → tool_call → result → 再推理循环，max 4 轮 |
| ToolRegistry | `tool_registry.py` | 按 name 注册工具，按 agent_level 过滤可见工具集，生成 OpenAI function-calling schema |
| HookChain | `hook_chain.py` | 工具执行前后拦截链：可修改参数、拒绝执行、校验输出 |
| KnowledgeGuardHook | `hooks/knowledge_guard.py` | 知识库守卫钩子：generate_* 调用前强制检索证据，无证据则拒绝，从源头防止 LLM 幻觉 |
| PermissionPolicy | `permission_policy.py` | 数值权限级别 (READ_ONLY=0 → FULL_ACCESS=3)，allow/deny 规则匹配 |
| ConversationCompactor | `conversation_compactor.py` | 1200 token 预算的 LLM 对话摘要，保留关键信息 |
| ContextSnapshot | `context_snapshot.py` | 聚合学生画像、学习进度、知识薄弱点，注入 Agent prompt |
| RecoveryEngine | `recovery_engine.py` | 按 failure_type 分类重试：Timeout 1次，RateLimit 2次，Retrieval 1次 |
| SkillLoader | `skill_loader.py` | 加载 SKILL.md，解析 YAML frontmatter，模板注入 |
| ResourceBundleWorkflow | `resource_bundle_workflow.py` | LangGraph StateGraph 编排多资源并发 fan-out 生成 |

### 7.3 容错设计

每个 LLM 调用都有确定性或启发式降级方案。系统永远不会因单点故障而完全不可用：

| 故障场景 | 降级策略 |
|---------|---------|
| LLM API 超时 | 重试 1 次 → 降级到 direct/heuristic 实现 |
| LLM Rate Limit | 重试 2 次 (指数退避) → 降级 |
| Embedding API 不可用 | 降级到纯 Grep 检索 |
| Redis 不可用 | 自动切换到 InMemory 实现 (限流/幂等/缓存) |
| 检索无结果 | 返回空上下文 + TutorAgent 使用诊断式脚手架 |

---

## 八、通信协议

### 8.1 SSE 事件协议

系统定义了 14 种标准化 SSE 事件类型，有 JSON Schema 契约 (`contracts/sse-events.schema.json`)：

```
event: progress
data: {"type":"progress","stage":"RETRIEVAL","percent":35,"message":"正在检索知识库..."}

event: result_chunk
data: {"type":"result_chunk","text":"在学习指针时，需要注意..."}

event: resource_file
data: {"type":"resource_file","resourceType":"SLIDES","title":"指针详解.pptx","downloadUrl":"/api/assets/download/{token}"}

event: question_batch
data: {"type":"question_batch","items":[{...}]}

event: judge_result
data: {"type":"judge_result","totalScore":85,"items":[{...}]}

event: video_gen:script
data: {"type":"video_gen:script","script":"..."}

event: video_gen:speech
data: {"type":"video_gen:speech","audioUrl":"..."}

event: video_gen:avatar
data: {"type":"video_gen:avatar","progress":50}

event: video_gen:complete
data: {"type":"video_gen:complete","videoUrl":"..."}

event: done
data: {"type":"done","summary":"..."}

event: error
data: {"type":"error","code":"RETRIEVAL_FAILED","message":"..."}
```

### 8.2 内外部通信通道

```
前端 ↔ Java BFF:
  ├── REST API (JSON)
  │   ├── POST /api/auth/login|register
  │   ├── GET/POST /api/conversations
  │   └── POST /api/smart-engine/submit
  └── SSE (text/event-stream)
      ├── GET /api/conversations/{id}/messages/stream
      └── GET /api/smart-engine/tasks/{id}/stream

Java BFF ↔ Python Agent:
  ├── HTTP + SSE (X-Zhixue-Internal-Token)
  │   ├── POST /internal/smart-engine/stream (SSE)
  │   ├── GET/POST /internal/conversations/{id}/messages
  │   └── POST /internal/smart-engine/{taskId}/cancel
  └── Python Agent → Java (HTTP callback)
      ├── POST /internal/smart-engine/tasks/{taskId}/started
      ├── POST /internal/smart-engine/tasks/{taskId}/events
      └── POST /internal/smart-engine/tasks/{taskId}/worker-failed

Java BFF → Python Agent (异步):
  └── Redis Streams (SmartEngine 任务队列)
      └── XADD zhixue:smart-engine:stream * task {...}
```

### 8.3 Nginx SSE 透传

Nginx 对 SSE 端点做特殊配置以确保长连接不中断：

```nginx
location ~ ^/api/(conversations/.*/messages/stream|smart-engine/tasks/.*/stream) {
    proxy_pass http://app:8081;
    proxy_http_version 1.1;
    proxy_set_header Connection "";
    proxy_buffering off;              # 关闭缓冲，实时推送
    proxy_read_timeout 1800s;         # 30min 长连接超时
    proxy_set_header X-Real-IP $remote_addr;
}
```

---

## 九、安全架构

### 9.1 纵深防御

```
┌─────────────────────────────────────────────┐
│  第 1 层: 传输安全                            │
│  ├── Nginx 安全头 (CSP, X-Frame-Options,     │
│  │   X-Content-Type-Options, HSTS)           │
│  ├── Gzip 压缩 (防 BREACH)                    │
│  └── 50MB 上传限制                            │
├─────────────────────────────────────────────┤
│  第 2 层: 认证与授权                           │
│  ├── JWT (HMAC-SHA256): Access 2h / Refresh 7d│
│  ├── BCrypt 密码哈希                           │
│  ├── 无状态 Session (CSRF disabled)           │
│  └── 公开端点白名单                            │
├─────────────────────────────────────────────┤
│  第 3 层: 速率限制                             │
│  ├── IP 级: 100 req/min (Redis Lua 滑动窗口)  │
│  └── 用户级: 60 req/min (Redis Lua 滑动窗口)   │
├─────────────────────────────────────────────┤
│  第 4 层: 业务安全                             │
│  ├── 幂等控制: Idempotency-Key (Redis SETNX)   │
│  ├── 内容安全: SafetyAgent 审查                 │
│  ├── 幻觉防护: KnowledgeGuardHook 证据门控      │
│  └── 文件安全: 路径穿越检查 + 类型白名单         │
├─────────────────────────────────────────────┤
│  第 5 层: 内部通信安全                          │
│  ├── X-Zhixue-Internal-Token (timing-safe)    │
│  ├── Docker 内部网络 (zhixue-net)              │
│  └── 数据库端口仅绑定 127.0.0.1                │
├─────────────────────────────────────────────┤
│  第 6 层: 数据安全                             │
│  ├── PostgreSQL RLS (24 表, 三级访问控制)       │
│  ├── 密码/Token 不入日志                        │
│  ├── 沙箱文件 2h TTL 自动清理                   │
│  └── 审计日志 (audit_log 表)                   │
└─────────────────────────────────────────────┘
```

### 9.2 认证端点白名单

以下端点跳过 JWT 认证：

| 路径 | 原因 |
|------|------|
| `/api/auth/register`, `/api/auth/login` | 注册/登录 |
| `/api/health`, `/actuator/health` | 健康检查 |
| `/internal/**` | 内部通信 (InternalToken) |
| `/api/conversations/images/*` | 公开图片 (JWT 签名 URL) |
| `/api-docs/**`, `/swagger-ui/**` | API 文档 |

---

## 十、部署架构

### 10.1 一键部署

```bash
git clone <repo-url> && cd zhixue-engine
cp .env.example .env
# 编辑 .env: 设置密码、JWT Secret、LLM API Key
docker compose up -d --build
```

### 10.2 容器启动顺序

```
1. postgres (健康检查: pg_isready)
2. mongo    (健康检查: mongosh ping)
3. redis    (健康检查: redis-cli ping)
     │
     ├── 4. python-agent (depends_on: postgres+mongo+redis healthy)
     │      ├── 等待 PostgreSQL 就绪
     │      ├── 启动 Redis Streams Worker
     │      └── 启动 Sandbox Cleanup Loop
     │
     └── 5. app (depends_on: postgres+mongo+redis+python-agent healthy)
            └── Spring Boot 启动 (约 15s)
                  │
                  └── 6. frontend (depends_on: app healthy)
                         └── Nginx 启动
```

### 10.3 热更新边界

当前联调/演示环境只允许 `docker cp` 热更新：

```bash
# 允许的操作:
docker cp ./frontend/dist/. frontend:/usr/share/nginx/html/
docker cp ./project/target/classes/. app:/app/classes/
docker cp ./python-agent/src/. python-agent:/app/src/

# 禁止的操作:
docker compose build
docker compose up --build
docker compose up --force-recreate
```

### 10.4 资源消耗

| 服务 | CPU | 内存 | 磁盘 |
|------|-----|------|------|
| frontend (Nginx) | 0.1 | 50MB | 20MB |
| app (Java) | 0.5 | 512MB | 150MB |
| python-agent | 1.0 | 512MB | 300MB |
| postgres | 0.5 | 256MB | 1GB (含向量) |
| mongo | 0.3 | 256MB | 500MB |
| redis | 0.1 | 64MB | 100MB |
| **总计** | **2.5** | **~1.6GB** | **~2GB** |
