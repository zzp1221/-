---
title: "RESTful API设计最佳实践"
course: 软件工程
chapter: 软件设计
difficulty: BASIC
tags: [软件工程, REST, API, 设计]
aliases: [RESTful API Design]
source: "Roy Fielding博士论文 (REST, 2000); Microsoft REST API Guidelines; Google API Design Guide"
updated_at: 2026-05-02
---

## 核心定义

REST(表述性状态转移)风格约束：1.客户-服务器分离 2.无状态(每个请求包含所需全部信息) 3.可缓存(响应声明可缓存性) 4.统一接口(资源URL标识、自描述消息、超媒体HATEOAS) 5.分层系统 6.按需代码(可选)。设计实践：URL名词复数(/users、/users/{id}/orders)、HTTP方法对应CRUD(GET/POST/PUT/PATCH/DELETE)、分页(offset/limit或cursor)、版本策略(v1/v2或Header)。

## 关键结论

1. REST不是规范而是一种架构风格 2. HATEOAS(超媒体驱动)常被忽略但Richardson Maturity Model最高级 3. 实际中GraphQL和gRPC是REST的重要替代方案

## 关联页面

[[HTTP状态码全览]] [[微服务架构设计]] [[API安全]]
