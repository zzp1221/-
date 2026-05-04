---
title: Cache概述
course: 计算机组成原理
chapter: 第四章 存储器系统
difficulty: INTERMEDIATE
tags: [Cache, 缓存, 局部性, 命中率, Cache行, 标记]
aliases: [Cache Memory, 高速缓冲存储器, Cache Basics]
source:
  - Patterson & Hennessy, Computer Organization and Design
updated_at: 2026-05-02

---

## 核心定义

Cache（高速缓冲存储器）是位于 CPU 和主存之间的高速小容量存储器（基于 SRAM），用于缓解 CPU 与主存之间的速度鸿沟——即冯诺依曼瓶颈。Cache 利用程序的局部性原理，将主存中 CPU 近期可能访问的数据块（Cache Block/Cache Line）预取到高速的 Cache 中。当 CPU 访问内存时，首先检查所需数据是否在 Cache 中（命中 Hit，从 Cache 快速读取）还是不在（缺失 Miss，需从慢速主存取数据并替换 Cache 中的一个块）。在一个精心设计的 Cache 中，命中率可达 90%-99%。Cache 的设计涉及多个关键决策：映射方式（直接/全相联/组相联）、替换算法（LRU/FIFO/Random）、写策略（写穿透/写回）、块大小等。现代 CPU 通常具备三级 Cache：L1（分离I/D，32-64KB）、L2（统一，256KB-1MB）、L3（统一、多核共享，数MB-数十MB）。

## 关键结论

- Cache 的实质是以空间换时间：用 SRAM 的高成本换取对 DRAM 的感知加速
- Cache 行（Cache Line）：Cache 与主存之间传输的最小数据单位，典型大小为 64 字节
- 标记（Tag）、索引（Index）和块内偏移（Block Offset）是从主存地址到 Cache 位置的三字段映射
- 命中时间（Hit Time）包括 Tag 比较和 MUX 选择；缺失代价（Miss Penalty）包括从主存取数据并填充 Cache 行的时间
- Cache 缺失类型：强制缺失（Compulsory Miss, 首次访问）、容量缺失（Capacity Miss, Cache 太小）、冲突缺失（Conflict Miss, 多块映射到同一位置）

## 易错点

1. "Cache 一致性"和"Cache 一致性协议（如 MESI）"不要混淆：前者是概念（保证多核/多Cache看到的数据一致），后者是实现机制。
2. 多级 Cache 间的包含关系（Inclusive vs Exclusive）：包含式（L1 在 L2 中）浪费容量但简化一致性；排他式（L1 不在 L2 中）有效利用总容量，但一致性协议更复杂。
3. Cache 行大小不是越大越好：过大的行增加缺失代价、浪费带宽、增加冲突缺失；过小的行降低空间局部性利用。

## 例题

**例题1：** 某 Cache 容量 64KB、行大小 64 字节、4 路组相联。求 Tag/Index/Offset 字段划分（32位地址）。

**解答：** Offset = log2(64) = 6 bit。组数 = 64KB / (64*4) = 256 组。Index = log2(256) = 8 bit。Tag = 32-8-6 = 18 bit。

**例题2：** 比较 3C 缺失（Compulsory, Capacity, Conflict）的产生原因和消除方法。

**解答：** 强制缺失由首次访问数据引起，无法完全消除，但可通过预取和更大块缓解。容量缺失由 Cache 容量不足引起，增大 Cache 可缓解。冲突缺失由映射策略导致（多地址竞争同一 Cache 行），增加相联度可缓解。组相联是平衡三种缺失的工程折中。

## 关联页面

[[Cache映射方式]] [[Cache替换算法]] [[Cache写策略]] [[存储器层次结构]] [[MESI协议]]
