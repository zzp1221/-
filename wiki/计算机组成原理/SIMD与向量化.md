---
title: "SIMD与向量化"
course: 计算机组成原理
chapter: 指令集
difficulty: INTERMEDIATE
tags: [计算机组成, SIMD, 向量化, AVX, NEON]
aliases: [SIMD, Vectorization, AVX-512, NEON]
source: "Intel Intrinsics Guide; ARM NEON Programmer's Guide; H&P《Computer Architecture》Ch 4"
updated_at: 2026-05-02
---

## 核心定义

SIMD(Single Instruction Multiple Data,单指令多数据流)是数据级并行模式——一条指令同时处理多个数据元素。x86系列：MMX(64位, 1997)→SSE(128位)→AVX(256位, Sandy Bridge 2011)→AVX-512(512位, Skylake-SP 2017)。ARM系列：NEON(128位, ARMv7+)。SIMD寄存器(DIR,XMM/YMM/ZMM寄存器或V寄存器)按lane划分——每个lane对应一个独立操作。编译器的自动向量化(automatic vectorization)将标量循环转换为SIMD指令——受限于指针别名和循环依赖。

## 强制向量化技巧

手动SIMD编程通过编译器intrinsics(如_mm_add_ps SSE加法)或直接用汇编。Intel ISPC(Implicit SPMD Program Compiler)提供C变种语言编译为SIMD代码。常见向量化模式：map(逐元素运算: f(x+1)→SIMD add)、reduce(求和:使用vector→shuffle reduction→横向加法)、scatter/gather(AVX2的vgatherdps根据索引向量加载不连续元素)。内存对齐(align to vector width——32/64字节对齐)减少跨cache line访问惩罚。Masked操作(AVX-512)按mask选择性应用操作——替代分支。

## 关键结论

1. AVX-512频率降低(CPU降频CPU基频以补偿功率)——这被称为AVX-512 offset 2. 编译器自动向量化通常被别名和复杂控制流阻挡(使用__restrict关键字) 3. 循环展开和reduction模式是自动向量化的关键 4. 向量长度增加和CPU频率的关系需要考虑(轻量SIMD在多数任务上优于重SIMD的降频困境) 5. 许多典型算法(矩阵乘法/sum/histogram)在SIMD下可见2x-16x加速

## 关联知识点

[[计算机组成原理-乱序执行与ROB]] [[计算机组成原理-GPU渲染管线与GPGPU]] [[C语言深入-restrict限定符]]
