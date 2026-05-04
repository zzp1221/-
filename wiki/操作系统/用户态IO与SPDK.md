---
title: "用户态IO与SPDK"
course: 操作系统
chapter: IO系统
difficulty: ADVANCED
tags: [操作系统, SPDK, 用户态IO, NVMe, DPDK]
aliases: [Storage Performance Development Kit]
source: "SPDK官方文档; Intel DPDK文档"
updated_at: 2026-05-02
---

## 核心定义

传统IO路径瓶颈：系统调用→VFS→文件系统→块层→驱动→中断，延迟>10μs。用户态IO绕过内核：SPDK将NVMe驱动放在用户态，通过轮询替代中断，用无锁队列与硬件直接交互，延迟降至<10μs。需要UIO/VFIO将PCI BAR映射到用户空间。DPDK类似思路用于网络包处理。

## 关键结论

1. SPDK实现NVMe-oF目标端延迟<100μs 2. 轮询导致CPU 100%使用率但延迟可预期 3. 需要hugepages减少页表开销 4. 适合延迟敏感场景(数据库、存储系统)

## 关联页面

[[IO控制方式]] [[中断系统]] [[DMA直接存储器访问]]
