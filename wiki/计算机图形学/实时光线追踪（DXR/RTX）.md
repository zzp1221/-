---
title: 实时光线追踪（DXR/RTX）
course: 计算机图形学
chapter: 光线追踪
difficulty: ADVANCED
tags: [实时光线追踪, DXR, RTX, 混合渲染, 降噪]
aliases: [Real-Time Ray Tracing, DXR, NVIDIA RTX, Hybrid Rendering]
source:
  - Real-Time Rendering (Akenine-Möller) Chapter 23
  - NVIDIA RTX Documentation
  - Microsoft DXR Specification
updated_at: 2026-05-03
---

## 核心定义

实时光线追踪（Real-Time Ray Tracing）是近年来图形学的重要突破，由 NVIDIA 在 2018 年推出 RTX 2080 GPU 首次实现硬件加速。RTX GPU 包含 RT Core（光线追踪核心），专门用于加速 BVH 遍历和光线-三角形求交。DXR（DirectX Raytracing）是 Microsoft 在 DirectX 12 中引入的光线追踪 API，定义了光线追踪管线的状态对象（包括 ray generation、closest hit、any hit、miss 着色器）。Vulkan 也通过 `VK_KHR_ray_tracing_pipeline` 扩展支持光线追踪。

实时光线追踪的核心挑战是性能：每帧只能发射有限的光线（每像素 1-4 条），导致严重的采样噪点。解决方案是混合渲染（Hybrid Rendering）：用光栅化处理主可见性（Primary Visibility），用光线追踪处理特定效果（反射、阴影、全局光照）。降噪（Denoising）是实时光线追踪的关键技术：对低采样率的噪声图像应用时空滤波器（Spatial-Temporal Filter），利用深度、法线、运动向量等辅助信息引导降噪。常用的降噪算法包括 SVGF（Spatiotemporal Variance-Guided Filtering）、NVIDIA 的 OptiX AI 降噪器。DXR 的着色器模型 6.3 引入了 ray tracing 着色器类型：RayGeneration（发射光线）、ClosestHit（最近交点处理）、AnyHit（任意交点处理，用于 alpha test）、Miss（光线未命中）。

## 关键结论

- RT Core 的 BVH 遍历速度是 CUDA 核心的 10 倍以上，但 BVH 的构建仍然在 CUDA 核心上执行
- DXR 的 Shader Table 机制允许每条光线调用不同的着色器，实现了灵活的材质系统
- 降噪算法的质量与采样率和时间稳定性密切相关：空间降噪会导致细节模糊，时间降噪会导致鬼影（ghosting）
- 神经网络降噪器（如 NVIDIA 的 OptiX AI Denoiser）在低采样率下比传统滤波器效果更好，但需要专用硬件支持
- Vulkan 的光线追踪扩展包括 `VK_KHR_ray_tracing_pipeline` 和 `VK_KHR_ray_query`（在任意着色器中发射光线）

## 易错点

1. **BVH 构建的 CPU 瓶颈**：动态场景中每帧需要重建 BVH，如果 BVH 构建在 CPU 上执行，会成为性能瓶颈。GPU 端的 BVH 构建（如 DXR 的 `BuildRaytracingAccelerationStructure`）可以缓解
2. **降噪的时间稳定性问题**：时间降噪器依赖前一帧的重投影结果，当物体快速移动或出现遮挡变化时，重投影失败会导致鬼影。需要使用可靠性权重和启发式规则
3. **Shader Table 的索引错误**：DXR 的 Shader Table 使用 Instance ID 和 Geometry ID 索引，索引错误会导致着色器调用错误，产生渲染 artifact

## 例题

**题目**：一个场景使用混合渲染：主可见性用光栅化（1 条光线/像素），反射用 1 条光线/像素，阴影用 1 条光线/像素。屏幕分辨率 $1920 \times 1080$，帧率目标 60 FPS。计算每秒需要发射的总光线数。

**解答**：

第一步，计算每帧的光线数：
- 主可见性光线（光栅化，不计）：0
- 反射光线：$1920 \times 1080 \times 1 = 2,073,600$
- 阴影光线：$1920 \times 1080 \times 1 = 2,073,600$
- 总计每帧：$4,147,200$ 条光线

第二步，计算每秒光线数：
$$\text{Rays/s} = 4,147,200 \times 60 = 248,832,000 \approx 2.49 \times 10^8 \text{ rays/s}$$

RTX 2080 Ti 的光线追踪性能约为 10 Giga Rays/s（$10^{10}$ rays/s），远超所需的 2.49 亿条/秒。但实际性能受 BVH 遍历深度、着色器复杂度等因素影响，实际可用性能约为理论峰值的 10-30%。

## 关联页面

[[光线追踪原理]] [[加速结构（BVH/KD-Tree）]] [[延迟渲染与前向+]] [[抗锯齿技术（MSAA/FXAA/TAA）]]
