---
title: "CAP定理与BASE理论"
course: 数据库原理
chapter: 分布式数据库
difficulty: INTERMEDIATE
tags: [数据库, CAP, BASE, 分布式, 一致性]
aliases: [CAP Theorem, BASE]
source: "Towards Robust Distributed Systems (Brewer 2000); CAP Proof (Gilbert & Lynch 2002)"
updated_at: 2026-05-02
---

## 核心定义

CAP定理：分布式系统在网络分区(P)发生时，只能在一致性(C)和可用性(A)之间二选一。CP系统(MongoDB/HBase/ZooKeeper)：分区时选一致性，可能拒写。AP系统(Cassandra/DynamoDB/CouchDB)：分区时选可用性，允许短暂不一致。CA在分布式系统中不存在（网络分区不可避免）。BASE理论（Basically Available + Soft-state + Eventually consistent）：AP系统的设计理念，牺牲强一致性换取高可用，最终达到一致性。

## 关键结论

1. CAP的C是强一致性(线性一致性)，不是最终一致性 2. 实际系统是连续性而非二元选择（在C和A之间调参）3. PACELC是对CAP的补充：分区时选A或C，正常时选L(latency)或C(consistency)

## 关联页面

[[NoSQL数据库对比]] [[分布式一致性协议]] [[Raft与Paxos]]
