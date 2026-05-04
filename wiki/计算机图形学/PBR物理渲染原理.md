---
title: PBR物理渲染原理
course: 计算机图形学
chapter: 光照与着色
difficulty: ADVANCED
tags: [PBR, BRDF, 微表面模型, 能量守恒, 菲涅尔, 金属度工作流]
aliases: [Physically Based Rendering, PBR, BRDF, Microfacet Model]
source:
  - Physically Based Rendering (PBRT, Pharr & Humphreys) Chapter 8, 9
  - Real-Time Rendering (Akenine-Möller) Chapter 9, 10
  - GAMES101 课程 Lecture 16-17
updated_at: 2026-05-03
---

## 核心定义

PBR（Physically Based Rendering，物理渲染）是基于物理原理的光照和着色方法，核心目标是能量守恒和物理正确性。PBR 的数学基础是 BRDF（双向反射分布函数）$f_r(\omega_i, \omega_o) = \frac{dL_o(\omega_o)}{L_i(\omega_i) \cos\theta_i d\omega_i}$，描述了从入射方向 $\omega_i$ 到出射方向 $\omega_o$ 的反射光比例。BRDF 必须满足两个物理约束：互易性（Helmholtz reciprocity，$f_r(\omega_i, \omega_o) = f_r(\omega_o, \omega_i)$）和能量守恒（反射能量不超过入射能量，$\int_{\Omega} f_r \cos\theta_o d\omega_o \leq 1$）。

微表面理论（Microfacet Theory）将粗糙表面建模为大量微小镜面的集合。微表面 BRDF 为 $f_r = \frac{D(h) F(\omega_i, h) G(\omega_i, \omega_o)}{4 \cos\theta_i \cos\theta_o}$，其中 $D(h)$ 是法线分布函数（NDF，描述微表面法线方向的统计分布），常用 GGX/Trowbridge-Reitz 分布 $D(h) = \frac{\alpha^2}{\pi((\alpha^2-1)\cos^2\theta_h + 1)^2}$；$F$ 是菲涅尔项，描述入射角增大时反射率增加的现象（Schlick 近似 $F = F_0 + (1-F_0)(1-\cos\theta)^5$）；$G$ 是几何遮蔽项（Geometry Function），描述微表面间的自遮挡，常用 Smith-GGX 模型。金属度工作流（Metallic Workflow）用两个参数描述材质：金属度（metallic，0=非金属，1=金属）和粗糙度（roughness）。非金属的 $F_0$ 约为 0.04，金属的 $F_0$ 等于 albedo 颜色。

## 关键结论

- 能量守恒要求漫反射和镜面反射的总能量不超过入射能量：$k_d + k_s \leq 1$，PBR 中 $k_d = (1 - F)(1 - metallic)$
- 菲涅尔效应在掠射角（grazing angle）处反射率趋近于 1，这是水、金属等在掠射角处看起来更亮的物理原因
- GGX 分布比 Blinn-Phong 分布有更好的长尾特性（tails），更符合真实材质的测量数据
- IBL（基于图像的照明）用环境贴图作为光源，通过预计算辐照度贴图（irradiance map）和预过滤环境贴图（pre-filtered environment map）实现高效的环境光照
- Disney BRDF 是一个经验模型，包含十余个参数（粗糙度、金属度、次表面散射等），广泛用于离线渲染和游戏

## 易错点

1. **sRGB 与线性空间混淆**：PBR 的所有光照计算必须在线性空间中进行。纹理输入（如 albedo）需要从 sRGB 转换到线性空间，最终输出再转换回 sRGB。直接在 sRGB 空间做光照计算会导致颜色偏暗
2. **粗糙度和光滑度混淆**：Disney 模型使用"粗糙度"（roughness），而某些引擎使用"光滑度"（smoothness = 1 - roughness），混用会导致材质效果反转
3. **菲涅尔项的 $F_0$ 设置错误**：非金属的 $F_0$ 在 0.02-0.05 范围内（由折射率决定），金属的 $F_0$ 等于 albedo 颜色。错误地将非金属的 $F_0$ 设为 1 会导致"看起来像金属"

## 例题

**题目**：一个非金属表面的粗糙度 $\alpha = 0.5$，折射率 $n = 1.5$（玻璃），在法线方向（$\theta = 0°$）处的菲涅尔反射率是多少？在掠射角（$\theta = 85°$）处呢？

**解答**：

第一步，计算法线方向的菲涅尔反射率 $F_0$（垂直入射）：
$$F_0 = \left(\frac{n_1 - n_2}{n_1 + n_2}\right)^2 = \left(\frac{1 - 1.5}{1 + 1.5}\right)^2 = \left(\frac{-0.5}{2.5}\right)^2 = 0.04$$

第二步，用 Schlick 近似计算掠射角处的菲涅尔值：
$$F(85°) = F_0 + (1 - F_0)(1 - \cos 85°)^5 = 0.04 + 0.96 \times (1 - 0.087)^5$$
$$= 0.04 + 0.96 \times (0.913)^5 = 0.04 + 0.96 \times 0.638 = 0.04 + 0.613 = 0.653$$

法线方向反射率仅 4%，但掠射角处反射率高达 65.3%。这就是为什么从侧面看窗户玻璃时能看到很强的反射——菲涅尔效应。

## 关联页面

[[光照模型（Lambert/Phong/Blinn-Phong）]] [[环境映射与反射]] [[纹理映射与Mipmap]] [[全局光照与路径追踪]]
