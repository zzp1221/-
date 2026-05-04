---
title: CISC与RISC
course: 计算机组成原理
chapter: 第五章 指令系统
difficulty: INTERMEDIATE
tags: [CISC, RISC, 指令集, x86, ARM, RISC-V, 复杂指令集, 精简指令集]
aliases: [CISC vs RISC, Complex Instruction Set, Reduced Instruction Set]
source:
  - Patterson & Hennessy, Computer Organization and Design
  - Patterson & Ditzel, The Case for the Reduced Instruction Set Computer (1980)
updated_at: 2026-05-02

---

## 核心定义

CISC（Complex Instruction Set Computer，复杂指令集计算机）和 RISC（Reduced Instruction Set Computer，精简指令集计算机）是两种对立的 ISA 设计哲学。CISC 强调以硬件复杂性换取编程便利性：提供大量功能强大的指令（数百条），支持复杂的寻址方式，单条指令可以完成读取-运算-写回等多步操作（如 x86 的 ADD [mem], reg）。变长指令编码，编译器工作较简单但CPU控制逻辑复杂。x86/x86-64 是 CISC 的代表。RISC 强调以软件（编译器）的智能换取硬件的高效和规整：仅有少量基本指令（几十到一百条），固定长度编码（通常 32 位），仅 Load/Store 指令访问内存，所有运算操作数在寄存器中。指令格式规整便于流水线和多发射，编译器承担更多优化责任。ARM、MIPS、RISC-V 是 RISC 的代表。现代的两者界限在模糊：x86 内部将 CISC 指令翻译为类 RISC 微操作执行；ARM 也增加了 SIMD 等复杂扩展。

## 关键结论

- RISC 的五大特征（Patterson 1980）：Load/Store 架构、固定长度指令、大寄存器堆、单周期执行、硬布线控制
- CISC 的优势：代码密度高（变长指令）；RISC 的优势：高性能（流水线友好）、低功耗、设计周期短
- 现代 x86 CPU 的"RISC 化"：将复杂 x86 指令解码为一条或多条简单微操作（μOps），后端执行核心实质上是 RISC-like
- ARM 的成功证明了 RISC 在移动/嵌入式领域的卓越效能
- RISC-V 是开放标准的 RISC ISA，推动指令集的自由化与定制化浪潮

## 易错点

1. "CISC 已死"是不准确的：x86 高性能处理器的存在证明，复杂的指令集可以通过微架构转化（μOp 转换）实现高效执行。
2. RISC 不是"指令数量少"的缩写，而是"每条指令做的事情少"：RISC 也可以有很多指令（ARM 有几百条），关键是每条指令功能简单。
3. RISC 不等于"低性能"：Apple M1/M2（ARM 架构）的性能已证明 RISC 可以实现顶级性能。

## 例题

**例题1：** CISC 和 RISC 分别如何做乘法运算？

**解答：** CISC：MUL R1, [mem] 一条指令完成取数、乘法、写回。RISC：LW R1, addr; LW R2, addr2; MUL R3, R1, R2 三条指令。CISC 指令少但每条更复杂；RISC 指令多但每条更简单。整体执行速度受限于微架构实现。

**例题2：** 解释 x86 的 μOp 转化机制。

**解答：** x86 取指后，复杂指令译码器（Complex Decoder）将变长 x86 指令转换为定长的 μOps。例如 ADD [EAX+4*EBX+100], ECX 被分解为：Load T1 = [EAX+4*EBX+100]; ADD T2 = T1, ECX; Store [EAX+4*EBX+100] = T2。μOps 被送入 RISC-like 的后端执行流水线，使用 Reservation Station、乱序执行等技术。

## 关联页面

[[指令系统概述]] [[指令格式与操作码]] [[寻址方式]] [[指令流水线概述]]
