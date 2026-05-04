---
title: "伙伴系统（Buddy System）"
course: 操作系统
chapter: 内存管理
difficulty: INTERMEDIATE
tags: [操作系统, 伙伴系统, BuddySystem, 物理内存管理]
aliases: [Buddy System]
source: "Operating System Concepts (Silberschatz) 第10章; Linux内核mm/page_alloc.c"
updated_at: 2026-05-02
---

## 核心定义

伙伴系统是Linux内核的物理页分配器。将物理内存划分为2^n个连续页的块。分配时找到满足请求的最小2^n块，必要时将大块分裂为两个'伙伴'。释放时检查伙伴是否空闲，若是则合并为更大的块，递归向上。伙伴的定义：两个大小相同、物理地址相邻、且起始地址对齐到块大小的块。

## 关键结论

1. 分配/释放O(log n)复杂度 2. 外部碎片可控（所有空闲块大小都是2的幂）3. /proc/buddyinfo可查看当前伙伴状态 4. 内核以page->private记录order和伙伴信息

## 关联页面

[[Slab分配器]] [[内存分配]] [[分页存储管理]]
