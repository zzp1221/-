---
title: "写时复制（Copy-on-Write）"
course: 操作系统
chapter: 内存管理
difficulty: INTERMEDIATE
tags: [操作系统, COW, 写时复制, fork, 内存管理]
aliases: [Copy-on-Write]
source: "Operating System Concepts (Silberschatz) 第9章; Linux内核源码分析"
updated_at: 2026-05-02
---

## 核心定义

写时复制是一种延迟复制优化技术。父进程fork子进程时，不立即复制全部页表，而是将父子进程的页表项都设为只读并标记为COW。当任一方尝试写时，触发缺页中断，内核才真正复制该页。这样fork后立即exec的进程（绝大多数情况）避免了大量无意义的复制。

## 关键结论

1. fork()+exec()的开销从O(进程内存)降到O(页表) 2. COW页在缺页处理中分配新物理页 3. /proc/PID/smaps的Shared_Clean/Shared_Dirty反映COW状态 4. 也用于KVM虚拟机的内存超分

## 关联页面

[[进程的创建与终止]] [[虚拟内存]] [[缺页中断]]
