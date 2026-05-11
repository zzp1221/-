---
title: "GPU架构与CUDA编程"
course: 计算机图形学
chapter: 并行计算
difficulty: ADVANCED
tags: [图形学, GPU, CUDA, 并行, 图形]
aliases: [GPU Architecture, CUDA Programming, Graphics Compute]
source: "NVIDIA CUDA Programming Guide; Akeley & Hanrahan real-time graphics; GPU Gems series (NVIDIA)"
updated_at: 2026-05-02
---

## 核心定义

现代GPU是高度并行化的many-core处理器。NVIDIA GPU的SM(Streaming Multiprocessor)：多个CUDA核心、专用Function Units(Tensor Core/RT Core)、L1 cache/shared memory和warp scheduler。warp(32线程)以SIMT模式执行——所有lane执行相同指令但在不同数据上(vergen)。Tensor Core(Volta+)提供4x4矩阵乘加(D=A*B+C)在单时钟周期内——对深度学习推理和光线追踪BVH的重要加速。Ray Tracing Core提供硬件加速的BVH遍历和ray-triangle intersection(帧内硬件加速)。

## CUDA编程模型

CUDA程序组织为grid→block→thread层级。Kernel函数(__global__)在GPU上以<<<gridDim,blockDim>>>启动——每个线程根据threadIdx和blockIdx计算全局数据索引。Memory hierarchy：register(每线程最快但有限——256 registers/thread最多影响活跃warp数)→shared memory(__shared__ — block可见,程序员管理,L1-like)→global memory(所有线程可见,最大但最慢——靠coalesced access保持带宽)。__syncthreads()在block内同步。Streams实现overlap传输+计算(异步kernel启动——concurrent copy and execute)。

## 关键结论

1. Warp divergence(同一warp内不同分支路径活跃)是GPU性能杀手(所有分支路径都执行但无效数据被屏蔽masked off) 2. 全局内存访问模式必须合并(coalesced)保证高带宽(block的相邻线程访问相邻地址——128B对齐) 3. Shared memory bank conflicts可能多线程访问同一bank的偏移(32-way bank stride padding解决) 4. Occupancy(活跃warp/SM的理论上限)是隐藏global memory latency的关键因素(延迟被另一个warp隐藏) 5. Unified Memory简化CPU-GPU数据迁移(自动页面迁移但可能有页错误延迟)

## 关联知识点

[[计算机组成原理-GPU渲染管线与GPGPU]] [[计算机图形学-PBR材质系统]] [[算法设计与分析-并行算法]]
