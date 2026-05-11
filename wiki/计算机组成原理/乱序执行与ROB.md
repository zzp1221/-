---
title: "乱序执行与ROB"
course: 计算机组成原理
chapter: CPU微架构
difficulty: ADVANCED
tags: [计算机组成, 乱序执行, ROB, 微架构, 寄存器重命名]
aliases: [Out-of-Order Execution, Reorder Buffer, Tomasulo]
source: "Tomasulo 1967 (IBM 360/91); H&P《Computer Architecture》Ch 3; Intel Optimization Manual §2.1"
updated_at: 2026-05-02
---

## 核心定义

乱序执行(Out-of-Order, OoO)允许CPU不按程序顺序执行指令——只要操作数就绪且功能单元可用就发射执行。核心数据结构：Reorder Buffer(ROB/重排序缓冲区)——按程序顺序存储所有正在执行的指令，确保指令按程序顺序提交(commit)；Register Alias Table(RAT)——将体系结构寄存器映射到物理寄存器(寄存器重命名)，消除写后读(WAW)和读后写(WAR)假数据冒险。Tomasulo算法(IBM 360/91)是乱序执行的奠基——通过保留站(reservation station)仲裁并分发就绪的指令。

## 数据流与ROB深度

乱序执行核心流程：Fetch→Decode→Rename→Dispatch到保留站→Issue(操作数就绪后)→Execute→Write Result广播到公共数据总线(CDB,Common Data Bus)→Complete→Commit(按ROB顺序写入寄存器文件和PC)。ROB深度决定飞行中(in-flight)指令的最大数量——现代CPU(Skylake:224, Zen4:320条目)。ROB满时前端必须停顿。Store Buffer和Load Queue解决内存访问重排序——先加载(load)可越过之前的store当无别名(内存消岐/分预测)。

## 关键结论

1. 乱序执行由WAR和WAW促发(真数据依赖RAW不能用Rename解决) 2. 推测执行(speculation)在分支预测后执行未来的指令(可能被抛弃——错误路径squash) 3. 乱序执行的验证难点——正确恢复精确异常(precise exceptions) 4. 存储前向(Store-to-Load Forwarding)减少数据要通过缓存的时间 5. 超标量(多发射)+乱序执行协同交付高IPC

## 关联知识点

[[计算机组成原理-分支预测器深度]] [[计算机组成原理-流水线与冒险]] [[编译原理-代码生成与优化]]
