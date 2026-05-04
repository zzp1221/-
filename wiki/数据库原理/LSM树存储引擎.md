---
title: "LSM树存储引擎"
course: 数据库原理
chapter: 存储引擎
difficulty: ADVANCED
tags: [数据库, LSM树, 存储引擎, LevelDB, RocksDB]
aliases: [Log-Structured Merge-Tree]
source: "The Log-Structured Merge-Tree (O'Neil 1996); RocksDB Wiki; LevelDB实现"
updated_at: 2026-05-02
---

## 核心定义

LSM树是写优化的存储结构：将随机写转为顺序写。结构：MemTable(内存有序结构，通常跳表)→WAL(预写日志)→SSTable(磁盘有序文件，不可变)→Compaction(后台合并SSTable)。写入：WAL→MemTable→满后flush为SSTable→后台compaction。读取：查MemTable→查Block Cache→查SSTable(用Bloom Filter快速排除+索引定位)。

## 关键结论

1. 写放大：compaction导致数据被多次重写(LevelDB≈10x，通过Universal/Level compaction优化) 2. 读放大可能需要查多层SSTable+Bloom Filter缓解 3. 代表：LevelDB、RocksDB、Cassandra、HBase、ClickHouse MergeTree

## 关联页面

[[B+树存储引擎]] [[NoSQL数据库对比]] [[LevelDB与RocksDB]]
