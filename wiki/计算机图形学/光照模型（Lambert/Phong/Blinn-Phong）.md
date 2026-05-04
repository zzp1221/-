---
title: 光照模型（Lambert/Phong/Blinn-Phong）
course: 计算机图形学
chapter: 光照与着色
difficulty: BASIC
tags: [光照模型, Lambert, Phong, Blinn-Phong, 镜面反射, 漫反射]
aliases: [Lighting Models, Lambertian, Phong Model, Blinn-Phong Model]
source:
  - Fundamentals of Computer Graphics (Marschner & Shirley) Chapter 10
  - GAMES101 课程 Lecture 8-9
  - Real-Time Rendering (Akenine-Möller) Chapter 5, 6
updated_at: 2026-05-03
---

## 核心定义

光照模型（Illumination Model）描述光与物体表面的交互，计算每个着色点的颜色。局部光照模型只考虑光源直接照射，不考虑物体间的间接光照（全局光照）。

Lambertian 漫反射模型：$L_d = k_d \cdot I \cdot \max(0, \mathbf{n} \cdot \mathbf{l})$，其中 $k_d$ 是漫反射系数（albedo），$I$ 是光源强度，$\mathbf{n}$ 是表面法线，$\mathbf{l}$ 是指向光源的方向。Lambert 模型假设表面是理想漫反射体（perfect diffuse surface），从任何方向观察亮度相同，亮度仅取决于法线与光线方向的夹角的余弦。$\max(0, \cdot)$ 确保背面不接收光照。

Phong 镜面反射模型：$L_s = k_s \cdot I \cdot \max(0, \mathbf{r} \cdot \mathbf{v})^p$，其中 $\mathbf{r}$ 是反射方向（$\mathbf{r} = 2(\mathbf{n} \cdot \mathbf{l})\mathbf{n} - \mathbf{l}$），$\mathbf{v}$ 是指向观察者的方向，$p$ 是光泽度指数（越大高光越集中）。Blinn-Phong 模型用半程向量 $\mathbf{h} = \frac{\mathbf{l} + \mathbf{v}}{|\mathbf{l} + \mathbf{v}|}$ 替代反射方向：$L_s = k_s \cdot I \cdot \max(0, \mathbf{n} \cdot \mathbf{h})^p$。Blinn-Phong 在 $\mathbf{l}$ 和 $\mathbf{v}$ 接近平行时与 Phong 结果相似，但计算更快（不需要计算反射），且在掠射角（grazing angle）时更物理合理。完整的 Blinn-Phong 模型（也称 Phong-Blinn 或 Modified Phong）包含环境光、漫反射和镜面反射三项：$L = k_a I_a + k_d I \max(0, \mathbf{n} \cdot \mathbf{l}) + k_s I \max(0, \mathbf{n} \cdot \mathbf{h})^p$。

## 关键结论

- Lambert 模型的能量守恒：漫反射系数 $k_d \in [0,1]$，$\int_{\Omega} k_d \frac{\cos\theta}{\pi} d\omega = k_d \leq 1$
- Phong 和 Blinn-Phong 不是物理正确的模型（不满足能量守恒，BRDF 不互易），但在实时渲染中广泛使用
- 环境光项 $k_a I_a$ 是对间接光照的极其粗糙近似，现代引擎用 IBL（Image-Based Lighting）替代
- 光照可以在顶点着色器（Gouraud 着色，每顶点计算）或片元着色器（Phong 着色，每像素计算）中进行
- 多光源情况下，每个光源的贡献独立计算后叠加：$L = \sum_{i} (L_{d,i} + L_{s,i}) + L_a$

## 易错点

1. **法线未归一化**：计算 $\mathbf{n} \cdot \mathbf{l}$ 前必须确保 $\mathbf{n}$ 和 $\mathbf{l}$ 都是单位向量，否则光照强度计算错误
2. **背面光照处理不当**：$\max(0, \mathbf{n} \cdot \mathbf{l})$ 将背面的光照截断为 0，这在某些情况下会导致物体背面完全黑暗。对于需要背面光照的情况（如双面材质），需要翻转法线
3. **镜面反射指数 p 的含义**：$p$ 越大高光越小越集中，但 $p$ 没有物理单位。Blinn-Phong 中相同的视觉效果需要的 $p$ 值约为 Phong 的 2-4 倍

## 例题

**题目**：使用 Blinn-Phong 模型计算着色点的颜色。已知：$k_a = (0.1, 0.1, 0.1)$, $k_d = (0.7, 0, 0)$（红色漫反射）, $k_s = (0.5, 0.5, 0.5)$, $p = 32$, $I_a = 1$, $I = 1$, $\mathbf{n} = (0, 0, 1)$, $\mathbf{l} = (0, 0, 1)$, $\mathbf{v} = (0, 0, 1)$。

**解答**：

第一步，计算半程向量：
$$\mathbf{h} = \frac{\mathbf{l} + \mathbf{v}}{|\mathbf{l} + \mathbf{v}|} = \frac{(0,0,1)+(0,0,1)}{|(0,0,2)|} = (0, 0, 1)$$

第二步，计算各项：
- 环境光：$L_a = k_a \cdot I_a = (0.1, 0.1, 0.1)$
- 漫反射：$\mathbf{n} \cdot \mathbf{l} = (0,0,1) \cdot (0,0,1) = 1$
  $L_d = k_d \cdot I \cdot 1 = (0.7, 0, 0) \cdot 1 \cdot 1 = (0.7, 0, 0)$
- 镜面反射：$\mathbf{n} \cdot \mathbf{h} = 1$
  $L_s = k_s \cdot I \cdot 1^{32} = (0.5, 0.5, 0.5) \cdot 1 \cdot 1 = (0.5, 0.5, 0.5)$

第三步，最终颜色：
$$L = L_a + L_d + L_s = (0.1+0.7+0.5, 0.1+0+0.5, 0.1+0+0.5) = (1.3, 0.6, 0.6)$$

颜色值超过 1.0，需要在显示前进行色调映射或截断到 $[0,1]$。

## 关联页面

[[着色频率（Flat/Gouraud/Phong Shading）]] [[PBR物理渲染原理]] [[纹理映射与Mipmap]] [[法线贴图与凹凸贴图]]
