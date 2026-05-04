---
title: 阴影映射Shadow Map
course: 计算机图形学
chapter: 阴影与反射
difficulty: INTERMEDIATE
tags: [阴影映射, Shadow Map, 深度比较, 阴影锯齿, PCF]
aliases: [Shadow Mapping, Shadow Map, Percentage Closer Filtering]
source:
  - Fundamentals of Computer Graphics (Marschner & Shirley) Chapter 11
  - Real-Time Rendering (Akenine-Möller) Chapter 7
  - GAMES101 课程 Lecture 12
updated_at: 2026-05-03
---

## 核心定义

阴影映射（Shadow Mapping）是最广泛使用的实时阴影技术，由 Lance Williams 在 1978 年提出。算法分两步：(1) 从光源视角渲染场景，只存储深度缓冲（Shadow Map）；(2) 从相机视角渲染场景时，将每个片元变换到光源空间，比较其深度值与 Shadow Map 中存储的深度值。如果片元深度大于 Shadow Map 中的值，说明有其他物体更靠近光源，该片元在阴影中。

Shadow Map 的分辨率决定了阴影质量。分辨率不足会导致阴影锯齿（Shadow Aliasing）——阴影边缘出现明显的块状伪影。解决方案包括：级联阴影映射（Cascaded Shadow Maps, CSM）将视锥体分为多个层级，每个层级使用独立的 Shadow Map，近处用高分辨率，远处用低分辨率；透视阴影映射（Perspective Shadow Maps, PSM）对 Shadow Map 应用透视变换，使近处分配更多分辨率。PCF（Percentage Closer Filtering）在比较深度前对 Shadow Map 的邻域进行采样，产生软阴影边缘。PCSS（Percentage Closer Soft Shadows）根据遮挡物与接收面的距离动态调整 PCF 的采样半径，实现物理正确的软阴影。阴影偏移（Shadow Bias）用于解决自阴影问题：在比较深度时给 Shadow Map 的深度值加上一个小的偏移量。

## 关键结论

- Shadow Map 是基于图像的阴影方法，复杂度与场景几何无关，适合复杂场景
- 级联阴影映射（CSM）将视锥体分为 3-4 级（如 0-10m, 10-50m, 50-200m），每级独立的 Shadow Map，是游戏引擎的标准做法
- PCF 的采样模式：$3 \times 3$ 或 $5 \times 5$ 的泊松圆盘采样，或使用随机旋转的采样核
- Shadow Map 的深度比较可以使用硬件支持的 `sampler2DShadow`，自动执行比较和插值
- 双向阴影映射（Dual Shadow Maps）同时存储正面和背面深度，可以正确处理自阴影

## 易错点

1. **Shadow Bias 设置不当**：bias 太小会导致自阴影（surface acne），bias 太大会导致阴影脱离物体（Peter Panning）。正确的 bias 需要根据表面法线和光线方向调整
2. **Shadow Map 分辨率不足**：低分辨率 Shadow Map 在近距离观察时阴影边缘会出现明显的锯齿。CSM 可以缓解但不能完全解决
3. **透视投影的 Shadow Map 精度问题**：透视投影的 Shadow Map 在远处精度很低（非线性深度分布）。线性化深度或使用对数深度可以改善

## 例题

**题目**：一个 Shadow Map 的分辨率为 $1024 \times 1024$，覆盖从光源出发的 $90°$ 视锥角。一个物体距离光源 10 米，计算该处 Shadow Map 每个纹素对应的世界空间大小。

**解答**：

第一步，计算 Shadow Map 覆盖的范围。在距离光源 $d$ 处，$90°$ 视锥角覆盖的范围为：
$$\text{范围} = 2d \cdot \tan(45°) = 2 \times 10 \times 1 = 20 \text{ 米}$$

第二步，计算每个纹素的世界空间大小：
$$\text{纹素大小} = \frac{20}{1024} \approx 0.0195 \text{ 米} \approx 2 \text{ 厘米}$$

在 10 米距离处，Shadow Map 的每个纹素对应约 2 厘米。小于 2 厘米的物体细节无法在阴影中体现，这就是 Shadow Map 的分辨率限制。

## 关联页面

[[阴影体Shadow Volume]] [[片元着色与深度测试]] [[级联阴影映射]] [[环境映射与反射]]
