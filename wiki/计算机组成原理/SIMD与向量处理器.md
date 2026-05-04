---
title: "SIMD指令集与向量处理"
course: 计算机组成原理
chapter: 处理器设计
difficulty: INTERMEDIATE
tags: [计算机组成原理, SIMD, 向量, SSE, AVX, NEON]
aliases: [SIMD, Vector Processing]
source: "Computer Architecture: A Quantitative Approach (Hennessy & Patterson) 第4章; Intel Intrinsics Guide"
updated_at: 2026-05-02
---

## 核心定义

SIMD(Single Instruction Multiple Data)一条指令同时操作多个数据。Intel x86：MMX(64bit)→SSE(128bit)→AVX2(256bit)→AVX-512(512bit)。ARM：NEON(128bit)、SVE(可变向量长度)。操作：向量加/乘/乘加(FMA)、shuffle/permute重排、gather/scatter非连续访问、mask/predicate条件执行。数据对齐(alignment)影响性能(虽然后续架构放宽了限制)。向量化方式：编译器自动向量化、Intrinsic函数、手写汇编。

## 关键结论

1. AVX-512 heavy指令会导致降频(license throttling)→需评估实际收益 2. 向量宽度翻倍不等于2x性能(受限于内存带宽) 3. SVE的可变向量长度(VLA)解决向前兼容 4. GPGPU本质上是超宽SIMT而非纯SIMD

## 关联页面

[[超标量与乱序执行]] [[GPU架构基础]]
