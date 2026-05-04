---
title: GPU通用计算GPGPU
course: 计算机图形学
chapter: 高级渲染
difficulty: INTERMEDIATE
tags: [GPGPU, 计算着色器, CUDA, OpenCL, GPU并行计算]
aliases: [GPGPU, Compute Shader, GPU Computing, Parallel Computing]
source:
  - Real-Time Rendering (Akenine-Möller) Chapter 18
  - GPU Gems Series (NVIDIA)
  - CUDA Programming Guide (NVIDIA)
updated_at: 2026-05-03
---

## 核心定义

GPGPU（General-Purpose Computing on GPU，GPU 通用计算）是利用 GPU 的大规模并行计算能力执行非图形任务的技术。GPU 拥有数千个计算核心（如 NVIDIA RTX 4090 有 16384 个 CUDA 核心），擅长执行大量相同操作的并行任务（SIMT/SIMD 模型）。计算着色器（Compute Shader）是图形 API（OpenGL/Vulkan/DirectX）中的通用计算接口，独立于渲染管线，可以在任意时间执行。计算着色器使用工作组（Work Group）模型：每个工作组包含多个工作项（Work Item），工作组内的工作项可以共享内存（Shared Memory）并通过屏障（Barrier）同步。

CUDA（Compute Unified Device Architecture）是 NVIDIA 的 GPGPU 编程框架，提供 C/C++ 扩展语言和运行时 API。CUDA 的核心概念：线程层次（Thread Hierarchy）分为 Grid、Block、Thread；内存层次（Memory Hierarchy）包括全局内存（Global Memory，大容量高延迟）、共享内存（Shared Memory，小容量低延迟，工作组内共享）、寄存器（Register，最快但最少）。OpenCL 是跨平台的 GPGPU 标准，支持 CPU、GPU、FPGA 等多种设备。Vulkan 的计算管线支持计算着色器，通过描述符集（Descriptor Set）绑定资源，通过命令缓冲提交计算命令。

## 关键结论

- GPU 计算的性能优势在于并行度：数千个线程同时执行，隐藏内存延迟。如果任务的并行度不足，GPU 利用率低
- 共享内存（Shared Memory）的访问速度比全局内存快 10-100 倍，是优化 GPU 程序的关键。典型模式：将全局内存的数据加载到共享内存，工作组内协作处理
- GPU 的 Warp/Wavefront 执行模型：32 个线程（NVIDIA）或 64 个线程（AMD）同步执行相同的指令。分支分歧（Branch Divergence）会导致性能下降
- 计算着色器在图形管线中的应用：粒子系统更新、后处理（高斯模糊、SSAO）、光源剔除（前向+）、体渲染的光线行进
- GPU 的内存带宽（如 RTX 4090 的 1 TB/s）远高于 CPU（约 50 GB/s），但延迟也更高。优化策略是提高内存访问的合并度（Coalesced Access）

## 易错点

1. **线程同步问题**：工作组内的线程通过 barrier 同步，但不同工作组之间无法同步。如果需要全局同步，需要多次内核启动（kernel launch）
2. **分支分歧（Branch Divergence）**：同一个 Warp 中如果线程走不同的分支（if-else），两个分支都会被执行（只是结果被掩码选择），性能下降。应尽量让同一个 Warp 的线程走相同的分支
3. **全局内存的合并访问**：相邻线程应该访问相邻的内存地址，否则内存事务会分裂（memory transaction splitting），带宽利用率下降

## 例题

**题目**：一个 CUDA 程序需要对长度为 $N = 10^6$ 的数组求和。每个线程块（Block）有 256 个线程，每个线程处理一个元素后进行块内归约（Reduction）。需要多少个线程块？归约需要多少步？

**解答**：

第一步，计算线程块数量：
$$\text{Block 数} = \lceil \frac{N}{256} \rceil = \lceil \frac{10^6}{256} \rceil = \lceil 3906.25 \rceil = 3907$$

第二步，块内归约步数：
每一步将活跃线程数减半：
$$\text{步数} = \log_2(256) = 8$$

归约过程：
- 第 1 步：256 个线程 -> 128 个部分和
- 第 2 步：128 -> 64
- ...
- 第 8 步：2 -> 1 个块内总和

最终得到 3907 个块的局部和，需要第二次内核启动（或 CPU 端）将它们相加得到最终结果。

## 关联页面

[[OpenGL与Vulkan架构对比]] [[粒子系统]] [[物理模拟基础]] [[体渲染与烟雾模拟]]
