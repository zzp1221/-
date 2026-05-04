---
title: "GPU架构与CUDA编程模型"
course: 计算机组成原理
chapter: 并行计算
difficulty: INTERMEDIATE
tags: [GPU, CUDA, 并行, SIMT]
aliases: [GPU Architecture, CUDA]
source: "CUDA C Programming Guide; Computer Architecture: A Quantitative Approach (Hennessy & Patterson)"
updated_at: 2026-05-02
---

## 核心定义

GPU是大规模并行处理器——数千个简单核心(SIMT模型)。NVIDIA GPU架构：SM(流多处理器)=多个CUDA Core+共享内存+寄存器文件。Warp(32线程束)以锁步执行——分支(warp divergence)导致利用率降低。内存层次：Global Memory(大，慢，如HBM/GDDR)→L2 Cache→Shared Memory(SM内，用户管理，快的软件控制缓存)→寄存器。CUDA编程模型：Grid→Blocks→Threads。线程索引：blockIdx+blockDim+threadIdx。

## 关键结论

1. 内存合并(coalescing)：相邻线程访问相邻地址——warp级内存请求合并为一次 2. Bank conflict——共享内存的32 banks中多线程访问同一bank 3. GEMM(矩阵乘)tiling是GPU优化的经典案例

## 关联页面

[[SIMD与向量处理器]] [[多处理器与并行编程]]
