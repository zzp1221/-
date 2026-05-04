---
title: CPU结构
course: 计算机组成原理
chapter: 第六章 中央处理器
difficulty: INTERMEDIATE
tags: [CPU, 处理器结构, 控制器, 数据通路, 运算器, 寄存器组]
aliases: [CPU Architecture, Processor Structure, 中央处理器结构]
source:
  - Patterson & Hennessy, Computer Organization and Design
updated_at: 2026-05-02

---

## 核心定义

中央处理器（Central Processing Unit, CPU）是计算机的核心部件，负责取指令、译码和执行。从功能划分角度，CPU 由两大基本部分组成：数据通路（Datapath）——执行数据处理和存储操作的硬件集合，包括寄存器组（Register File）、ALU、多路选择器（MUX）、程序计数器（PC）等，处理指令执行过程中的数据流；控制器（Control Unit）——负责指挥和协调数据通路的工作，根据指令的操作码生成相应的控制信号序列，决定 ALU 执行何种运算、寄存器如何选择、数据如何流动等。此外，CPU 还包括时钟系统、流水线寄存器、中断处理逻辑等辅助单元。

从实现方式上，控制器可分为硬布线控制器（Hardwired Control）和微程序控制器（Microprogrammed Control）。硬布线控制器使用组合逻辑门和状态机直接生成控制信号，速度快但修改困难；微程序控制器将每条机器指令实现为一段微程序（存储在控制存储器 ROM 中），灵活但速度较慢。现代 CPU 普遍采用硬布线+微码的混合方案。

## 关键结论

- 数据通路包括三种基本组件：组合逻辑（ALU、MUX、加法器）、时序逻辑（寄存器、PC、存储器）和互连线路（总线）
- 控制信号驱动的操作：RegWrite（寄存器写使能）、ALUSrc（ALU 第二操作数选择）、MemWrite/MemRead、Branch 等
- 单周期 CPU 每时钟周期执行一条完整指令，时钟周期由最慢指令决定，效率低
- 多周期 CPU 将指令执行分为多个阶段，每阶段一个时钟周期，不同指令所需周期数不同
- 现代 CPU 采用流水线技术进一步并行化指令执行，CPI 趋近于 1

## 易错点

1. 数据通路和控制器的关系：数据通路是"被控对象"，控制器是"控制者"。控制器的输出信号直接作用于数据通路的各组件。
2. PC 的更新时机：在单周期设计中，PC+4 和分支目标地址的计算在同一个周期完成（通过加法器和 MUX 选择），最终结果在时钟沿写入 PC。
3. 寄存器堆的"读异步写同步"特性：读操作是组合逻辑（地址给出数据即输出），写操作是时序逻辑（时钟沿写入），这使得同一时钟周期内可以读某个寄存器并写另一个寄存器。

## 例题

**例题1：** 画出单周期 CPU 中 R-type 指令（ADD R1, R2, R3）的数据通路。

**解答：** IF：PC -> 指令存储器 -> 指令寄存器；ID：操作码送控制器，R2/R3 地址送寄存器堆读出；EX：ALU 执行 R2+R3，ALUSrc 选寄存器输出；MEM：该指令不访问内存；WB：ALU 结果写回 R1。控制信号：RegDst=1(写R1), ALUSrc=0(选R3), MemtoReg=0(选ALU结果), RegWrite=1, MemRead=0, ALUOp=ADD。

**例题2：** I-type 指令（LW R1, offset(R2)）与 R-type 的数据通路有何不同？

**解答：** I-type 的 EX 阶段使用了不同的 ALU 操作（加法用于地址计算：R2 + sign_ext(offset)）；MEM 阶段需要读数据存储器（MemRead=1）；WB 阶段选择存储器读出的数据写回寄存器（MemtoReg=1）而非 ALU 结果。偏移量需经过符号扩展单元扩展到 32 位。

## 关联页面

[[控制器]] [[数据通路]] [[ALU]] [[指令流水线概述]] [[冯诺依曼结构]]
