---
title: 环境光遮蔽AO
course: 计算机图形学
chapter: 光照与着色
difficulty: INTERMEDIATE
tags: [环境光遮蔽, AO, SSAO, 烘焙AO, 屏幕空间]
aliases: [Ambient Occlusion, SSAO, Screen Space Ambient Occlusion]
source:
  - Real-Time Rendering (Akenine-Möller) Chapter 11
  - Fundamentals of Computer Graphics (Marschner & Shirley) Chapter 11, 24
  - GAMES101 课程 Lecture 17
updated_at: 2026-05-03
---

## 核心定义

环境光遮蔽（Ambient Occlusion, AO）是一种近似全局光照的技术，用于计算表面点被周围几何体遮挡环境光的程度。AO 的核心思想：凹陷处、接缝处、角落处接收的环境光较少（被周围几何体遮挡），应该更暗。数学上，AO 值定义为：$A(\mathbf{p}) = \frac{1}{\pi} \int_{\Omega} V(\mathbf{p}, \omega) \cos\theta \, d\omega$，其中 $V(\mathbf{p}, \omega)$ 是可见性函数（从点 $\mathbf{p}$ 沿方向 $\omega$ 能否看到天空，可见为 1，被遮挡为 0），$\cos\theta$ 是法线余弦权重。AO 值为 1 表示完全暴露（无遮挡），0 表示完全被遮挡。

烘焙 AO（Baked AO）在离线阶段预计算每个顶点或纹素的 AO 值，存储在顶点颜色或纹理中。这种方法质量高但只适用于静态场景。SSAO（Screen Space Ambient Occlusion，屏幕空间环境光遮蔽）是实时渲染中的主流方法，在屏幕空间对每个像素采样周围的深度缓冲来估计遮挡。SSAO 的基本算法：对每个像素，在其法线方向的半球内随机采样多个点，检查这些点的深度是否小于深度缓冲中的值（被遮挡），遮挡比例就是 AO 值。SSAO 的缺点是依赖屏幕空间信息（只能看到当前可见的几何体），可能产生自遮挡伪影和噪点。改进算法包括 SSDO（Screen Space Directional Occlusion，考虑方向性遮挡）、HBAO+（Horizon-Based AO，基于水平角的 AO）、GTAO（Ground Truth AO，基于物理的 AO）。

## 关键结论

- AO 假设环境光是均匀的各向同性漫射光，这个假设在户外场景中基本成立，但在有强方向光源或彩色光源时不够准确
- SSAO 的采样策略很重要：使用半球采样（沿法线方向的半球）比全球采样更准确，使用泊松圆盘分布或 Halton 序列可以减少噪点
- SSAO 的结果通常需要模糊（blur）处理以减少采样噪点，但过度模糊会丢失细节
- 烘焙 AO 可以与光照贴图（Lightmap）结合，存储更丰富的光照信息
- HBAO+ 和 GTAO 通过分析深度缓冲的水平方向梯度来估计遮挡，比随机采样更高效且噪点更少

## 易错点

1. **SSAO 的自遮挡问题**：在平坦表面上，如果采样半径过大，采样点可能位于表面下方（深度缓冲中更近），导致平坦区域出现错误的遮挡。解决方法是使用法线方向的半球采样并排除位于表面下方的采样点
2. **AO 值的范围误解**：AO 值是 $[0, 1]$ 的遮挡因子，通常用于乘以环境光。但某些引擎中 AO 也被应用于间接光照（diffuse GI），此时需要更谨慎的处理
3. **深度缓冲的非线性**：SSAO 采样深度缓冲时，深度值是非线性的（透视投影后的 $z$ 值），直接比较深度值会导致近距离和远距离的遮挡判断不一致。需要将深度值转换到线性空间

## 例题

**题目**：一个 SSAO 算法对每个像素在法线半球内采样 16 个点。某像素的 16 个采样点中，有 4 个点的深度大于深度缓冲中的值（被遮挡）。求该像素的 AO 值。

**解答**：

AO 值的计算公式：
$$A = 1 - \frac{\text{被遮挡的采样点数}}{\text{总采样点数}} = 1 - \frac{4}{16} = 1 - 0.25 = 0.75$$

AO 值为 0.75，表示该点有 25% 的环境光被遮挡。

在片元着色器中，该像素的环境光贡献将乘以 0.75：
$$L_{ambient} = AO \cdot k_a \cdot I_a = 0.75 \cdot k_a \cdot I_a$$

如果该像素位于墙角处，遮挡比例可能更高（如 8/16），AO 值为 0.5，墙角会明显变暗，产生更真实的阴影效果。

## 关联页面

[[PBR物理渲染原理]] [[延迟渲染与前向+]] [[屏幕空间反射SSR]] [[光照模型（Lambert/Phong/Blinn-Phong）]]
