---
title: "LRU近似算法与CLOCK"
course: 操作系统
chapter: 内存管理
difficulty: INTERMEDIATE
tags: [操作系统, LRU, CLOCK, 页面置换, 近似算法]
aliases: [CLOCK Algorithm]
source: "Operating System Concepts (Silberschatz) 第10章"
updated_at: 2026-05-02
---

## 核心定义

精确LRU开销大（每次访问都要更新栈/链表），实际系统使用CLOCK近似算法。基本CLOCK：页表项有访问位(accessed bit)，缺页时循环扫描，访问位=1的置0并跳过，访问位=0的淘汰。改进CLOCK：增加修改位(dirty bit)，四类页：(0,0)最优淘汰、(0,1)次优(需写回)、(1,0)再次、(1,1)最后淘汰。两轮扫描：先找(0,0)，再找(0,1)并写回。

## 关键结论

1. CLOCK的扫描指针在内存压力小时可能转一圈回到原位 2. 改进CLOCK比基本CLOCK减少不必要的写回磁盘 3. Linux的kswapd使用类似改进CLOCK的机制 4. 扫描策略需配合工作集模型确定驻留集大小

## 关联页面

[[页面置换算法综合]] [[缺页中断处理流程]] [[工作集模型]]
