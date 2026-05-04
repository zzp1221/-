---
title: Cassandra与Dynamo
course: 分布式系统
chapter: 分布式存储
difficulty: INTERMEDIATE
tags: [Cassandra, Dynamo, AP系统, 最终一致性, 无主复制, Gossip]
aliases: [Apache Cassandra, Amazon Dynamo, Dynamo风格, 最终一致性存储]
source:
  - "Dynamo: Amazon's Highly Available Key-value Store, DeCandia et al. (2007)"
  - "Apache Cassandra Documentation"
  - "Designing Data-Intensive Applications, Martin Kleppmann, Chapter 5 & 6"
updated_at: 2026-05-03
---

## 核心定义

Dynamo是Amazon于2007年发表的分布式KV存储论文，Cassandra是Facebook开源的分布式数据库（受Dynamo和Bigtable双重影响）。两者都属于**AP系统**（可用性优先），提供**最终一致性**。

**Dynamo的核心技术**：
- **一致性哈希**：数据分布在哈希环上，每个节点负责一段区间
- **虚拟节点**：每个物理节点映射多个虚拟节点，实现负载均衡
- **Quorum机制**：通过W+R>N配置一致性级别（W=写入副本数，R=读取副本数，N=总副本数）
- **向量时钟**：检测数据冲突
- **反熵协议（Anti-Entropy）**：使用Merkle Tree检测副本差异
- **Gossip协议**：节点间传播成员和状态信息
- **Hinted Handoff**：临时将写入转发到其他节点，待目标节点恢复后再转交

**Cassandra的架构**：
- **去中心化**：所有节点对等（无主节点），使用Gossip协议进行节点发现和故障检测
- **数据模型**：宽列存储（类似Bigtable），支持CQL（类似SQL的查询语言）
- **可调一致性**：用户可以在每次查询中指定一致性级别（ONE, QUORUM, ALL等）
- **LSM-Tree存储引擎**：写入性能高，后台Compaction合并数据

**冲突解决**：Dynamo使用**向量时钟**检测冲突，交给应用层解决；Cassandra使用**最后写入获胜（LWW）**，基于时间戳自动解决冲突（可能丢失更新）。

## 关键结论

- Dynamo/Cassandra是**AP系统**的典型代表，优先保证可用性，接受最终一致性
- **LWW（Last Write Wins）**简单但可能丢失并发更新——这是Cassandra的设计取舍
- Cassandra的**可调一致性**允许用户在一致性、可用性和延迟之间灵活选择
- **Gossip协议**是无中心架构的核心——每个节点定期随机选择其他节点交换状态信息
- Cassandra适合**写多读少**、**高可用**、**跨数据中心**的场景，如时间序列数据、日志存储、IoT数据

## 易错点

1. **误认为Cassandra永远不一致**：通过设置QUORUM或ALL一致性级别，Cassandra可以提供强一致性，但会牺牲可用性和延迟
2. **忽视LWW的数据丢失风险**：在并发写入场景下，LWW可能丢失更新。如果业务需要保留所有更新，应使用CRDT或应用层冲突解决
3. **混淆Cassandra和关系型数据库**：Cassandra虽然支持CQL，但不支持JOIN、事务（单行原子操作除外）、外键等关系型特性。数据建模需要按查询模式设计（Query-Driven）

## 例题

**题目**：一个Cassandra集群有5个副本，副本因子N=3。执行一个写入操作，一致性级别设为QUORUM。

（1）需要多少个副本确认才算写入成功？
（2）如果此时读取一致性级别设为ONE，能否保证读到最新数据？
（3）如果读取一致性级别设为QUORUM，能否保证读到最新数据？

**解答**：

**（1）QUORUM写入需要的确认数**：
- QUORUM = ⌊N/2⌋ + 1 = ⌊3/2⌋ + 1 = 2
- 需要至少2个副本确认写入才算成功

**（2）读取ONE能否保证最新数据**：
- W=2, R=1, N=3
- W + R = 2 + 1 = 3 = N，**不满足** W + R > N
- **不能保证**读到最新数据。读操作可能从一个未收到最新写入的副本读取

**（3）读取QUORUM能否保证最新数据**：
- W=2, R=2, N=3
- W + R = 2 + 2 = 4 > N = 3，**满足** W + R > N
- **能保证**读到最新数据。写入的2个副本和读取的2个副本至少有1个重叠（鸽巢原理）

**总结**：
| 配置 | W | R | W+R | 是否一致 |
|------|---|---|-----|---------|
| ONE/ONE | 1 | 1 | 2 | 否 |
| QUORUM/ONE | 2 | 1 | 3 | 否 |
| QUORUM/QUORUM | 2 | 2 | 4 | 是 |
| ALL/ONE | 3 | 1 | 4 | 是 |

## 关联页面

[[一致性哈希]] [[数据复制策略]] [[分布式时间与向量时钟]] [[CAP定理详解]] [[一致性模型（强/最终/因果）]]
