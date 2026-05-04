---
title: Snooping协议
course: 计算机组成原理
chapter: 第八章 多核处理器
difficulty: ADVANCED
tags: [Snooping, 监听协议, Cache一致性, 总线监听, 写无效, 写更新]
aliases: [Snooping Protocol, Bus Snooping, 总线监听协议]
source:
  - Patterson & Hennessy, Computer Organization and Design
  - Sorin, Hill & Wood, A Primer on Memory Consistency and Cache Coherence
updated_at: 2026-05-02

---

## 核心定义

Snooping 协议（总线监听协议 / Bus Snooping Protocol）是实现 Cache 一致性的经典方式之一，广泛用于基于总线的对称多处理器（SMP）系统。其核心思想是每个 Cache 控制器持续"监听"（Snoop）共享总线上的所有事务（缓存行读/写/失效请求），当检测到与自己缓存数据相关的总线事务时，根据一致性协议（如 MESI）更新本地 Cache 行的状态或向数据请求方提供最新的数据副本。Snooping 协议分为两类：写无效协议（Write-Invalidate Protocol）——当处理器要写入一个被共享的 Cache 行时，在总线上发送无效化消息，使所有其他处理器中该行的缓存副本标记为无效，然后专有地进行写入（MESI 属于此类）；写更新协议（Write-Update Protocol / Write-Broadcast）——写操作时将新数据广播到所有持有该行副本的处理器，使其同步更新。Snooping 协议的实现依赖共享总线天然的广播特性，适用于核心数不多（一般 <=8 核）的系统。

## 关键结论

- Snooping 协议利用共享总线的广播特性：每个总线事务对所有缓存控制器可见，无需额外的通信网络
- 写无效的典型流程：P(A)修改共享副本 -> P(A)在总线上发 BusRdX(读独占) -> 所有其他 P 将该行本地副本失效 -> P(A)获独占权后写入
- 写更新的典型流程：P(A)写入时在总线上广播新值 -> 所有持有该行副本的 P 更新本地副本为最新值
- 写无效 vs 写更新：写无效通信量少（单次失效后多写无需额外通信）、易于实现；写更新在"单生产者多消费者"场景下延迟低但带宽消耗大
- Snooping 的扩展性限制：总线成为瓶颈，所有处理器共享单一广播域，增加到 16-32 核时总线请求冲突剧烈

## 易错点

1. Snooping 需要 Cache 控制器额外硬件：每个 Cache 标签需要双端口（一个供本地核心访问，一个供 Snoop 访问），增加了设计复杂度和功耗。
2. 写更新协议中"后续写"不一定需广播：若写的数据在被上次广播后没有被其他人再次使用，广播就是浪费带宽。
3. Snooping 协议假设事务原子的全局广播顺序：所有处理器看到的广播事务顺序必须一致（总线串行化保证）。

## 例题

**例题1：** 比较 Snooping 协议和 Directory 协议的扩展性。

**解答：** Snooping 依赖总线广播，总线带宽限制随核心数增长（O(N) 总线事务），适合 <=8 核。Directory 协议使用分布式目录记录每个 Cache 行的共享者，通过点对点消息通信，带宽需求随被共享行数增长，适合数十到数百核的大规模多处理器（如服务器、HPC）。

**例题2：** 写无效 Snooping 协议中 "Ownership" 的概念。

**解答：** 当某 Cache 行处于 Modified 状态时，该 Cache 拥有该行的 Ownership——它持有最新数据并负责在接收到其他处理器的读请求时提供数据（可能既不依赖也不等待主存响应），这称为"干预"（Intervention）。若发生替换，拥有者必须执行写回（Write-Back）到主存，传递所有权。

## 关联页面

[[MESI协议]] [[Cache一致性]] [[多核处理器基础]] [[Cache写策略]]
