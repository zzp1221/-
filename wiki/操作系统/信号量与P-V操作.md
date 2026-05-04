---
title: "信号量与P-V操作"
course: 操作系统
chapter: 同步与互斥
difficulty: INTERMEDIATE
tags: [操作系统, 信号量, PV操作, Dijkstra, 同步]
aliases: [Semaphore]
source: "Cooperating Sequential Processes (Dijkstra 1965); Operating System Concepts (Silberschatz) 第6章"
updated_at: 2026-05-02
---

## 核心定义

信号量是Dijkstra提出的经典同步原语。结构：整型计数器+等待队列。P操作(wait/proberen)：先减1，若<0则进程阻塞加入等待队列。V操作(signal/verhogen)：加1，若≤0则唤醒等待队列中的一个进程。二元信号量计数=0或1（等价于互斥锁）。计数信号量可控制多资源并发访问。

## 关键结论

1. P/V必须是原子操作（关中断或使用硬件原子指令）2. 信号量vs互斥锁：信号量可用作条件同步（生产者-消费者）3. 信号量编程易错：顺序错误、遗忘V操作、死锁 4. POSIX信号量：sem_wait/sem_post，System V信号量功能更强但API复杂

## 关联页面

[[临界区]] [[互斥与同步机制]] [[生产者消费者问题]] [[自旋锁与互斥锁对比]]
