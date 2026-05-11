---
title: "分布式快照Chandy-Lamport"
course: 分布式系统
chapter: 分布式协议
difficulty: ADVANCED
tags: [分布式系统, 快照, Chandy-Lamport, 一致性快照]
aliases: [Distributed Snapshot, Chandy-Lamport Algorithm, Consistent Cut]
source: "Chandy & Lamport 1985 (Distributed Snapshots); Verissimo & Rodrigues《Distributed Systems for System Architects》; Kshemkalyani & Singhal"
updated_at: 2026-05-02
---

## 核心定义

Chandy-Lamport算法(1985)在分布式系统中捕获一致全局快照(consistent global snapshot)而不中断系统——即记录在某个时刻各节点的状态和所有在途传输中的消息。核心假设：1.)信道是故障免费的FIFO(unidirectional,exactly-once) 2.)信道图连通。算法：快照发起者记录自己的状态后发送marker消息到所有传出信道；当节点首次接收到marker(在某个传入信道上)时，记录自己的状态、调用marker发送规则(发送marker到所有传出信道)并从该传入信道直到接收下一个channels的marker间记录所有消息(channel recording)。所有节点完成记录后快照完成。

## 一致切与意义

一致切(consistent cut)指快照中的事件集满足因果闭包——若事件e在快照中且f happens-before e则f也在快照中。Chandy-Lamport算法仅在实践中获取可检测为'垃圾'的空窗期(节点记录后的前置消息被遗漏——但因协议设定后置消息在稍后恢复)。Fidge/Mattern向量时钟(vector clocks)检测快照的因果一致性。分布式快照的应用：1.)死锁检测 2.)全局状态检测(debug) 3.)checkpoint/故障恢复(RRB/DFS的checkpoints) 4.)日志抽取(merge point in consistent snapshot) 5.)分布式垃圾回收。

## 关键结论

1. 一致快照不反映系统任何时刻的实际状态——它是组合多个时刻的近似(因果一致) 2. 非FIFO信道需要序列号包装成FIFO 3. 不需要停止系统——快照获取是偷窃式(stealthy) 4. 快照的开销主要是marker发送(O(diameter)时间)和channel recording存储(消息频次) 5. Chandy-Lamport是理解一致性、因果和分布式监控的理论基石(许多后续工作基础)

## 关联知识点

[[分布式系统-逻辑时钟与向量时钟]] [[分布式系统-分布式共识深度(Paxos/Raft对比)]] [[操作系统-虚拟内存与TLB]]
