---
title: ZAB协议（ZooKeeper）
course: 分布式系统
chapter: 一致性协议
difficulty: INTERMEDIATE
tags: [ZAB, ZooKeeper, 崩溃恢复, 消息广播, Leader选举]
aliases: [ZAB, ZooKeeper Atomic Broadcast, ZooKeeper原子广播]
source:
  - "A simple totally ordered broadcast protocol, Junqueira, Hunt, Konolige & Reed (2011)"
  - "ZooKeeper: Wait-free coordination for Internet-ready systems, Hunt et al. (2010)"
  - "Apache ZooKeeper Official Documentation"
updated_at: 2026-05-03
---

## 核心定义

ZAB（ZooKeeper Atomic Broadcast）是Apache ZooKeeper使用的原子广播协议，用于在分布式环境中实现高可用的协调服务。ZAB保证所有变更以**全序（total order）**的方式广播到所有节点，即使在Leader切换期间也不会丢失已确认的事务。

ZAB协议包含两个主要阶段：

**崩溃恢复（Recovery / Leader Election）**：当系统启动或Leader失效时，进入崩溃恢复阶段。节点通过**ZXID**（事务ID，由epoch和计数器组成）选举拥有最新数据的节点为新Leader。新Leader确定后，收集所有Follower的数据状态，确保所有节点同步到最新的已提交事务。只有当多数派节点完成同步后，新Leader才能开始广播阶段。

**消息广播（Broadcast）**：类似两阶段提交（2PC），但简化为单向流程。Leader为每个事务分配ZXID，将事务提案发送给所有Follower。Follower写入本地日志后返回ACK。当Leader收到多数派的ACK后，发送COMMIT给所有Follower。

**ZXID结构**：ZXID是64位整数，高32位是epoch（Leader任期），低32位是该epoch内的事务计数。新Leader选举时epoch递增，这确保了不同Leader的ZXID全局有序。

**与Raft的对比**：ZAB和Raft非常相似（都使用Leader+日志复制），但有关键区别：ZAB的epoch对应Raft的term，ZXID对应Raft的(index, term)，ZAB的恢复阶段比Raft更复杂（需要同步所有未提交的事务）。

## 关键结论

- ZAB保证**已提交的事务不丢失**：一旦多数派ACK了事务，即使Leader切换，该事务也不会丢失
- ZAB的**全序保证**：所有事务按ZXID的顺序广播，所有Follower以相同顺序应用
- ZAB的恢复阶段确保**新Leader拥有所有已提交事务**：通过比较ZXID，选出数据最新的节点作为Leader
- ZooKeeper使用ZAB实现**线性一致性写**和**顺序一致性读**（通过Follower转发读请求到Leader，或使用 `sync()` 操作）
- ZAB与Multi-Paxos、Raft属于同一类协议（Leader-based consensus），核心思想一致

## 易错点

1. **混淆ZAB和Paxos**：虽然都解决共识问题，但ZAB的设计目标是**原子广播**（按顺序广播一系列值），而Paxos的设计目标是就**单个值**达成一致。Multi-Paxos通过多个Paxos实例实现日志复制，与ZAB更接近
2. **忽视ZAB的恢复阶段复杂性**：新Leader不能立即开始广播，需要先完成同步。在同步期间，系统对外不可用（不可写）
3. **误解ZooKeeper的一致性保证**：ZooKeeper的读操作默认是**最终一致性**的（从本地副本读取），只有通过 `sync()` + 读操作才能获得**线性一致性**读

## 例题

**题目**：一个ZooKeeper集群有5个节点，当前Leader是节点A（epoch=3）。A处理了以下事务：ZXID=3,1到3,5。A将3,1到3,4广播给所有节点并获得多数派ACK，但3,5只获得了A和B的ACK。此时A崩溃，请问新Leader选举时，哪个节点应该成为新Leader？新Leader的epoch是什么？事务3,4和3,5的命运分别是什么？

**解答**：

**新Leader选举**：比较各节点的最新ZXID。
- 节点A：3,5（已崩溃，不参与选举）
- 节点B：3,5（收到了3,5的ACK）
- 节点C、D、E：最新到3,4

节点B的ZXID最大（3,5），但3,5只获得了2个ACK（A和B），未构成多数派（需要3个），因此3,5未被提交。B仍可能成为新Leader（因为其数据最新），但需要在恢复阶段处理未提交的3,5。

**新Leader的epoch**：新Leader（B）的epoch为 **4**（旧epoch 3 + 1）。

**事务命运**：
- **3,4**：已被多数派（如A、B、C、D、E中的至少3个）ACK，已提交，不会丢失。新Leader B会确保所有节点都收到3,4。
- **3,5**：只有A和B的ACK（2个），未构成多数派，未提交。新Leader B在恢复阶段需要决定是否继续提交3,5。通常的做法是：如果新Leader有3,5，则继续广播并尝试获得多数派ACK；如果无法获得，则丢弃该事务。

## 关联页面

[[Paxos协议详解]] [[Raft协议详解]] [[ZooKeeper原理与应用]] [[Multi-Paxos与日志复制]] [[数据复制策略]]
