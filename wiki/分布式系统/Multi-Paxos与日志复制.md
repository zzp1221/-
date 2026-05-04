---
title: Multi-Paxos与日志复制
course: 分布式系统
chapter: 一致性协议
difficulty: ADVANCED
tags: [Multi-Paxos, 日志复制, Leader, 共识, 状态机复制]
aliases: [Multi-Paxos, 日志复制, Log Replication, State Machine Replication]
source:
  - "Paxos Made Simple, Lamport (2001)"
  - "Designing Data-Intensive Applications, Martin Kleppmann, Chapter 9"
  - "In Search of an Understandable Consensus Algorithm, Ongaro & Ousterhout (2014)"
updated_at: 2026-05-03
---

## 核心定义

Basic Paxos每次只能就一个值达成共识，效率很低。Multi-Paxos是Basic Paxos的扩展，通过一系列Paxos实例（slot）实现**日志复制**，从而支持**状态机复制（State Machine Replication, SMR）**——多个节点以相同的顺序执行相同的操作，保持状态一致。

**核心优化——Leader选举**：Multi-Paxos引入一个稳定的Leader，由Leader负责所有提案的提交。当Leader稳定时，可以跳过Phase 1（Prepare阶段），直接进入Phase 2（Accept阶段），将两阶段协议简化为一轮消息往返。

**日志结构**：每个节点维护一个日志序列，每个日志条目对应一个Paxos实例。日志条目包含：槽位号（slot number）、命令（command）、已选定的值。节点按顺序应用日志条目到状态机。

**日志复制流程**：
1. Client向Leader发送命令
2. Leader选择下一个空闲槽位，将命令作为该槽位的值进行Paxos共识
3. 共识达成后，Leader通知所有Follower该槽位的值
4. 所有节点按顺序应用日志到状态机
5. Leader返回结果给Client

**日志一致性保证**：Leader需要确保Follower的日志与自己一致。新Leader上任时，需要通过一个**日志同步（log synchronization）**过程来确定每个槽位已选定的值——这本质上是为每个未确定的槽位重新运行Paxos。

## 关键结论

- Multi-Paxos通过**Leader**将Basic Paxos的两阶段简化为一阶段（Leader稳定时），显著提升了性能
- Multi-Paxos的Leader是**拜占庭式的弱Leader**——Leader可能提出错误的值，但安全性由Acceptor保证（Acceptor可以拒绝过时的提案）
- 日志复制是**状态机复制**的核心：只要所有节点以相同顺序执行相同命令，它们的状态就会保持一致
- Multi-Paxos在工程实现中有许多变体，不同系统的实现细节差异很大（如Google的Chubby、Spanner）
- 日志的**压缩（compaction）**和**快照（snapshot）**是必要的优化，否则日志会无限增长

## 易错点

1. **混淆Multi-Paxos的Leader和Raft的Leader**：Multi-Paxos的Leader更弱——它不保证独占写入权，其他节点也可以同时提出提案（虽然实际中通常由Leader独占）
2. **忽视日志空洞（log holes）**：Multi-Paxos的日志可能有空洞——某个槽位可能还没有被选定。处理空洞需要额外的协议来填充
3. **高估跳过Phase 1的条件**：跳过Phase 1的前提是Leader稳定且没有其他节点在竞争。Leader切换或提案冲突时，仍需运行完整的两阶段

## 例题

**题目**：一个Multi-Paxos系统有5个节点，Leader为节点A。系统运行了很长时间，日志中有1000个槽位已被选定。此时节点A崩溃，节点B成为新Leader。节点B的日志有槽位1-998，缺少999和1000。节点C有槽位1-999，节点D有槽位1-1000。请问新Leader B如何确定槽位999和1000的值？

**解答**：

新Leader B需要对槽位999和1000分别运行**完整的Paxos两阶段**来确定它们的值。

**对于槽位1000**：
1. B发送 `Prepare(新编号)` 给多数派（如B、C、D、E）
2. D返回Promise，附带已接受的值（如果D已接受该槽位的值）
3. 如果多数派中有人接受了该值，B在Phase 2必须使用该值
4. B发送 `Accept(新编号, 值)` 给多数派
5. 如果多数派接受，该值被选定

**对于槽位999**：
1. 同样运行完整的Paxos两阶段
2. C返回Promise，附带已接受的值（如果C已接受了该值）
3. B继承该值进行Phase 2

**关键点**：即使槽位的值之前已经被选定，新Leader也需要重新运行Paxos来"学习"该值。这是Multi-Paxos保证安全性的机制——新Leader不能假设之前的值一定被选定了，必须通过Paxos来确认。

## 关联页面

[[Paxos协议详解]] [[Raft协议详解]] [[ZAB协议（ZooKeeper）]] [[GFS与HDFS]] [[数据复制策略]]
