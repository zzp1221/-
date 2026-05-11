---
title: "分布式共识深度(Paxos/Raft对比)"
course: 分布式系统
chapter: 共识协议
difficulty: ADVANCED
tags: [分布式系统, Paxos, Raft, 共识, 一致性]
aliases: [Distributed Consensus, Paxos vs Raft, Multi-Paxos]
source: "Lamport 1998 (Paxos Made Simple); Ongaro & Ousterhout 2014 (Raft); Howard 2019 (Paxos vs Raft survey)"
updated_at: 2026-05-02
---

## 核心定义

分布式共识(distributed consensus)要求多个节点在某个提案上达成一致。Paxos(Lamport)是共识协议的理论基础——分两阶段：Phase 1(Prepare——Proposer发起proposal number→获得多数Acceptor的promise不处理更低编号)和Phase 2(Accept——Proposer发送value→多数Acceptor accept)。Raft(Ongaro)以可理解性为设计目标——通过强领导(strong leader)和受限行为减少状态空间。核心子问题：领导人选举(Leader Election——获得多数vote)、日志复制(Log Replication——Leader强制follower复制日志)、安全性(arg)。

## Paxos vs Raft对比

根本结构差异：Raft的领导人时刻保证独自接收写(leader-centric——任何日志entry都必须通过leader转述)， Paxos的提案可来自任何节点(every node can propose——但实际多用stable leader即Multi-Paxos)。Raft的日志不空洞(entry必须索引连续——index+term唯一标识)，Multi-Paxos允许日志空洞(需要单独填补——view stamping优化)。成员变更：Raft使用joint consensus(两个配置重叠——新配置和老配置交换)保证安全性(中间无需多个阶段)，Paxos需要考虑更多。Raft的"可理解"设计已成为工业界分布式系统的首选入门。

## 关键结论

1. Paxos难以实现正确(历史中很多系统打着Paxos旗号实际有bug——e.g. Google Chubby) 2. Raft的可理解性大大缩短了开发人员从阅读论文到正确实现的时间(~1-2个月 vs ~>4个月) 3. 两个协议都在leader failure时产生短暂不可用(~选举时间) 4. 两者都是crash fault tolerant(CFT——非拜占庭) 5. 大多数生产级raft实现(etcd/hashicorp raft/TiKV)在基本raft上扩展了pipelining和batch + witness/snapshot

## 关联知识点

[[分布式系统-拜占庭容错实践(PBFT/HotStuff)]] [[分布式系统-CAP定理与一致性模型]] [[分布式系统-分布式快照Chandy-Lamport]]
