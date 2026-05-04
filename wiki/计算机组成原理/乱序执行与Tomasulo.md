---
title: "Tomasulo算法详解"
course: 计算机组成原理
chapter: 处理器设计
difficulty: ADVANCED
tags: [计算机组成原理, Tomasulo, 乱序执行, 保留站]
aliases: [Tomasulo Algorithm]
source: "An Efficient Algorithm for Exploiting Multiple Arithmetic Units (Tomasulo 1967); Computer Architecture (Hennessy & Patterson)"
updated_at: 2026-05-02
---

## 核心定义

Tomasulo算法是乱序执行的经典实现（IBM 360/91）。保留站(Reservation Station)：每条指令发射时分配到对应功能单元的保留站项，记录操作数状态(就绪值或等待哪个保留站产生)。公共数据总线(CDB)：每条完成的指令在CDB上广播结果+保留站ID，所有等待该结果的保留站捕获(旁路tag匹配实现寄存器重命名)。Load/Store Buffer追踪内存操作顺序。

## 关键结论

1. Tomasulo实现了寄存器重命名(通过保留站tag) 2. CDB是物理瓶颈——现代处理器每个功能单元有自己的旁路网络 3. ROB(Reorder Buffer)加入后形成现代乱序核心：保留站+ROB+物理寄存器堆

## 关联页面

[[超标量与乱序执行]] [[指令流水线与冒险]] [[寄存器重命名]]
