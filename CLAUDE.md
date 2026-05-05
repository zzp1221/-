# CLAUDE.md

行为准则，用于减少 LLM 常见编码错误。偏向谨慎而非速度。

***

阅读项目代码，找出bug和仅仅是占位链路未完整实现的链路以及存在的问题，修复bug和问题以及解决存在的问题，更新docker容器中的代码。根据8. 全链路Bug 排查给出优化建议驱动下一次任务。循环直到功能全部实现,无严重bug和问题

## 1. TDD：先写测试，再写代码

**没有测试等于没有完成。** 红→绿→重构。

| 层                   | 框架                        |
| ------------------- | ------------------------- |
| Python Agent/检索/知识层 | pytest + pytest-asyncio   |
| Java                | JUnit 5 + Mockito（集成测试优先） |
| TS                  | Vitest                    |

LLM 调用用 mock，数据库用事务回滚。开始前回答：失败场景？最小断言？边界条件？**回答不了 = 没理解需求。**

***

## 2. 先想清楚再编码

涉及 TS↔Java↔Python 的变更列出接口影响。SSE 事件或 schema 变更说明兼容性。

| 边界          | 上游                       | 下游                 |
| ----------- | ------------------------ | ------------------ |
| 前端↔Java     | `api/*.ts` 类型            | `dto/*.java`       |
| Java↔Python | `PythonAgentClient.java` | `server.py` SSE 格式 |
| Python↔DB   | `import_wiki_to_db.py`   | `rag.wiki_page`    |
| Agent↔工具    | `agent_core_loop.py`     | 各 Agent 工具注册       |

***

## 3. 简洁优先

最少代码。不推测。单次使用不抽象。没要求的可配置性不做。写完发现 200 行可 50 行的重写。

易过度设计：新增课程 = wiki\_topics.py 加数据行；LLM 供应商切换已有 `LLMComponentOverride`，新增 Agent 提供 `*_llm` 绑定；3 个以上 Agent 共享才提复用模块。

***

## 4. 手术级变更

只动必须动的。不改相邻代码。匹配现有风格。孤儿 import 要清理，之前就存在的死代码不提不删。

Python: async/await、Pydantic、4空格 | Java: Spring Boot、UUID JWT | TS: 函数组件、Tailwind、避免 any

***

## 5. 目标驱动

定义成功标准，循环验证。

| 任务       | 标准                                      | <br />      |
| -------- | --------------------------------------- | :---------- |
| 新增 Agent | `pytest tests/test_new_agent.py -v` 全通过 | <br />      |
| 新增 API   | \`curl -s :8081/api/xxx                 | jq .\` 预期结构 |
| 检索调参     | hits\@3 >= 90%（30+ 题）                   | <br />      |
| 降级模型     | Profile/Judge 核心字段一致 >95%（50 题 diff）    | <br />      |

***

## 6. 项目约束

**契约：** Java 是唯一入口、SSE 格式依赖 `event:`/`data:` 前缀、向量 1024 维不可改、Docker Compose 是基线。

**禁止硬编码：** 类型名→枚举、密码/密钥→环境变量、模型名→`LLMComponentOverride`、中文→i18n/constants、路径→config/env。

**新增课程：** wiki 目录 → `import_wiki_to_db.py --incremental` → `vectorize_wiki.py --incremental` → resources → test\_rag 验证 hits\@3。

***

## 7. 内存与存储

强制：缓存必须 TTL；SSE emitter 三回调都移除；禁止 `except: pass`；文件写入必须带清理。
***

## 8. 全链路 Bug 排查

**前端已部署在 80 端口。每次联调前执行：从全局到单点，通过前端入口找出三个服务接起来才会出现的 bug。**

单服务测试正常、联调就出问题——重点排 nginx 超时截断、跨层 SSE 字段不匹配、容器 sandbox 路径不一致、docker-compose 遗漏环境变量。找出 bug 并给优化建议。

```
□ 登录 → JWT → localStorage
□ 流式对话 → SSE text/event-stream → 逐字渲染
□ 任务 SSE → progress/done 推动
□ resource_file downloadUrl 可下载
□ >5min 任务不被截断
□ Console 无 CORS/401/ERR_CONNECTION_REFUSED
```

***

**标志：diff 少、重写少、问题在犯错前澄清。**
