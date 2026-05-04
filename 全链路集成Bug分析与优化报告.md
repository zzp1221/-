# 全链路集成 Bug 分析与优化报告

> 日期: 2026-05-04
> 分析方法: 从 nginx:80 → Java:8081 → Python:8000 全链路追踪，交叉验证接口契约、SSE 格式、超时配置

---

## 一、严重 Bug（会导致功能完全失效）

### 1.1 NGINX SSE 超时截断（CRITICAL）

**位置**: `frontend/nginx.conf:34`

```nginx
proxy_read_timeout 300s;
```

**问题**: AI 资源生成（文档/视频/PPT）可能需要 5-10 分钟。nginx 在 300 秒无数据时强制断开 SSE 连接，但 Java→Python 之间的 HTTP streaming 不受影响——Java 继续消费 Python 输出，SSE emitter 继续 `send()`，但 nginx 已经关闭了到前端的连接。前端收到连接断开，用户体验为"卡住然后突然失败"。

**修复**: SSE 端点单独加长超时

```nginx
location /api/smart-engine/tasks/ {
    proxy_read_timeout 1800s;  # 30 分钟
}
location /api/conversations/ {
    proxy_read_timeout 1800s;
}
```

### 1.2 Download URL 是相对路径，Docker 容器内不可达（CRITICAL）

**位置**: `ArtifactDownloadService.java:78`

```java
String url = "/api/assets/download/" + savedArtifact.getDownloadToken();
```

**问题**: 下载 URL 是**相对路径**。SSE 把 `downloadUrl: "/api/assets/download/abc123"` 推给前端。前端在浏览器中使用 `new URL(downloadUrl, window.location.origin)` 或直接 `<a href>` 时，浏览器会用当前 origin (`http://localhost:80`) + 路径请求。这在**单机测试**中能工作（因为 :80 的 nginx 会代理到 Java :8081）。

但当 docker-compose 三服务启动后，**sandbox 临时文件在 Python 容器内**（`/data/sandbox-temp/`）。Java 容器执行 `Files.exists(Path.of(sandboxPath))` (`ArtifactDownloadService.java:57`) 时，访问的是**Java 容器的文件系统**，不是 Python 容器的。两个容器**不共享** sandbox-temp 文件系统！

仔细看配置：
- docker-compose line 144: Java 挂载 `D:\软件杯\Data\sandbox-temp:/data/sandbox-temp`
- docker-compose line 182: Python 挂载 `D:\软件杯\Data\sandbox-temp:/data/sandbox-temp`

两者都挂载了同一个宿主机目录，所以**文件系统是共享的**。但 Java 内 `Path.of(sandboxPath)` 的路径格式必须是 `/data/sandbox-temp/xxx`（容器内路径），而 Python 内部写文件时 `SANDBOX_ROOT=/data/sandbox-temp`。只要 Python 返回的 `sandboxPath` 也是 `/data/sandbox-temp/` 格式就行。

但如果 Python 内部使用的是 Windows 路径（D:\软件杯\Data\sandbox-temp\...），Java 容器内就找不到。

**验证**: 检查 Python `resource_builder.py` 中 `_scoped_file_name` 返回的是容器路径还是宿主机路径。

### 1.3 SSE done 事件重复触发 onDone（HIGH）

**位置**: `sse.ts:58` + `conversation.ts:106-108`

**问题**: 有两个地方会调用 `onDone()`:
1. `sse.ts:58` — reader 自然关闭（`done=true`）后调用
2. `conversation.ts:106-108` — 收到 `event==='done'` 时调用

如果 Java 发送 done 事件后 `emitter.complete()`，前端 reader 会收到 `done=true`，触发 `onDone()`。同时，done 事件的处理也调用 `onDone()`。结果：`onDone` **被调用两次**，可能导致 UI 状态异常或重复请求。

同样的 bug 也存在于 `smartEngine.ts:107`。

## 二、中等问题（特定条件下会失效）

### 2.1 Conversation SSE 过滤 Stage 名称过严

**位置**: `ConversationService.java:214-217`

```java
if (stage != null && !stage.isBlank() && !"tutoring".equals(stage)) {
    return "";
}
```

**问题**: 只在 `stage == "tutoring"` 时才将 chunk 展示给用户。如果 TutorAgent 的 AgentCoreLoop 输出的 `result_chunk` 事件的 stage 字段是其他值（如 `null`、`"explaining"`、`"retrieving"`），前端就收不到任何文本。查 TutorAgent 代码确认它实际会发什么 stage。

**风险**: 三服务联调时，Python Supervisor 的 stage 命名可能与 Java 硬编码的 `"tutoring"` 不匹配。

