---
title: "Slab分配器与内核内存管理"
course: 操作系统
chapter: 内存管理
difficulty: ADVANCED
tags: [操作系统, Slab, 内核内存, BuddySystem]
aliases: [Slab Allocator]
source: "The Slab Allocator: An Object-Caching Kernel Memory Allocator (Bonwick 1994); Linux内核mm/slab.c"
updated_at: 2026-05-02
---

## 核心定义

Slab分配器在Buddy System之上构建，用于高效分配固定大小的内核对象。Buddy System以页为单位分配，但内核经常需要分配小对象（inode、dentry、task_struct），造成严重内部碎片。Slab维护每种对象类型的缓存(kmem_cache)，预分配slab（1到多个连续页），内部划分为object槽位。分配/释放只需标记slot状态。

## 关键结论

1. 三种变体：SLAB(传统)、SLUB(简化版，Linux默认)、SLOB(嵌入式) 2. SLUB去掉了复杂的着色和队列，每个CPU有本地缓存 3. /proc/slabinfo查看slab使用情况

## 关联页面

[[伙伴系统Buddy System]] [[内存分配]]
