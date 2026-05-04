---
title: Cache写策略
course: 计算机组成原理
chapter: 第四章 存储器系统
difficulty: INTERMEDIATE
tags: [Cache写策略, 写穿透, 写回, 写分配, 脏位, 写缓冲]
aliases: [Cache Write Policy, Write-Through, Write-Back, Write-Allocate]
source:
  - Patterson & Hennessy, Computer Organization and Design
updated_at: 2026-05-02

---

## 核心定义

Cache 写策略决定了当 CPU 执行写操作（Store 指令）时，数据如何处理：是同时更新 Cache 和下一级存储，还是仅更新 Cache 并延迟写回。两种基本写策略：写穿透（Write-Through）——写操作同时更新 Cache 和主存（或下一级 Cache）。优点是数据一致性好（Cache 与主存始终保持一致），简化了 Cache 一致性协议的设计；缺点是每次写操作都需要访问较慢的主存，写流量大，功耗高。写回（Write-Back）——写操作仅更新 Cache，将对应 Cache 行标记为"脏"（Dirty Bit=1），只有当该脏行被替换出去时才将整个 Cache 行写回主存。优点是写流量显著减少（多次写同一 Cache 行只需一次写回），功耗低；缺点是数据一致性维护更复杂。写缺失（Write Miss）的处理策略：写分配（Write-Allocate）——将缺失的 Cache 行先从主存取到 Cache 再写入（通常与 Write-Back 搭配）；非写分配（No-Write-Allocate）——直接写入主存而不加载到 Cache（通常与 Write-Through 搭配）。

## 关键结论

- Write-Through + No-Write-Allocate 策略简单一致，适合简单处理器和 I/O 设备
- Write-Back + Write-Allocate 是现代 CPU 的主流选择：写流量少，性能高
- Write-Through 需要写缓冲（Write Buffer）缓解写入延迟：CPU 将写入数据放入缓冲区后立即继续执行，由总线控制器异步完成实际主存写入
- 脏位（Dirty Bit）在 Write-Back 策略中至关重要：标记该 Cache 行已被修改，替换时必须写回
- 写策略的选择直接影响多核一致性协议的复杂度

## 易错点

1. Write-Back 不是"永远不写主存"：当脏行被替换时全体写回（Write-Back），所以替换的代价比 Write-Through 大（需写一整行）。
2. Write-Through 不一定真的每次写穿到主存：在多级 Cache 中，Write-Through 通常只写到下一级（如 L1->L2），L2 可能用 Write-Back 再写到主存。
3. 写缓冲满会导致 CPU 停顿：L1 使用 Write-Through 时，连续密集写入会导致写缓冲饱和，CPU 必须等待。

## 例题

**例题1：** 比较 Write-Through 和 Write-Back 在以下场景的优劣：CPU 密集循环中对同一变量反复加 1（共 1000 次）。

**解答：** Write-Through：每次写入都穿透到主存或 L2，共 1000 次写操作，浪费总线带宽和功耗。Write-Back：变量在 Cache 行中连续被修改 1000 次，仅在最终替换时写回一次，写流量减少 1000 倍。

**例题2：** DMA 设备直接访问主存时，对 Write-Back Cache 有什么影响？

**解答：** DMA 可能读取到过时（Stale）的主存数据，因为最近的写操作还只在 Cache 中（未写回）。解决方法：(1) DMA 区域标记为不可缓存（Non-Cacheable），(2) DMA 访问前 CPU 主动刷新 Cache 行（Cache Flush）将脏数据写回主存，确保一致性。

## 关联页面

[[Cache概述]] [[Cache映射方式]] [[Cache替换算法]] [[MESI协议]] [[DMA]]
