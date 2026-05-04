---
title: "B+树存储引擎与InnoDB"
course: 数据库原理
chapter: 存储引擎
difficulty: ADVANCED
tags: [数据库, B+树, InnoDB, MySQL, 聚簇索引]
aliases: [B+Tree Storage Engine]
source: "MySQL 8.0 Reference Manual (InnoDB); Database System Concepts (Silberschatz) 第12章"
updated_at: 2026-05-02
---

## 核心定义

B+树是数据库中最常用的索引结构，数据只存储在叶子节点。InnoDB中：聚簇索引(主键索引)的叶子节点存储完整行数据，二级索引的叶子节点存储主键值（回表查询）。页(B+树节点)=16KB(默认)。页内记录通过单向链表连接，页间通过双向链表连接。插入可能导致页分裂(50/50 split)，删除导致页合并。

## 关键结论

1. 聚簇索引决定了行的物理存储顺序 2. 二级索引回表是常见性能瓶颈，覆盖索引可避免 3. 页分裂和页合并是B+树维护的主要开销 4. 自增主键减少页分裂（总在尾部插入）

## 关联页面

[[B树与B+树]] [[聚簇索引与非聚簇索引]] [[查询优化]]
