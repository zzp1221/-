---
title: Serverless架构
course: 分布式系统
chapter: 新兴架构
difficulty: INTERMEDIATE
tags: [Serverless, FaaS, BaaS, 函数计算, 无服务器, AWS Lambda]
aliases: [Serverless, 无服务器架构, FaaS, Function as a Service, BaaS]
source:
  - "Serverless Architectures on AWS, Sbarski & Kroonenburg (2017)"
  - "AWS Lambda Documentation"
  - "CNCF Serverless Whitepaper"
updated_at: 2026-05-03
---

## 核心定义

Serverless（无服务器）是一种云计算执行模型，开发者不需要管理服务器，只需编写业务逻辑代码，由云平台自动处理资源分配、扩缩容和运维。Serverless包含两个核心概念：

**FaaS（Function as a Service）**：函数即服务。开发者编写单个函数，由平台在事件触发时执行。特点：
- **事件驱动**：函数由事件触发（如HTTP请求、消息队列、文件上传）
- **按需执行**：没有请求时不运行，不消耗资源
- **自动扩缩容**：平台根据请求量自动扩缩容
- **按调用计费**：只对实际执行时间付费（精确到毫秒）

代表：AWS Lambda、Azure Functions、Google Cloud Functions

**BaaS（Backend as a Service）**：后端即服务。使用云平台提供的后端服务（如数据库、认证、存储），无需自建。
- 代表：Firebase、AWS DynamoDB、AWS Cognito

**Serverless的优势**：
- **零运维**：不需要管理服务器、操作系统、运行时
- **按需付费**：空闲时不付费，成本与实际使用量成正比
- **自动扩缩容**：从0到10000并发，平台自动处理
- **快速开发**：开发者只关注业务逻辑

**Serverless的局限**：
- **冷启动（Cold Start）**：函数首次调用时需要初始化运行时，增加延迟
- **执行时间限制**：如AWS Lambda最长执行15分钟
- **状态管理**：函数是无状态的，状态需要外部存储
- **供应商锁定**：不同云平台的FaaS接口不兼容
- **调试困难**：分布式环境下的调试比本地开发困难

## 关键结论

- Serverless适合**事件驱动**、**请求量波动大**、**单次执行时间短**的场景
- **冷启动**是Serverless的主要性能问题——可以通过预留并发、轻量运行时来缓解
- Serverless不适合**长时间运行**、**有状态**、**低延迟要求**的场景
- **Serverless vs 容器**：Serverless更简单但灵活性低，容器更灵活但需要管理
- Serverless正在向**有状态Serverless**演进（如AWS Step Functions、Durable Functions）

## 易错点

1. **冷启动问题被忽视**：Java函数的冷启动可能需要数秒。可以通过Keep Warm（定期调用）或预留并发来缓解
2. **不适合所有场景**：长时间运行的任务（如视频转码）不适合Lambda（15分钟限制）
3. **供应商锁定**：不同云平台的FaaS接口不兼容，迁移成本高。可以使用Serverless Framework等抽象层

## 例题

**题目**：某公司需要构建一个图片处理服务，功能包括：用户上传图片 → 生成缩略图 → 存储到S3 → 发送通知。平均每天1万次调用，峰值1000次/分钟。请比较Serverless和传统架构的方案。

**解答**：

**方案一：Serverless架构**

```
用户上传 → API Gateway → Lambda（生成缩略图）→ S3存储
                              ↓
                          SNS通知
```

**配置**：
- Lambda：Python运行时，内存512MB，超时30秒
- API Gateway：接收上传请求
- S3：存储原图和缩略图
- SNS：发送通知

**成本估算**（AWS）：
- Lambda：10000次/天 × 30天 = 30万次/月
- 每次执行200ms，512MB内存
- Lambda费用：30万 × 0.2秒 × 512MB / 1024 / 1000 × $0.0000166667 = 约$0.5/月
- API Gateway费用：30万 × $0.0000035 = 约$1/月
- **总费用：约$2/月**

**方案二：传统架构**

```
用户上传 → Nginx → EC2（图片处理）→ S3存储
                      ↓
                  SNS通知
```

**配置**：
- EC2：t3.micro（2 vCPU, 1GB RAM），$8/月
- Nginx：反向代理
- 应用：Python Flask

**成本**：EC2 $8/月，即使没有请求也需要付费

**对比**：
| 维度 | Serverless | 传统架构 |
|------|-----------|---------|
| 月成本 | $2 | $8 |
| 扩缩容 | 自动 | 手动 |
| 运维 | 无 | 需要 |
| 延迟 | 有冷启动 | 稳定 |
| 适用场景 | 低频、波动大 | 持续高负载 |

**推荐**：日均1万次、峰值1000次/分钟的场景，**Serverless更合适**——成本低、零运维、自动扩缩容。

## 关联页面

[[云原生架构]] [[边缘计算架构]] [[Actor模型与Akka]] [[消息队列原理]] [[熔断与降级]]
