---
title: "GraphQL查询语言"
course: 程序设计
chapter: API设计
difficulty: INTERMEDIATE
tags: [GraphQL, API, 查询语言]
aliases: [GraphQL]
source: "GraphQL官方文档; GraphQL in Action; Facebook GraphQL Spec"
updated_at: 2026-05-02
---

## 核心定义

GraphQL是API查询语言和运行时。客户端精确指定所需字段(避免over-fetching/under-fetching)。Schema定义数据类型和关系(强类型系统)。Query获取数据、Mutation修改数据、Subscription实时订阅。Resolver函数——每个字段对应一个resovler从数据源获取数据。N+1问题：GraphQL嵌套查询可能导致——用DataLoader(Facebook)批处理和缓存请求。

## 关键结论

1. GraphQL适合多端(iOS/Android/Web)不同数据需求 2. 过度灵活+深度嵌套查询需要限制(max depth/complexity)防DDoS 3. REST适合服务间调用，GraphQL适合前端-后端交互

## 关联页面

[[RESTful API设计]] [[HTTP缓存策略]]
