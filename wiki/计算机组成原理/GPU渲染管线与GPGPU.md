---
title: "GPU渲染管线与GPGPU"
course: 计算机组成原理
chapter: 并行架构
difficulty: INTERMEDIATE
tags: [计算机组成, GPU, GPGPU, 渲染管线, CUDA]
aliases: [GPU Architecture, GPGPU, SIMT, CUDA]
source: "NVIDIA CUDA Programming Guide; H&P《Computer Architecture》Ch 4 GPU; Akeley & Hanrahan《Real-Time Graphics》"
updated_at: 2026-05-02
---

## 核心定义

GPU(Graphics Processing Unit)是大规模并行多线程架构。图形渲染管线阶段：顶点处理(vertex shader)→图元装配→光栅化(rasterization)→像素处理(fragment shader)→输出合并。GPGPU(General-Purpose GPU)将GPU用于非图形计算。NVIDIA的CUDA编程模型基于SIMT(Single Instruction Multiple Threads)——一组32个线程(warp)锁定在同一指令上执行(SIMD-like)。SM(Streaming Multiprocessor)是核心执行单元——每个SM有多个warp scheduler和大量的计算单元以及寄存器文件。

## CUDA核心抽象

CUDA的核心概念：grid→blocks→threads层次——所有线程在相同代码（kernel）但通过threadIdx/blockIdx区分各自处理的数据。共享内存(shared memory, 每个block可见, 约48-164KB/SM)是程序员管理的快速on-chip存储器(类似L1 cache但需显式同步——__syncthreads)。Glowal memory访问必须对齐(optimal alignment)且合并(coalesced)——相邻线程访问相邻地址才有效率(否则导致多次transaction)。Occupancy(占用率——活跃warp/SM上最大warp)是隐藏memory latency的关键(高占用>延迟容忍)。

## 关键结论

1. GPU不适合分支密集型算法(同一warp内分支diverge——损失性能) 2. GPU的寄存器压力(register pressure)限制活跃线程数 3. Tensor Core(Volta+)提供专门的矩阵乘法加速(适合深度学习) 4. 与CPU的同步需通过事件/stream(cudaMemcpyAsync/cudaStreamSynchronize) 5. Compute Capability决定了可用的CUDA特性版本

## 关联知识点

[[计算机组成原理-SIMD与向量化]] [[计算机组成原理-CPU缓存与局部性原理]] [[计算机图形学-PBR材质系统]]