### 2.2 SseEmitterService 竞态：terminal 判定窗口

**位置**: `SseEmitterService.java:44-47`

```java
SmartEngineTask latestTask = taskRepository.findById(task.getId()).orElse(task);
if (!latestTask.isTerminal()) {
    emitters.computeIfAbsent(task.getId(), ...).add(emitter);
} else {
    emitter.complete();
}
```

**问题**: 在 DB 查询（line 44）和 emitter 注册（line 47）之间，后台线程可能已经完成任务并调用了 `publish(done, true)` → `emitters.remove(taskId)`。新注册的 emitter 进入一个刚被清空的列表，永远不会收到 done 事件，也永远不会被 complete（timeout=0）。

### 2.3 API_BASE_URL 在 DEV vs PROD 的行为差异

**位置**: `request.ts:37`

```ts
return import.meta.env.PROD ? '' : 'http://localhost:8081';
```

**问题**: 当用 `pnpm dev`（Vite dev server on :5173）连 Docker 容器时：
- DEV 模式 → `API_BASE_URL = 'http://localhost:8081'`
- SSE URL = `http://localhost:8081/api/smart-engine/tasks/{id}/stream`

这应该能工作，因为 Java 暴露了 `:8081`。但 Vite dev server 的 proxy 配置（`vite.config.ts:23-28`）只代理了 `/api` 开头的请求，对开发模式下直接构造的完整 URL 无效。SSE fetch 用的是完整 URL（`API_BASE_URL + path`），不经过 Vite proxy。

如果用户已经在 Docker 中运行，`:8081` 端口是暴露在宿主机的，所以直接访问 `http://localhost:8081/api/...` 应该能通。没问题。

但如果用户用 `!` 命令在 WSL/bash 中测试时，`localhost:8081` 需要确认 Docker 端口映射正确。

### 2.4 CORS `allowedHeaders` 缺少 `Idempotency-Key`

**位置**: `CorsConfiguration.java:26-35`

`Idempotency-Key` 在 allowedHeaders 列表中（line 34），所以是允许的。没问题。

但 `Last-Event-ID` 也在列表中（line 33）。这个 header 是 EventSource API 自动发送的，用于 SSE 重连。当前前端用的是 `fetch` + `ReadableStream`（手动 SSE 解析），不是浏览器原生 `EventSource`，所以不会发 `Last-Event-ID`。没问题。

### 2.5 幂等性 reserve/findExisting 竞态

**位置**: `SmartEngineOrchestratorService.java:79-97`

```java
boolean reserved = idempotencyService.reserve(currentUser.userId(), ...);
if (!reserved) {
    return idempotencyService.findExisting(...)
        .map(...)
        .orElseThrow(() -> new IllegalStateException(...));
}
```

**问题**: 如果 `reserve()` 失败后、`findExisting()` 执行前，已有的记录被其他原因删除，会抛 `IllegalStateException`（HTTP 500）。应该返回 409 而不是 crash。

## 三、前端集成问题

### 3.1 null profile crash（已知未修复）

**位置**: `LearningStudioDemoPage.tsx:862`

```tsx
props.profile?.preference.join('、')
```

`null?.preference` → `undefined` → `.join()` → **TypeError crash**

### 3.2 SSE abort 后 reader 未 cancel

**位置**: `sse.ts:60-64`

```ts
catch (error) {
    if (error instanceof DOMException && error.name === 'AbortError') {
        return;  // reader 没有 cancel
    }
}
```

**问题**: 当 AbortController.abort() 触发时，fetch 被取消，但 `reader` 没有被显式 `cancel()`。在 Chrome 中可能导致连接泄漏。

### 3.3 Conversation stream 错误处理吞没

**位置**: `ConversationService.java:131-142`

```java
} catch (Exception ex) {
    try {
        if (assistantReply.isEmpty()) {
            appendConversationMessage(..., ex.getMessage(), false);  // 把异常消息当对话存
        }
        sendErrorEvent(emitter, conversationId, sequence, ex.getMessage());
    } catch (IOException ioException) {
        emitter.completeWithError(ioException);
        return;  // 错误事件发送失败则直接 close
    }
    emitter.complete();
}
```

**问题**: 
1. `ex.getMessage()` 被当作 assistant 消息存入对话——用户会在聊天记录中看到异常堆栈
2. 如果 `sendErrorEvent` 成功但 `emitter.complete()` 失败（连接已断），客户端可能看不到错误事件

### 3.4 Resource 下载链接过期时间不透明

**位置**: `ArtifactDownloadService.java:75`

```java
artifact.setExpiresAt(OffsetDateTime.now().plusSeconds(appProperties.getDownload().getArtifactTtlSeconds()));
```

