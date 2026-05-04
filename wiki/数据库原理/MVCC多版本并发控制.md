---
title: "MVCC多版本并发控制详解"
course: 数据库原理
chapter: 事务与并发
difficulty: ADVANCED
tags: [数据库, MVCC, 事务, 并发控制, PostgreSQL, MySQL]
aliases: [Multiversion Concurrency Control]
source: "PostgreSQL官方文档第13章; MySQL InnoDB Multi-Versioning; 数据库系统概念"
updated_at: 2026-05-02
---

## 核心定义

MVCC通过保存数据的多个版本来实现非阻塞读和高效并发控制。读不阻塞写，写不阻塞读。PostgreSQL：每个元组有xmin(创建事务ID)和xmax(删除事务ID)。MySQL InnoDB：undo log保存旧版本，ReadView确定可见性。快照隔离(SI)：每个事务看到数据库的一致性快照。写偏斜(Write Skew)是SI的已知异常。

## 关键结论

1. PG直接在元组中管理版本(需要VACUUM清理)，MySQL通过undo log回溯 2. 长事务导致旧版本堆积：MySQL undo膨胀，PG表膨胀 3. SSI(Serializable SI)可检测写偏斜

## 关联页面

[[多版本并发控制MVCC]] [[事务ACID特性]] [[并发调度协议]]
