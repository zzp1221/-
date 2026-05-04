---
title: HDR与色调映射
course: 计算机图形学
chapter: 高级渲染
difficulty: INTERMEDIATE
tags: [HDR, 色调映射, Tone Mapping, 曝光, 亮度适应]
aliases: [High Dynamic Range, Tone Mapping, Exposure, Luminance Adaptation]
source:
  - Real-Time Rendering (Akenine-Möller) Chapter 11
  - Fundamentals of Computer Graphics (Marschner & Shirley) Chapter 21
  - GAMES101 课程 Lecture 17
updated_at: 2026-05-03
---

## 核心定义

HDR（High Dynamic Range，高动态范围）渲染指的是在渲染管线中使用超过 $[0,1]$ 范围的浮点精度颜色值，保留场景中从极暗到极亮的完整亮度范围。真实世界的亮度范围非常大：月光约 0.1 nit，阳光约 100,000 nit，动态范围达到 $10^6$。标准 LDR 显示器只能显示约 8 位（256 级）的亮度，无法直接显示 HDR 内容。色调映射（Tone Mapping）是将 HDR 颜色值压缩到显示器可显示的 $[0,1]$ 范围的过程。

色调映射算子（Tone Mapping Operator, TMO）分为全局算子和局部算子。全局算子对所有像素使用相同的映射函数：Reinhard 算子 $L_{display} = \frac{L}{1+L}$ 简单但保留了高光细节；Filmic 算子（如 Hable/Uncharted 2）模拟胶片的 S 形响应曲线，在暗部和亮部有更好的对比度。局部算子考虑像素的邻域信息：局部适应（Local Adaptation）根据周围区域的亮度调整映射曲线，可以增强局部对比度。曝光（Exposure）控制整体亮度：$L_{mapped} = TMO(L \times 2^{EV})$，其中 $EV$ 是曝光值。自动曝光（Auto Exposure）根据场景的平均亮度（或对数平均亮度）自动调整曝光值，模拟人眼的亮度适应。Bloom（辉光）效果在色调映射前提取高亮度区域并模糊，产生光晕。

## 关键结论

- HDR 渲染管线：场景渲染到浮点 FBO（如 GL_RGBA16F）-> Bloom 处理 -> 色调映射 -> 最终输出到 LDR 屏幕
- Reinhard 算子的全局版本：$L_{display} = \frac{L_{white}^2 \cdot L}{L_{white}^2 + L}$，$L_{white}$ 是映射到白色的亮度值
- 自动曝光的对数平均亮度：$L_{avg} = \exp\left(\frac{1}{N}\sum_{i} \log(\delta + L_i)\right)$，使用对数避免极亮像素主导
- Bloom 的实现：提取亮度超过阈值的像素 -> 高斯模糊（通常使用多 pass 降低采样）-> 与原图叠加
- 色调映射应该在线性空间中完成，sRGB 转换在色调映射之后执行

## 易错点

1. **色调映射的顺序错误**：Bloom 应该在色调映射之前执行（在线性 HDR 空间中模糊），否则模糊效果在非线性空间中不正确
2. **自动曝光的闪烁**：场景亮度突然变化时（如从室内到室外），自动曝光需要时间适应。如果适应速度太快会导致闪烁，太慢会导致过渡不自然
3. **Bloom 的阈值设置**：Bloom 阈值太低会导致所有物体都产生辉光，太高则只有极亮光源有辉光。通常使用 $[0.8, 1.0]$ 的阈值范围

## 例题

**题目**：一个 HDR 场景中有三个像素的亮度值分别为 $L_1 = 0.1$, $L_2 = 1.0$, $L_3 = 10.0$。使用 Reinhard 算子 $L_{display} = \frac{L}{1+L}$ 计算色调映射后的亮度。

**解答**：

$$L_{1,display} = \frac{0.1}{1+0.1} = \frac{0.1}{1.1} \approx 0.091$$
$$L_{2,display} = \frac{1.0}{1+1.0} = \frac{1.0}{2.0} = 0.5$$
$$L_{3,display} = \frac{10.0}{1+10.0} = \frac{10.0}{11.0} \approx 0.909$$

分析：
- 暗部（$L_1 = 0.1$）几乎不变（0.091 ≈ 0.1）
- 中间调（$L_2 = 1.0$）映射到 0.5
- 亮部（$L_3 = 10.0$）从 10.0 压缩到 0.909，但仍然保留了与中间调的区分

Reinhard 算子将无限的亮度范围压缩到 $[0, 1)$，但 $L=1$ 永远映射不到 1（$\frac{1}{2} = 0.5$）。使用 $L_{white}$ 参数可以控制映射到白色的亮度值。

## 关联页面

[[抗锯齿技术（MSAA/FXAA/TAA）]] [[延迟渲染与前向+]] [[模板缓冲与后处理]] [[PBR物理渲染原理]]