**问题**: 默认 TTL 未知（来自配置）。如果 TTL 太短（如 5 分钟），用户在阅读文档时链接过期。SSE 推送的 `expiresInSec` 和 `expiresAt` 字段前端需要展示给用户。

## 四、Python Agent 集成问题

### 4.1 Supervisor 路由失败返回 400 而非 500

**位置**: `server.py:122-124`

```python
try:
    SUPERVISOR.resolve_route(request.service_type, request.params)
except ValueError as exc:
    raise HTTPException(status_code=400, detail=str(exc))
```

**问题**: 如果 `service_type` 不在 `route_map` 中，返回 400。但 Java 调用方期望 SSE 流或特定错误格式。Java `PythonAgentClient` 的实现需要处理这个 400 响应并转为 SSE error 事件。

### 4.2 SSE 事件中 `asyncio.sleep(0.01)` 累加延迟

**位置**: `server.py:66`

```python
yield event.to_sse()
await asyncio.sleep(0.01)  # 每个事件加 10ms
```

**问题**: 如果一个请求产生 50 个 SSE 事件，总共增加 500ms 延迟。这是不必要的人为延迟。

### 4.3 Conversation 消息持久化失败导致用户消息丢失

**位置**: `ConversationService.java:258-271`

```java
private void appendConversationMessage(...) {
    try {
        pythonConversationMessageClient.appendMessage(...);
    } catch (Exception ex) {
        if (failOnError) {
            throw new ApplicationException(...);  // 用户消息发送失败 → 直接抛异常
        }
    }
}
```

**问题**: 用户消息（`failOnError=true`）如果持久化失败，整个 stream 调用失败，但用户已经在等待回复。应该先发 stream 再异步持久化用户消息。

## 五、优化建议

### 5.1 全链路超时对齐

当前各层超时不一致：

| 层 | 超时 | 问题 |
|----|------|------|
| nginx proxy_read_timeout | 300s | 太短，AI 生成任务可超 5min |
| Java HttpClient (调 Python) | ? | 未在 docker-compose 中配置 |
| Python LLM API 调用 | 60s (默认) | 可能太短 |
| 前端 axios timeout | 30s | 对 SSE 不适用（单独 fetch） |

建议统一为：SSE 端点 1800s，普通请求 60s。

### 5.2 SSE 重连机制

当前 fetch+ReadableStream 不支持自动重连。如果网络断开：
- 前端流式渲染中断
- 用户只能刷新页面
- 重新订阅 task SSE 可以 replay 已有事件（`SseEmitterService.replayEvents`），但前端没实现这个逻辑

建议：前端在 SSE 断开时显示"连接中断，正在重连"并重新调用 `GET /api/smart-engine/tasks/{id}/stream`。

### 5.3 Sandbox 文件清理

`ArtifactDownloadService` 签发 URL 后文件不清理。`download()` 方法不删除文件。依赖外部 TTL 任务（未实现）。

### 5.4 前端错误展示

`request.ts` 的 `ApiError` 有 `code` 和 `traceId` 但大部分前端页面只用 `ex.message` 展示错误，丢失了 `traceId`。用户报告问题时无法追踪。

### 5.5 监控盲区

三服务全链路缺乏：
- 每个 SSE 连接的存活时间和收发字节数
- Python→Java 的 HTTP streaming 连接数
- 每个 Agent 的执行耗时分布

没有这些指标，三服务联调出问题时只能靠猜。

---

## 六、优先级修复顺序

| 优先级 | Bug | 影响 | 修复工作量 |
|--------|-----|------|-----------|
| P0 | nginx SSE 超时 300s | 所有 AI 生成任务失败 | 5 分钟 |
| P0 | done 事件重复触发 onDone | UI 异常、可能重复提交 | 10 分钟 |
| P1 | SseEmitter 竞态窗口 | 低频但无法恢复的黑洞连接 | 30 分钟 |
| P1 | Conversation stage 过滤过严 | 用户看不到 AI 回复 | 15 分钟 |
| P1 | null profile crash | 页面崩溃 | 1 分钟 |
| P2 | Conversation 异常消息存入对话 | 用户体验差 | 15 分钟 |
| P2 | Idempotency reserve/find 竞态 | 低频 500 错误 | 20 分钟 |
| P2 | asyncio.sleep(0.01) | 每个请求多 500ms | 1 分钟 |
| P3 | SSE reader 未 cancel | 连接泄漏（低频） | 10 分钟 |
| P3 | Sandbox 文件不清理 | 磁盘渐进式增长 | 1 小时 |
| P3 | 缺少 SSE 重连 | 网络抖动丢失流式内容 | 2 小时 |
