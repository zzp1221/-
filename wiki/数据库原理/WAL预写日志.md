---
title: "WAL（Write-Ahead Log）原理"
course: 数据库原理
chapter: 存储引擎
difficulty: ADVANCED
tags: [数据库, WAL, 预写日志, 崩溃恢复, ARIES]
aliases: [Write-Ahead Logging]
source: "ARIES: A Transaction Recovery Method (Mohan 1992); PostgreSQL/MySQL WAL文档"
updated_at: 2026-05-02
---

## 核心定义

WAL是数据库崩溃恢复的基石。核心规则：修改数据页前必须先将REDO日志刷到持久存储（先记后写）。日志包含REDO(重做信息：如何重做修改)和UNDO(回滚信息：如何撤销修改)。ARIES恢复算法三阶段：1.Analysis(重放日志确定哪些事务活跃、需要REDO哪些页) 2.REDO(从checkpoint开始重做所有修改) 3.UNDO(回滚未提交事务)。

## 关键结论

1. WAL将随机写变为顺序写（性能关键优化）2. Checkpoint减少恢复时需REDO的日志量 3. PostgreSQL WAL是物理日志(页级)，MySQL Redo Log也是物理日志 4. 崩溃恢复后保证已提交事务不丢失(持久性)

## 关联页面

[[事务ACID特性]] [[文件系统日志机制]] [[LSM树存储引擎]]
