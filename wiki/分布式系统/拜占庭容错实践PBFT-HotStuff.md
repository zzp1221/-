---
title: "拜占庭容错实践(PBFT/HotStuff)"
course: 分布式系统
chapter: 共识协议
difficulty: ADVANCED
tags: [分布式系统, 拜占庭容错, PBFT, HotStuff, BFT]
aliases: [Byzantine Fault Tolerance, PBFT, HotStuff, BFT]
source: "Castro & Liskov 1999 (PBFT); Yin et al. 2019 (HotStuff); Buchman 2016 (Tendermint); LibraBFT"
updated_at: 2026-05-02
---

## 核心定义

拜占庭容错(BFT)处理节点可能恶意行为(不仅仅是崩溃)的共识——以拜占庭将军问题命名(Lamport 1982)。经典的PBFT(Practical Byzantine Fault Tolerance, 1999)是第一个实用的BFT协议，容错f个恶意节点需n>=3f+1个总节点。PBFT三阶段：pre-prepare(leader分发proposal)→prepare(节点广播prepare确认,收集到2f matching prepare消息→进入committed)→commit(广播commit,收集到2f+1 commit→本地执行)。View change在leader故障时更换leader。HotStuff(2019,Libra Diem采用的协议)线性化了leader-based流程——允许只有一个leader消息触发共识。

## HotStuff与区块链共识

HotStuff的核心创新：1.)三次消息交换(准备prepare→预提交pre-commit→提交commit)——leader收集回应后发给followers{ack, nack, or timeout} 2.)Pipelining——每个块同时处于各不同阶段(一个块的commit阶段=下一块的pre-commit,第三个块的prepare)——提升吞吐量 3.)线性视图切换(所有节点在super-majority下就leader更换达成一致)。Tendermint(基于PBFT共识引擎+app interface ABCI)在Cosmos network中使用。

## 关键结论

1. PBFT的O(n^2)消息复杂度限制了网络规模(通常<=20-100节点) 2. HotStuff降低消息复杂度到O(n)——使得BFT在数百节点规模可行 3. BFT共识需要同时考虑活性(liveness——最终达成共识)和安全性(safety——一旦共识不过期) 4. 对于crash-only系统——Paxos/Raft(CFT)已足够(降低复杂性) 5. 证明BFT在面对非确定性恶意行为时的正确性很有挑战——需模型检测和形式化证明

## 关联知识点

[[分布式系统-分布式共识深度(Paxos/Raft对比)]] [[分布式系统-CAP定理与一致性模型]] [[信息安全-密码学基础]]
