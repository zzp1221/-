---
title: "NoSQL数据库全景对比"
course: 数据库原理
chapter: 数据库概述
difficulty: BASIC
tags: [数据库, NoSQL, 键值, 文档, 列族, 图]
aliases: [NoSQL Database Comparison]
source: "Designing Data-Intensive Applications (Kleppmann) 第2章"
updated_at: 2026-05-02
---

## 核心定义

NoSQL数据库按数据模型分类：键值存储(Redis，DynamoDB，etcd)——简单KV操作极快。文档存储(MongoDB，CouchDB，Firestore)——JSON文档，灵活schema。列族存储(Cassandra，HBase)——宽列，高写入吞吐。图数据库(Neo4j，ArangoDB)——节点+边，图遍历查询。时序数据库(InfluxDB，TimescaleDB)——时间戳主键，高压缩。

## 关键结论

1. 选择标准：数据模型匹配是第一优先级 2. 关系型vs NoSQL：并非替代而是互补（多模型架构）3. NewSQL(CockroachDB/TiDB/Spanner)试图统一SQL+水平扩展 4. 大多数实际系统使用混合持久化(Polyglot Persistence)

## 关联页面

[[CAP与BASE理论]] [[LSM树存储引擎]] [[B+树存储引擎]]
