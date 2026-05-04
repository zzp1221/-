---
title: 抗锯齿技术（MSAA/FXAA/TAA）
course: 计算机图形学
chapter: 高级渲染
difficulty: INTERMEDIATE
tags: [抗锯齿, MSAA, FXAA, TAA, 锯齿, 采样]
aliases: [Anti-Aliasing, Multisample AA, FXAA, Temporal AA]
source:
  - Real-Time Rendering (Akenine-Möller) Chapter 9, 12
  - Fundamentals of Computer Graphics (Marschner & Shirley) Chapter 8, 9
  - GAMES101 课程 Lecture 9
updated_at: 2026-05-03
---

## 核心定义

锯齿（Aliasing）是光栅化中由于采样不足导致的视觉伪影，表现为物体边缘的"阶梯"（jaggies）和纹理的摩尔纹（moiré pattern）。根据 Nyquist 采样定理，当信号频率超过采样频率的一半时会出现混叠。抗锯齿（Anti-Aliasing, AA）技术的目标是减少或消除这些伪影。

SSAA（Super-Sample Anti-Aliasing，超采样抗锯齿）在每个像素内使用多个采样点（如 $2 \times 2$），对每个采样点独立执行着色计算，然后平均。SSAA 质量最高但性能开销是原来的 4 倍。MSAA（Multisample Anti-Aliasing，多重采样抗锯齿）是 SSAA 的优化：每个像素有多个采样点（如 4x MSAA 有 4 个采样点），但片元着色器只执行一次（在像素中心），只有覆盖采样（coverage test）是每采样点独立的。MSAA 在几何边缘有很好的效果，但对纹理锯齿无效。MSAA 需要额外的显存存储多重采样纹理。

FXAA（Fast Approximate Anti-Aliasing）是后处理抗锯齿算法，在屏幕空间对边缘进行检测和模糊。FXAA 速度快（只需一次额外的全屏 pass），但可能导致细节模糊和时间闪烁。TAA（Temporal Anti-Aliasing，时间抗锯齿）利用多帧信息：每帧在像素内随机偏移采样位置（Jittering），然后与前几帧的结果混合。TAA 可以有效地减少几何和着色锯齿，但在快速运动时会导致鬼影（ghosting）和时间模糊。TAA 的实现需要运动向量（Motion Vector）来重投影前一帧的结果。

## 关键结论

- MSAA 的存储开销：4x MSAA 需要 4 倍的显存（多重采样深度缓冲和颜色缓冲），但着色计算只执行一次
- TAA 的核心是 Jittering（每帧随机偏移采样点）和重投影（Reprojection，利用运动向量将前一帧的结果映射到当前帧）
- TAA 的鬼影问题可以通过"亮度裁剪"（Clipping）缓解：限制混合后的颜色在当前帧颜色的范围内
- DLSS（Deep Learning Super Sampling）和 FSR（FidelityFX Super Resolution）是基于深度学习/算法的超分辨率技术，可以与 AA 结合使用
- 边缘检测抗锯齿（如 SMAA）先检测边缘，再在边缘处进行混合，平衡了质量和性能

## 易错点

1. **MSAA 与延迟渲染不兼容**：MSAA 的多重采样纹理在延迟渲染的 G-Buffer 阶段会产生巨大的显存开销（4x MSAA 需要 4 倍的 G-Buffer）。通常延迟渲染使用 TAA 或 FXAA
2. **TAA 的 Jittering 不足**：如果采样位置的偏移模式不是均匀分布的（如 Halton 序列），TAA 的收敛速度会变慢，需要更多帧才能消除锯齿
3. **FXAA 的细节损失**：FXAA 会模糊所有检测到的"边缘"，包括纹理细节中的边缘（如树叶、铁丝网），导致细节丢失

## 例题

**题目**：一个 $1920 \times 1080$ 的屏幕使用 4x MSAA，颜色缓冲为 RGBA8（每通道 8 位）。计算 MSAA 颜色缓冲的显存开销。

**解答**：

第一步，计算单采样颜色缓冲的大小：
$$\text{单采样} = 1920 \times 1080 \times 4 \text{ 字节} = 8,294,400 \text{ 字节} \approx 7.91 \text{ MB}$$

第二步，4x MSAA 颜色缓冲的大小：
$$\text{4x MSAA} = 8,294,400 \times 4 = 33,177,600 \text{ 字节} \approx 31.64 \text{ MB}$$

还需要加上 4x MSAA 深度缓冲（通常 32 位）：
$$\text{4x MSAA 深度} = 1920 \times 1080 \times 4 \times 4 = 33,177,600 \text{ 字节} \approx 31.64 \text{ MB}$$

总计：约 63.28 MB。对比无 MSAA 的 7.91 MB + 7.91 MB = 15.82 MB，4x MSAA 增加了约 47.46 MB 显存。

## 关联页面

[[光栅化算法]] [[延迟渲染与前向+]] [[HDR与色调映射]] [[屏幕空间反射SSR]]
