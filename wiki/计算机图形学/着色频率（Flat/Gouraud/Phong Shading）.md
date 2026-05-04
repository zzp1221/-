---
title: 着色频率（Flat/Gouraud/Phong Shading）
course: 计算机图形学
chapter: 光照与着色
difficulty: BASIC
tags: [着色频率, Flat Shading, Gouraud Shading, Phong Shading, 插值着色]
aliases: [Shading Frequency, Flat/Gouraud/Phong Shading]
source:
  - Fundamentals of Computer Graphics (Marschner & Shirley) Chapter 10
  - GAMES101 课程 Lecture 8-9
  - Real-Time Rendering (Akenine-Möller) Chapter 5
updated_at: 2026-05-03
---

## 核心定义

着色频率（Shading Frequency）指的是光照计算的执行频率——每个三角形、每个顶点还是每个像素。三种主要着色频率各有特点：

Flat Shading（平面着色）：对每个三角形只计算一次光照，通常使用三角形的一个顶点法线（或三角形面法线）计算颜色，三角形内部所有像素使用相同的颜色。Flat Shading 的优点是计算量最小，缺点是三角形边界处有明显的棱角感，低多边形模型看起来是"棱角分明"的。

Gouraud Shading（高洛德着色）：在每个顶点处计算光照得到顶点颜色，然后在光栅化阶段对顶点颜色进行线性插值得到每个像素的颜色。Gouraud Shading 比 Flat Shading 平滑得多，但对高光的表示有限——如果高光区域没有被顶点覆盖（高光完全在三角形内部），则高光会"丢失"。这是因为线性插值无法表示二次函数（高光项是非线性的）。

Phong Shading（冯氏着色）：在每个顶点处插值法线向量（而不是颜色），然后在每个像素处用插值后的法线重新计算光照。Phong Shading 能正确渲染高光，因为每个像素独立计算光照。需要注意：Phong Shading 与 Phong 光照模型是不同的概念——Phong Shading 指的是逐像素着色的方式，Phong 光照模型指的是镜面反射的数学模型。现代游戏通常使用 Phong Shading（逐像素着色）配合 Blinn-Phong 或 PBR 光照模型。

## 关键结论

- 着色频率的选择是质量与性能的权衡：Flat < Gouraud < Phong（质量递增，计算量递增）
- Gouraud Shading 中顶点法线的计算：平滑表面使用顶点相邻面法线的加权平均（面积或角度加权），硬边处复制面法线不平均
- Phong Shading 的法线插值必须在透视校正后进行，否则在斜视角度下会出现失真
- 实际 GPU 硬件的光栅化器自动对所有 varying 变量（包括法线）进行透视正确的重心坐标插值
- 高光在低多边形上用 Gouraud Shading 容易出现"高光丢失"问题，因为高光峰值可能完全在三角形内部

## 易错点

1. **混淆 Phong Shading 和 Phong 光照模型**：Phong Shading 是逐像素着色方法，Phong 光照模型是漫反射+镜面反射的数学模型。两者可以独立使用——可以用 Phong 光照模型配合 Gouraud Shading
2. **法线平均导致硬边丢失**：如果对所有顶点都进行法线平均，模型上的硬边（如立方体的棱）会变得圆滑。正确做法是对硬边复制独立的顶点法线
3. **Gouraud Shading 的能量不守恒**：线性插值后的颜色可能超过原始计算的颜色范围（凸函数的线性插值总是低于函数值），导致高光变暗。也可能在某些情况下出现颜色超出 $[0,1]$ 范围

## 例题

**题目**：一个三角形三个顶点的法线分别为 $\mathbf{n}_A = (0,0,1)$, $\mathbf{n}_B = (1,0,0)$, $\mathbf{n}_C = (0,1,0)$。光源方向 $\mathbf{l} = (0,0,1)$。分别用 Flat、Gouraud、Phong Shading 计算三角形中心点的颜色（仅考虑漫反射，$k_d = 1$）。

**解答**：

**Flat Shading**：使用顶点 A 的法线（或面法线，此处用 A）：
$$L = \max(0, (0,0,1) \cdot (0,0,1)) = 1$$
整个三角形颜色为 1。

**Gouraud Shading**：
先计算三个顶点的颜色：
$$L_A = \max(0, (0,0,1) \cdot (0,0,1)) = 1$$
$$L_B = \max(0, (1,0,0) \cdot (0,0,1)) = 0$$
$$L_C = \max(0, (0,1,0) \cdot (0,0,1)) = 0$$

中心点的重心坐标为 $(\frac{1}{3}, \frac{1}{3}, \frac{1}{3})$，插值后：
$$L_{center} = \frac{1}{3} \cdot 1 + \frac{1}{3} \cdot 0 + \frac{1}{3} \cdot 0 = \frac{1}{3} \approx 0.33$$

**Phong Shading**：
先插值法线：
$$\mathbf{n}_{center} = \frac{1}{3}(0,0,1) + \frac{1}{3}(1,0,0) + \frac{1}{3}(0,1,0) = (\frac{1}{3}, \frac{1}{3}, \frac{1}{3})$$

归一化：$|\mathbf{n}_{center}| = \frac{\sqrt{3}}{3}$，$\hat{\mathbf{n}}_{center} = (\frac{1}{\sqrt{3}}, \frac{1}{\sqrt{3}}, \frac{1}{\sqrt{3}})$

逐像素计算：
$$L = \max(0, \frac{1}{\sqrt{3}}) = \frac{1}{\sqrt{3}} \approx 0.577$$

Phong Shading 的结果（0.577）比 Gouraud Shading（0.33）更亮，因为非线性函数（余弦）的插值与插值后的余弦值不同。

## 关联页面

[[光照模型（Lambert/Phong/Blinn-Phong）]] [[光栅化算法]] [[法线贴图与凹凸贴图]] [[PBR物理渲染原理]]
