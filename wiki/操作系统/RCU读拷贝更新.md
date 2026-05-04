---
title: "RCU（读拷贝更新）"
course: 操作系统
chapter: 并发控制
difficulty: ADVANCED
tags: [操作系统, RCU, 并发控制, 锁自由, Linux内核]
aliases: [Read-Copy-Update]
source: "Linux Kernel Documentation (RCU); McKenney RCU论文"
updated_at: 2026-05-02
---

## 核心定义

RCU是Linux内核中使用的无锁并发机制，专为读多写少场景优化。写操作不直接修改原数据，而是先复制→修改→在适当时机替换指针→等待所有老读者完成后释放旧数据。读者完全不阻塞无需获取锁。关键API：rcu_read_lock/unlock标记读临界区、synchronize_rcu等待所有老读完成、call_rcu异步回调释放。

## 关键结论

1. 读者开销几乎为零（只是禁抢占）2. 写者需要等待宽限期(Grace Period) 3. Linux内核中广泛使用（网络栈、文件系统、VFS）4. 不适合写多场景

## 关联页面

[[临界区]] [[互斥与同步机制]] [[锁自由数据结构]]
