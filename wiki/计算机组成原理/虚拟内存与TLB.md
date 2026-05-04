---
title: "虚拟内存与TLB机制"
course: 计算机组成原理
chapter: 存储器层次
difficulty: INTERMEDIATE
tags: [计算机组成原理, 虚拟内存, TLB, 页表, 缺页]
aliases: [Virtual Memory, TLB]
source: "Computer Organization and Design (Patterson & Hennessy) 第5章; Intel x86架构手册"
updated_at: 2026-05-02
---

## 核心定义

虚拟内存为每个进程提供独立的地址空间。页表：虚拟页号→物理页框号(+权限/存在/脏/访问位)。多级页表减少内存开销(x86-64:4级→5级(PML5)页表)。TLB(快表)：缓存最近使用的虚实地址映射(内容可寻址存储器CAM+RAM)。TLB缺失：硬件填表(x86 CR3页面遍历)或软件填表(MIPS)。ASID(地址空间ID)避免上下文切换时全刷TLB。

## 关键结论

1. L1 TLB延迟<1 cycle(全相联)、L2 TLB延迟4-8 cycles 2. 大页(2MB/1GB)用更少TLB条目覆盖更大范围 3. Meltdown漏洞利用访存指令微架构副作用绕过页保护

## 关联页面

[[缓存体系结构]] [[大页内存与透明大页]] [[缺页中断处理流程]]
