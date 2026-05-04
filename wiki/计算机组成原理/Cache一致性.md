---
title: Cache一致性
course: 计算机组成原理
chapter: 第八章 多核处理器
difficulty: ADVANCED
tags: [Cache一致性, 多核, 共享数据, 一致性协议, 写传播, 写串行]
aliases: [Cache Coherence, 缓存一致性, Coherence Protocol]
source:
  - Patterson & Hennessy, Computer Organization and Design
  - Sorin, Hill & Wood, A Primer on Memory Consistency and Cache Coherence
updated_at: 2026-05-02

---

## 核心定义

Cache 一致性（Cache Coherence）是多核/多处理器系统中的核心问题：当多个核心各自拥有独立的 Cache（私有 L1/L2），它们对同一内存地址的缓存副本必须保持一致。假设核 A 和核 B 各自缓存了变量 x=0，核 A 修改 x=1，此时核 B 的 Cache 中 x 仍然为 0（过时），若不加以处理将返回错误的值。Cache 一致性协议定义了规则，确保所有处理器对同一地址的访问所见一致。一致性的两个基本要求：写传播（Write Propagation）——一个核对数据的修改必须使其他核可见；写串行化（Write Serialization）——所有核对同一地址的写操作必须看起来以相同的顺序被观察到（全局顺序一致）。一致性协议分为监听式协议（Snooping Protocol）——所有 Cache 控制器监听共享总线上的事务（如 MESI 协议），适合总线型多处理器；目录式协议（Directory-Based Protocol）——使用集中式目录记录每个 Cache 行被哪些处理器缓存，适合扩展性要求高的大规模多处理器。

## 关键结论

- 一致性和一致性模型（Consistency Model）的区别：一致性保证单个地址的多副本一致，一致性模型定义多个地址的读/写操作之间的全局顺序规则
- MESI 是经典的监听式一致性协议：Modified（已修改且独占）、Exclusive（独占且干净）、Shared（共享且干净）、Invalid（无效）
- 目录协议使用分布式位向量（Sharing Vector）追踪每个 Cache 行的位置，适合 >8 核的大规模系统
- 伪共享（False Sharing）：不同核访问同一 Cache 行的不同变量，一致性协议误认为数据冲突导致频繁失效，严重影响性能
- 现代 CPU 在 L1/L2 使用写无效式（Write-Invalidate）MESI 协议，L3 作为统一缓存仲裁点

## 易错点

1. Cache 一致性不是"Cache 立即同步"：一致性不要求修改瞬时广播并更新所有副本，只要求在"有意义"的时刻（如读该地址时）数据是正确/最新的。
2. 一致性（Coherence）和一致性模型（Consistency）是两个层次的概念：Coherence 是手段（协议保障），Consistency 是编程模型约定（如 Sequential Consistency, TSO, Relaxed）。
3. 一致性检查的粒度是 Cache 行：同行的无关数据共享会导致伪共享的性能问题。

## 例题

**例题1：** 两个核 A 和 B 共享变量 x=0，初始都在 Shared 态。A 写 x=1，描述 MESI 状态转移。

**解答：** 初始 x 在 A、B 均为 Shared 态。A 发起写操作：A 在总线上广播"读独占"（Read Exclusive / BusRdX），将自己的 Cache 行转 Modified，同时使 B 的副本变 Invalid。A 写入 x=1 成功。若 B 后续读 x：B 发起"读"请求，A 监听后知自己持有最新 Modified 数据，通过总线将该 Cache 行提供给 B（写回内存并可选的复制），A 转 Shared，B 获得 Shared 副本。

**例题2：** 伪共享的例子和消除方法。

**解答：** 两个线程分别频繁更新相邻的 4 字节整数 a 和 b，它们落在同一 64 字节 Cache 行中。每个线程的写操作会使另一个核的该 Cache 行失效，造成频繁一致性协议通信（Cache Line Bouncing），吞吐率大幅下降。消除方法：在 a 和 b 之间填充 60 字节的填充数据（Padding），确保两者位于不同的 Cache 行中。

## 关联页面

[[MESI协议]] [[Snooping协议]] [[多核处理器基础]] [[Cache概述]]
