---
title: GFS与HDFS
course: 分布式系统
chapter: 分布式存储
difficulty: INTERMEDIATE
tags: [GFS, HDFS, 分布式文件系统, 数据块, 主从架构]
aliases: [Google File System, Hadoop Distributed File System, 分布式文件系统]
source:
  - "The Google File System, Ghemawat, Gobioff & Leung (2003)"
  - "HDFS Architecture Guide, Apache Hadoop Documentation"
  - "Designing Data-Intensive Applications, Martin Kleppmann, Chapter 10"
updated_at: 2026-05-03
---

## 核心定义

GFS（Google File System）是Google于2003年发表的分布式文件系统论文，HDFS（Hadoop Distributed File System）是其开源实现。两者采用相似的架构，专为**大规模数据处理**（如MapReduce）优化。

**架构组件**：
- **Master/NameNode**：管理文件系统的元数据（文件名、目录结构、块到ChunkServer/DataNode的映射），是系统的中心节点
- **ChunkServer/DataNode**：存储实际的数据块。文件被分成固定大小的块（GFS为64MB，HDFS默认128MB），每个块默认保存3个副本

**写入流程**：
1. Client向Master请求持有该块的ChunkServer列表
2. Client将数据推送到所有副本（链式推送）
3. Client发送写请求到**主副本（primary）**
4. Primary确定写入顺序，通知所有Secondary副本
5. 所有副本完成后，Primary回复Client

**一致性模型**：GFS提供**松弛的一致性**（relaxed consistency）——不保证所有副本完全一致，可能出现重复记录和不一致。这简化了设计，但要求应用层处理。

**Master的高可用**：Master是单点，通过**操作日志（operation log/checkpoint）**持久化元数据。HDFS引入了**Standby NameNode**和**JournalNode**实现NameNode的高可用（HA）。

## 关键结论

- GFS/HDFS的设计目标是**高吞吐量**而非低延迟，适合**大文件顺序读写**，不适合大量小文件
- **大块大小**（64MB/128MB）的设计是为了减少Master的元数据量和客户端与Master的交互次数
- **主副本（Primary）**负责确定写入顺序，解决了并发写入的一致性问题
- GFS的一致性模型是**最终一致性**的变体——记录可能重复、不同副本可能不一致
- HDFS的**NameNode HA**通过主备切换实现，**Federation**通过多个NameNode管理不同命名空间实现水平扩展

## 易错点

1. **误认为GFS/HDFS适合所有场景**：GFS/HDFS专为大文件顺序读写优化，不适合低延迟的随机读写（如HBase需要HDFS但有自己的存储层）
2. **忽视小文件问题**：每个文件在NameNode中约占150字节元数据，大量小文件会导致NameNode内存溢出。解决方案包括：HAR归档、SequenceFile合并
3. **混淆GFS的一致性与强一致性**：GFS的松弛一致性意味着应用需要处理重复记录和不一致，这与数据库的强一致性完全不同

## 例题

**题目**：一个HDFS集群有1个NameNode和1000个DataNode，文件大小为1TB，块大小为128MB，副本因子为3。请计算：
（1）文件被分成多少个块？
（2）系统中总共有多少个块（含副本）？
（3）NameNode需要管理多少个块映射关系？

**解答**：

**（1）文件块数**：
- 文件大小：1TB = 1024 × 1024 MB = 1,048,576 MB
- 块大小：128MB
- 块数：1,048,576 / 128 = **8192个块**

**（2）总块数（含副本）**：
- 副本因子：3
- 总块数：8192 × 3 = **24576个块**

**（3）NameNode管理的映射关系**：
- NameNode需要管理的映射关系包括：
  - 文件到块的映射：文件被分成8192个块，所以有8192个映射
  - 块到DataNode的映射：每个块有3个副本，分布在不同的DataNode上
- 但NameNode**不持久化**块到DataNode的映射——它通过DataNode的**心跳报告**在内存中维护
- 持久化的元数据：文件名、文件大小、块列表（8192个块ID）
- 内存中的元数据：每个块对应的3个DataNode位置

**元数据大小估算**：
- 每个文件元数据约150字节
- 每个块元数据约150字节
- 总内存：8192 × 150 ≈ 1.2MB（非常小）
- 实际系统中，NameNode内存瓶颈来自**大量小文件**，而非少量大文件

## 关联页面

[[MapReduce编程模型]] [[Bigtable与HBase]] [[数据复制策略]] [[数据分片与哈希取模]] [[Spark核心原理]]
