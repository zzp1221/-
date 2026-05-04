---
title: Raft协议详解
course: 分布式系统
chapter: 一致性协议
difficulty: INTERMEDIATE
tags: [Raft, 共识算法, Leader选举, 日志复制, 安全性]
aliases: [Raft, Raft Consensus, Raft共识算法]
source:
  - "In Search of an Understandable Consensus Algorithm, Ongaro & Ousterhout (2014)"
  - "MIT 6.824: Distributed Systems"
  - "Designing Data-Intensive Applications, Martin Kleppmann, Chapter 5"
updated_at: 2026-05-03
---

## 核心定义

Raft是Diego Ongaro和John Ousterhout于2014年提出的共识算法，设计目标是比Paxos更易于理解，同时提供等价的安全性保证。Raft将共识问题分解为三个相对独立的子问题：**Leader选举**、**日志复制**和**安全性**。

**Leader选举**：Raft使用任期（term）机制，每个任期最多有一个Leader。节点状态为Follower、Candidate或Leader。当Follower在选举超时时间内未收到Leader心跳时，转变为Candidate，自增任期号并发起选举。Candidate向所有节点发送 `RequestVote` RPC，获得多数派投票后成为Leader。如果收到更高任期的消息，则退回为Follower。

**日志复制**：Client将命令发送给Leader，Leader将命令追加到本地日志，然后并发地向所有Follower发送 `AppendEntries` RPC。当多数派节点确认后，该日志条目被**提交（committed）**，Leader将结果应用到状态机并返回给Client。

**安全性保证**（五大关键特性）：
1. **选举安全**：每个任期最多一个Leader
2. **日志匹配**：如果两个日志在某索引处有相同的任期号，则该索引之前的所有条目也相同
3. **Leader完整性**：如果某日志条目在某任期被提交，则该条目出现在所有更高任期Leader的日志中
4. **状态机安全**：如果某节点在某索引应用了某条目，其他节点在该索引不会应用不同的条目
5. **Leader追加**：Leader永远不会覆盖或删除自己的日志，只追加

## 关键结论

- Raft通过**随机化选举超时**（如150-300ms）解决选举冲突，大幅减少了Paxos中的活锁问题
- Raft的Leader具有**强领导**特性——所有日志复制必须经过Leader，这简化了推理但限制了吞吐量
- **PreVote机制**可以防止网络分区中的节点不断自增任期号，避免分区恢复后扰乱当前Leader
- Raft的日志压缩通过**快照（snapshot）**实现——定期将已提交的日志截断，保存状态机快照
- Raft在工程中被广泛采用：etcd、CockroachDB、TiKV、Consul等都使用Raft作为共识层

## 易错点

1. **误认为提交等于应用**：日志条目被提交（commit）意味着已被多数派持久化，但还未应用（apply）到状态机。应用是异步进行的
2. **忽视Leader完整性是选举机制保证的**：Candidate在选举时必须检查自己的日志是否"足够新"——只有日志至少和多数派一样新的节点才能当选，这保证了Leader拥有所有已提交的日志条目
3. **混淆心跳和日志复制**：心跳本质上是不携带日志条目的 `AppendEntries` RPC。心跳的作用是维持Leader权威，防止Follower发起选举

## 例题

**题目**：一个Raft集群有5个节点（A、B、C、D、E），当前任期为3，A是Leader。A在日志索引5处复制了一个条目到A、B、C，然后A崩溃。随后D发起选举（任期4），获得了D和E的投票。

（1）D能否成为Leader？为什么？
（2）如果D成为了Leader，会发生什么？

**解答**：

**（1）D不能成为Leader。**

根据Raft的**选举限制（Election Restriction）**：Candidate的日志必须至少和多数派一样新。判断标准是：先比较最后日志条目的任期号，任期号大的日志更新；任期号相同则比较日志长度，长度大的更新。

- A的最后条目：任期3，索引5
- B的最后条目：任期3，索引5
- C的最后条目：任期3，索引5
- D的最后条目：假设任期3，索引4（或更少）

D的日志比A、B、C旧，而A、B、C构成多数派（3/5），因此D无法获得多数派投票。即使D和E投票给D，也只有2票，不构成多数派。

**（2）假设D错误地成为了Leader（比如A、B、C全部崩溃）**：

如果D成为Leader，它会尝试将自己的日志复制给其他节点。由于D的日志缺少索引5处的条目，而该条目已经被A、B、C多数派接受（已提交），D会覆盖已提交的条目——这违反了Raft的安全性保证。

但Raft的选举机制确保了这种情况不会发生：只有拥有所有已提交条目的节点才能获得多数派投票成为Leader。

## 关联页面

[[Paxos协议详解]] [[Multi-Paxos与日志复制]] [[ZAB协议（ZooKeeper）]] [[etcd与分布式KV]] [[数据复制策略]]
