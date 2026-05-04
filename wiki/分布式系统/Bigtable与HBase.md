---
title: Bigtable与HBase
course: 分布式系统
chapter: 分布式存储
difficulty: INTERMEDIATE
tags: [Bigtable, HBase, 列族, LSM-Tree, SSTable, 分布式数据库]
aliases: [Bigtable, HBase, 列族存储, Wide Column Store]
source:
  - "Bigtable: A Distributed Storage System for Structured Data, Chang et al. (2006)"
  - "HBase Reference Guide, Apache HBase Documentation"
  - "Designing Data-Intensive Applications, Martin Kleppmann, Chapter 3"
updated_at: 2026-05-03
---

## 核心定义

Bigtable是Google于2006年发表的分布式列族存储系统，HBase是其开源实现。Bigtable被设计用来管理**PB级结构化数据**，广泛应用于Google的搜索索引、Gmail、Google Maps等服务。

**数据模型**：Bigtable的数据模型是一个**稀疏的、分布式的、持久化的多维有序映射**。数据通过 `(row_key, column_family:qualifier, timestamp)` 三元组寻址，每个单元格存储一个值。

- **行键（Row Key）**：按字典序排列，范围分片（每个Tablet包含一个行键范围）
- **列族（Column Family）**：数据按列族存储和压缩，列族需预定义
- **时间戳（Timestamp）**：支持多版本数据，可配置保留策略

**存储引擎**：基于**LSM-Tree（Log-Structured Merge Tree）**：
1. 写入先到**MemTable**（内存中的有序结构）
2. MemTable满后刷写到**SSTable**（磁盘上的有序不可变文件）
3. 后台**Compaction**合并多个SSTable，减少读放大

**架构**：
- **Master**：分配Tablet给TabletServer，处理Schema变更
- **TabletServer**：管理Tablet（行键范围分区），处理读写请求
- **底层存储**：GFS/HDFS存储SSTable文件，Chubby/ZooKeeper用于分布式锁和Master选举

## 关键结论

- LSM-Tree的**写入性能极高**（顺序写入），但**读取可能较慢**（需要查找多个SSTable），通过Bloom Filter优化
- Bigtable/HBase适合**写多读少**、**大量数据**、**需要强一致性**的场景
- **Compaction策略**对性能影响重大：Minor Compaction合并小SSTable，Major Compaction合并所有SSTable
- HBase的行键设计至关重要——**热点问题**（所有写入集中在少数Region）需要通过行键设计（加盐、反转、哈希）来避免
- Bigtable的一致性保证：**单行操作是原子的**（行级事务），跨行操作无事务保证

## 易错点

1. **误认为Bigtable支持复杂查询**：Bigtable/HBase只支持按行键的点查询和范围扫描，不支持SQL的JOIN、聚合等操作。需要二级索引来支持非主键查询
2. **忽视LSM-Tree的写放大问题**：虽然写入性能高，但Compaction会导致数据被多次重写（写放大），影响磁盘寿命和性能
3. **行键设计不当导致热点**：如果使用时间戳作为行键前缀，所有写入会集中在最新的Region上，导致热点。应该使用反转时间戳或哈希

## 例题

**题目**：一个HBase集群存储用户行为日志，行键设计为 `{user_id}_{timestamp}`。随着数据增长，发现写入性能持续下降。请分析原因并提出优化方案。

**解答**：

**问题分析**：

使用 `{user_id}_{timestamp}` 作为行键时，如果大部分用户集中在少数几个活跃用户（如大V），这些用户的日志会集中在少数几个Region上，导致：
- **Region热点**：少数Region承载了大部分写入
- **Compaction压力**：热点Region的SSTable增长快，频繁触发Compaction
- **写入阻塞**：热点Region的MemTable频繁刷写，影响写入性能

**优化方案**：

**方案一：行键加盐（Salting）**
- 在行键前添加随机前缀：`{salt}_{user_id}_{timestamp}`
- salt范围为0-9，将数据分散到10个Region
- 缺点：范围查询需要扫描多个salt前缀

**方案二：反转user_id**
- 行键设计为 `{reverse(user_id)}_{timestamp}`
- 将相似的user_id分散到不同Region

**方案三：使用哈希前缀**
- 行键设计为 `MD5(user_id)[0:2]}_{user_id}_{timestamp}`
- 哈希前缀确保数据均匀分布
- 查询时先计算哈希前缀，再进行范围扫描

**推荐方案**：使用**哈希前缀**，在均匀分布和查询效率之间取得平衡。同时优化Compaction策略（如使用FIFO Compaction删除过期日志）。

## 关联页面

[[GFS与HDFS]] [[数据分片与哈希取模]] [[MapReduce编程模型]] [[Cassandra与Dynamo]] [[Spanner与TrueTime]]
