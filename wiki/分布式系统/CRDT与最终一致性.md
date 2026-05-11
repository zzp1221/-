---
title: "CRDT与最终一致性"
course: 分布式系统
chapter: 一致性模型
difficulty: ADVANCED
tags: [分布式系统, CRDT, 最终一致性, 无冲突复制]
aliases: [Conflict-free Replicated Data Types, CRDT, Eventual Consistency]
source: "Shapiro et al. 2011 (CRDTs); Brewer 2000 (CAP); Terry et al. 1995 (Eventual Consistency); Dynamo paper"
updated_at: 2026-05-02
---

## 核心定义

CRDT(Conflict-free Replicated Data Types,无冲突复制数据类型)是在分布式系统中无需协调(synchronization)即可并发的可复制数据结构——合并操作commutative、associative且idempotent保证最终一致性无冲突。两大类型：基于操作的CRDT(op-based——操作在发出端应用然后重传到其他replica)和基于状态的CRDT(state-based——定期merge state,要求merge是set的least-upper-bound在预定义的semilattice上)。经典CRDT：G-Counter(增长计数器——各自维护vector,sum合局值), PN-Counter(正负计数器), G-Set(只增集合), OR-Set(观察消除集合——tombstone追踪删除)。

## 实际应用

CRDT在协同编辑(Google Docs style——YATA/Logoot/RGA算法处理文本插入序列)和分布数据库(AntidoteDB/Riak)中找到应用。Delta state CRDT缩减合并了的state大小(只传输变化部分而非整个state)。ORMap(Observed-Remove Map)追踪因果关系以删除不再引用的tombstones。本地优先软件(local-first software)使用CRDT在所有设备上无服务器协同。数据库中的最终一致性(KV stores——Dynamo/Cassandra)通过CRDT或LWW(Last-Writer-Wins)解决并发更新冲突。

## 关键结论

1. CRDT消除分布式系统中'协商解决冲突'的需要(自动merging——无需交互协议) 2. 操作CRDT要求可靠的因果广播(causal broadcast)——底层更多假设 3. CRDT的元数据(tombstones/clocks)随时间增长(需要压缩garbage collection) 4. CRDT不能保留某些invariant——全局唯一值/order invariant需要额外机制 5. CRDT+Actor模型(如Elixir)给出无锁分布的近乎理想方案

## 关联知识点

[[分布式系统-CAP定理与一致性模型]] [[分布式系统-分布式共识深度(Paxos/Raft对比)]] [[数据库原理-事务与并发控制]]
