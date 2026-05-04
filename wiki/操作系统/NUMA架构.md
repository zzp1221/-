---
title: "NUMA架构与内存亲和性"
course: 操作系统
chapter: 内存管理
difficulty: ADVANCED
tags: [操作系统, NUMA, 内存架构, 多处理器]
aliases: [Non-Uniform Memory Access]
source: "Computer Architecture: A Quantitative Approach (Hennessy & Patterson)"
updated_at: 2026-05-02
---

## 核心定义

NUMA（非一致内存访问）是多处理器架构，每个CPU有自己的本地内存，访问本地内存快、远程内存慢（延迟差2-3倍）。UMA中所有CPU访问内存延迟相同但总线带宽是瓶颈。现代多路服务器均为NUMA架构。OS需要感知NUMA拓扑，尽量将进程内存分配在本地节点。Linux的numactl/mbind控制内存策略。

## 关键结论

1. NUMA Ratio=远程延迟/本地延迟，通常1.5-3.0 2. Linux默认first-touch策略（首次访问的CPU所在节点分配内存）3. 数据库、JVM需要显式配置NUMA感知 4. 跨NUMA节点的锁竞争性能灾难

## 关联页面

[[多处理器架构]] [[缓存一致性协议]] [[内存层次结构]]
