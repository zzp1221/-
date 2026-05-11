---
title: "CPU亲和性与NUMA"
course: 操作系统
chapter: CPU调度与架构
difficulty: ADVANCED
tags: [操作系统, CPU亲和性, NUMA, 调度, 内存架构]
aliases: [CPU Affinity, NUMA, Non-Uniform Memory Access]
source: "Linux kernel documentation: cpusets; Drepper《What Every Programmer Should Know About Memory》; ACPI NUMA specification"
updated_at: 2026-05-02
---

## 核心定义

CPU亲和性(CPU affinity)指进程/线程绑定到特定CPU核心的机制。Linux通过taskset命令或sched_setaffinity()系统调用设置。硬亲和性由用户指定，软亲和性由调度器维护(尽量让进程留在同一CPU以利用缓存热数据)。NUMA(Non-Uniform Memory Access)在大规模多处理器系统中，每个CPU有自己的本地内存——本地内存访问快(1x)，远程内存访问慢(1.5-3x)。NUMA-aware调度目标是让进程使用本地内存和执行CPU。

## NUMA实战

Linux的NUMA感知通过numactl查看和设置。libnuma提供API控制内存分配策略(MPOL_BIND绑定到特定节点、MPOL_INTERLEAVE均匀分布在节点之间、MPOL_PREFERRED偏好节点但不强制)。numa_alloc_onnode分配特定节点上的内存。典型的NUMA调度策略：mbind将线程的内存页面迁移到本地节点。大型数据库(PostgreSQL/Oracle)和Java GC(ZGC/Shenandoah)对NUMA友好以实现更好的性能。

## 关键结论

1. 双socket服务器的NUMA效果显著——需明确管理内存和CPU亲和 2. 宿主线程和目标内存必须位于同一NUMA节点最优 3. 虚拟化环境中NUMA拓扑映射复杂(vNUMA) 4. Intel的SAP(Sub-NUMA Clustering)在socket内创建NUMA域 5. /proc/PID/numa_maps展示每个VMA的NUMA分布

## 关联知识点

[[操作系统-多级反馈队列调度MLFQ]] [[操作系统-虚拟内存与TLB]] [[计算机组成原理-多核处理器架构]]
