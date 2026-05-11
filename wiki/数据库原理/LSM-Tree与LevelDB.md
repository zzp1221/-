---
title: "LSM-Tree与LevelDB"
course: 数据库原理
chapter: 存储引擎
difficulty: ADVANCED
tags: [数据库, LSM-Tree, LevelDB, RocksDB, 存储引擎]
aliases: [Log-Structured Merge-Tree, LSM, LevelDB]
source: "O'Neil et al. 1996 (LSM-Tree); LevelDB/RocksDB源码; Luo & Carey 2020 (LSM-based storage survey)"
updated_at: 2026-05-02
---

## 核心定义

LSM-Tree(Log-Structured Merge-Tree)是针对写密集型工作负载优化的存储结构。核心思想：将随机写转化为顺序写——新写入首先在内存排序缓冲区(MemTable,通常使用跳表skiplist实现)，写满后刷入磁盘形成不可变的有序文件(SSTable)。后台compaction(合并compaction)持续合并多层SSTable——删除重复键和已标记删除的记录。读操作需检查MemTable+最近的SSTable(通过bloom filter过滤不在的SSTable)+更深层的SSTable(因合并延迟)。

## Leveled vs Tiered

LSM合并策略分两大类：Tiered(分层合并——LevelDB/RocksDB,各层大小按倍数增长(level0:256MB,level1:1GB,level2:10GB...),一定大小触发compaction合并到下一层，读取最差需检查O(log N)个SSTable) vs Tiered(Tiered合并——Cassandra/ScyllaDB,合并一组SSTable成为一个更大的SSTable)。RocksDB(LevelDB的优化版)通过多线程compaction/压缩字典/prefix bloom filter实现极高性能——是许多现代数据库(TiKV/MyRocks/ArangoDB)的存储引擎。

## 关键结论

1. LSM-Tree牺牲读性能换取写性能——适合写密集型场景(日志/时序数据/IoT) 2. 写放大(write amplification)是LSM的主要代价——每个key可能因compaction被写多次 3. 读放大(read amplification)由需要搜索多层引起——bloom filter缓解但可能误报 4. Compaction的IO风暴(compaction storm)导致性能抖动——需要限速 5. B+树更适合读密集事务(OLTP)，LSM适合写密集日志和时序数据(特别是append-only场景)

## 关联知识点

[[数据库原理-索引B+树与哈希索引]] [[数据库原理-事务与并发控制]] [[操作系统-文件系统与IO基础]]
