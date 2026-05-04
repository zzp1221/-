---
title: Paxos协议详解
course: 分布式系统
chapter: 一致性协议
difficulty: ADVANCED
tags: [Paxos, 共识算法, 提案, 多数派, 一致性协议]
aliases: [Paxos, Basic Paxos, 基本Paxos, Lamport Paxos]
source:
  - "The Part-Time Parliament, Lamport (1998)"
  - "Paxos Made Simple, Lamport (2001)"
  - "Designing Data-Intensive Applications, Martin Kleppmann, Chapter 9"
  - "MIT 6.824: Distributed Systems"
updated_at: 2026-05-03
---

## 核心定义

Paxos是Leslie Lamport于1989年提出（1998年正式发表）的分布式共识算法，是分布式系统理论的基石。Paxos解决的问题是：在可能发生节点故障的异步分布式系统中，如何让多个节点就**单个值**达成一致。

Paxos包含三种角色（一个节点可以同时担任多个角色）：
- **Proposer（提案者）**：提出提案（提案号n, 值v）
- **Acceptor（接受者）**：对提案进行投票，决定是否接受
- **Learner（学习者）**：学习被选定的值

**两阶段过程**：

**Phase 1a: Prepare**：Proposer选择一个全局唯一且递增的提案号n，向多数派Acceptor发送 `Prepare(n)` 请求。

**Phase 1b: Promise**：Acceptor收到 `Prepare(n)` 后，如果n大于它已响应的所有Prepare请求的编号，则承诺不再接受编号小于n的提案，并返回它已接受的编号最高的提案（如果有的话）。

**Phase 2a: Accept**：Proposer收到多数派的Promise后，如果所有Promise中都没有已接受的提案，则Propose自己的值；否则，使用Promise中编号最高的提案的值。Proposer向多数派发送 `Accept(n, v)`。

**Phase 2b: Accepted**：Acceptor收到 `Accept(n, v)` 后，除非它已经响应了编号大于n的Prepare请求，否则接受该提案。

当多数派Acceptor接受了同一个提案，该值被**选定（chosen）**。

## 关键结论

- Paxos保证**安全性（safety）**——不会选定两个不同的值，但不保证**终止性（liveness）**——在活锁情况下可能无法选出值
- **活锁问题**：两个Proposer交替提出递增编号的提案，互相覆盖对方的Prepare请求，导致永远无法达成共识。解决方案：随机退避或选出Leader
- Paxos的正确性关键在于：**多数派交集性质**——任意两个多数派至少有一个共同的Acceptor，确保已选定的值不会被覆盖
- **Multi-Paxos**通过选举Leader减少Prepare阶段的开销，是实际应用中的常用形式
- Lamport的论文以古希腊Paxos岛的议会制度为隐喻，导致论文难以理解。后来的"Paxos Made Simple"用更直接的语言重新描述了算法

## 易错点

1. **忽视提案编号的全局唯一性要求**：提案编号必须全局唯一且单调递增，通常通过 `(节点ID, 递增序列号)` 的方式生成
2. **混淆"被接受"和"被选定"**：一个提案被单个Acceptor接受不等于被选定。只有被多数派Acceptor接受的提案才被选定
3. **误解Paxos的终止性保证**：Paxos只保证安全性（不做出错误决定），不保证终止性（在极端情况下可能无法达成共识）。这与FLP不可能定理一致——Paxos通过放弃确定性的终止保证来绕过FLP限制

## 例题

**题目**：在一个5节点的Paxos系统中，假设节点A、B、C、D、E都是Acceptor。Proposer1提出提案(1, "X")并获得A、B、C的接受。随后Proposer2提出提案(2, "Y")，开始Phase 1并获得B、C、D的Promise响应。请问Proposer2在Phase 2应该提议什么值？为什么？

**解答**：

Proposer2在Phase 2应该提议值 **"X"**。

**分析过程**：
1. Proposer2发送 `Prepare(2)` 给B、C、D、E（任意多数派）
2. B、C、D返回Promise响应
3. B和C之前接受了提案(1, "X")，D未接受过任何提案
4. 根据Paxos规则，Proposer2必须使用Promise中**编号最高的已接受提案的值**——即提案(1, "X")的值"X"
5. 因此Proposer2发送 `Accept(2, "X")` 给多数派

**为什么Paxos要求这个规则**：这是Paxos安全性的核心。如果Proposer2忽略已接受的提案而提议自己的值"Y"，就可能出现：A、B、C已经接受了"X"（已选定），而B、C、D又接受了"Y"——这违反了安全性。Paxos通过"继承"已接受的值来确保不会覆盖已被多数派接受的值。

## 关联页面

[[Multi-Paxos与日志复制]] [[Raft协议详解]] [[FLP不可能定理]] [[两阶段提交2PC]] [[ZAB协议（ZooKeeper）]]
