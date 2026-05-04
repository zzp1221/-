---
title: Spanner与TrueTime
course: 分布式系统
chapter: 分布式存储
difficulty: ADVANCED
tags: [Spanner, TrueTime, 全球分布式数据库, 外部一致性, GPS时钟]
aliases: [Google Spanner, TrueTime, 外部一致性, External Consistency]
source:
  - "Spanner: Google's Globally-Distributed Database, Corbett et al. (2012)"
  - "Spanner, TrueTime and the CAP Theorem, Google (2016)"
  - "Designing Data-Intensive Applications, Martin Kleppmann, Chapter 7 & 9"
updated_at: 2026-05-03
---

## 核心定义

Spanner是Google于2012年发表的全球分布式数据库，是第一个在全球范围提供**强一致性**（外部一致性）的分布式数据库。Spanner的创新之处在于使用**TrueTime API**来解决分布式系统中的时钟不确定性问题。

**TrueTime API**：TrueTime返回的不是精确的时间点，而是一个**置信区间** `[earliest, latest]`，保证真实时间在此区间内。TrueTime使用GPS和原子钟来校准各数据中心的时钟，将时钟误差控制在**7ms以内**（通常1-4ms）。

```python
TT.now() -> TTinterval: [earliest, latest]
```

**外部一致性（External Consistency）**：比线性一致性更强。如果事务T1在物理时间上先于T2提交，则T1的时间戳小于T2。这保证了全球范围内的因果一致性。

**Spanner的实现**：
- 使用**Paxos**进行数据复制（每个分片/Paxos Group一个Paxos实例）
- 读写事务使用**2PC + Paxos**：跨分片事务通过2PC协调，每个分片通过Paxos保证可用性
- 事务时间戳通过TrueTime分配，利用**提交等待（commit wait）**机制保证外部一致性——提交时等待直到时间戳的不确定性窗口过去

**Commit Wait机制**：事务T提交时，选择时间戳 `s = TT.now().latest`，然后等待直到 `TT.now().earliest > s`。这确保了在T的提交对其他事务可见时，物理时间已经过了s，从而保证外部一致性。

## 关键结论

- Spanner通过**TrueTime + Commit Wait**实现了**外部一致性**，这是CAP定理的一个优雅的工程解——在正常运行时同时提供C和A
- TrueTime的关键是**有界时钟不确定性**——通过GPS和原子钟将误差控制在毫秒级
- Spanner的**读写事务**使用2PC+Paxos（强一致性），**只读事务**可以无锁读取（使用快照时间戳）
- Spanner证明了**时间**可以作为分布式系统中实现强一致性的关键工具
- CockroachDB和TiDB是Spanner的开源模仿者，但使用HLC（混合逻辑时钟）替代TrueTime

## 易错点

1. **忽视TrueTime的物理基础设施要求**：TrueTime依赖GPS接收器和原子钟，每个数据中心需要部署专门的硬件。这是Spanner难以被其他公司复制的根本原因
2. **误认为Spanner完全避免了CAP的权衡**：Spanner在网络分区时仍需在C和A之间选择。TrueTime只是缩小了不确定窗口，没有消除它
3. **混淆外部一致性与线性一致性**：外部一致性是关于**事务提交顺序**的保证（与物理时间一致），线性一致性是关于**单对象操作**的实时性保证

## 例题

**题目**：在Spanner中，事务T1在物理时间10:00:00.000提交，事务T2在物理时间10:00:00.005提交。TrueTime的时钟不确定性为5ms。请问：

（1）Spanner如何保证外部一致性？
（2）T1和T2的时间戳关系是什么？

**解答**：

**（1）Spanner通过Commit Wait机制保证外部一致性**：

当T1在物理时间10:00:00.000提交时：
1. T1选择时间戳 `s1 = TT.now().latest`
2. 假设此时TT.now() = [9:59:59.998, 10:00:00.003]，则s1 = 10:00:00.003
3. T1等待直到 `TT.now().earliest > 10:00:00.003`
4. 这意味着物理时间已经过了10:00:00.003，T1的提交才对外可见

当T2在物理时间10:00:00.005提交时：
1. T2选择时间戳 `s2 = TT.now().latest`
2. 此时TT.now() = [10:00:00.003, 10:00:00.008]，则s2 = 10:00:00.008
3. T2等待直到 `TT.now().earliest > 10:00:00.008`

**（2）时间戳关系**：

由于T1的Commit Wait确保了在T1可见时物理时间已过10:00:00.003，而T2在物理时间10:00:00.005才提交（晚于T1可见的时间），因此：

- s1 < s2（T1的时间戳小于T2）
- 外部一致性保证：如果T1在物理时间上先于T2提交，则T1的时间戳小于T2

Commit Wait的代价是引入了约5ms的延迟（时钟不确定性窗口），但这换来了全球范围的强一致性保证。

## 关联页面

[[Paxos协议详解]] [[两阶段提交2PC]] [[一致性模型（强/最终/因果）]] [[分布式时间与向量时钟]] [[Bigtable与HBase]]
