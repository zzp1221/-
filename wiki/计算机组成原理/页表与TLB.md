---
title: 页表与TLB
course: 计算机组成原理
chapter: 第四章 存储器系统
difficulty: INTERMEDIATE
tags: [页表, TLB, 快表, MMU, 地址转换, 多级页表]
aliases: [Page Table, Translation Lookaside Buffer, 快表]
source:
  - Patterson & Hennessy, Computer Organization and Design
updated_at: 2026-05-02

---

## 核心定义

页表（Page Table）是记录虚拟页号（VPN）到物理页框号（PFN）映射关系的数据结构，由操作系统创建和维护并存储在物理内存中。每个进程拥有独立的页表，通过 MMU（Memory Management Unit）完成地址转换。页表项（PTE, Page Table Entry）通常包含：物理页框号 PFN（主数据），有效位 V（该页是否在物理内存中），保护位（读/写/执行权限），脏位 D（该页是否被修改过），访问位 A（该页最近是否被访问过，用于页面替换算法）。当虚拟页不在物理内存中（V=0）时发生缺页异常（Page Fault），操作系统从磁盘调入。

TLB（Translation Lookaside Buffer，快表）是 MMU 内的专用 Cache，缓存最近使用的 VPN->PFN 映射，以加速地址转换。TLB 容量很小（通常 64-256 项），采用全相联或高组相联映射，命中率可达 99%以上。TLB 命中时地址转换只需 1 个时钟周期；TLB 缺失时需要访问内存中的页表（可能需要多次访存），代价可达数十到上百周期。TLB 与 Cache 的协作共同构成了现代计算机访存的"双层加速"机制。

## 关键结论

- 多级页表以空间换时间（换表的大小）：每级页表仅 4KB（存 512 个/1024 个 PTE），不使用的分支无需分配空间
- 倒置页表（Inverted Page Table）以 PFN 为索引，表项数 = 物理页框数，节省空间但查找复杂（需哈希）
- TLB 实际上是地址转换的"Cache"，同样有命中/缺失、替换策略、写策略等
- TLB Shootdown：多核环境下，当一个核修改页表时需通知其他核心刷新对应的 TLB 项（软件或硬件机制）
- 虚拟化环境下的嵌套页表：Guest VA -> Guest PA -> Host PA，Intel EPT 和 AMD NPT 提供硬件支持

## 易错点

1. TLB 缺失不一定等于页缺失：TLB 缺失仅表示该映射不在 TLB 中，需要走页表查找（PTW, Page Table Walk）；页缺失指 V=0 的 PTE，需要磁盘 I/O。
2. TLB 与 L1 Cache 的地址同时转换和命中判断：现代 CPU 使用 VIPT (Virtually Indexed, Physically Tagged) 策略——用 VA 低位做 Index（并行访问），Tag 比较用 PA 高位（防止别名问题）。
3. TLB 刷新（Flush）的代价：进程切换时需要全部或部分刷新 TLB（除非使用进程 ID ASID 区分）。TLB 刷新后性能短期下降。

## 例题

**例题1：** 32 位地址空间，4KB 页，两级页表（每级 10 位），单 PTE 4 字节。 求两级页表总开销。

**解答：** 一级页表（Page Directory）：2^10 * 4B = 4KB；二级页表每个覆盖 4KB*1024=4MB，需要多少个由进程实际使用的地址空间决定。全 4GB 映射需要 2^10 个二级页表，共 4MB。但实际进程只映射几十 MB，开销通常几十 KB 到几百 KB。多级页表的核心价值：节约不需要映射的中间级页表空间。

**例题2：** TLB 容量 64 项，4KB 页。TLB 可以覆盖的最大地址空间是多少？

**解答：** TLB 覆盖 = 64 * 4KB = 256KB。如果程序的工作集（频繁访问的数据/代码）不超过 256KB，TLB 命中率将极高。这对 TLB 容量设计和软件优化（页大小、数据布局）具有指引意义。巨页（Huge Page, 2MB/1GB）可大大扩展 TLB 覆盖范围。

## 关联页面

[[虚拟存储器]] [[存储器层次结构]] [[Cache概述]] [[操作系统内存管理]]
