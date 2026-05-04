---
title: 隐式曲面与CSG
course: 计算机图形学
chapter: 几何表示
difficulty: INTERMEDIATE
tags: [隐式曲面, CSG, 距离场, 布尔运算, 等值面]
aliases: [Implicit Surface, CSG, Signed Distance Field, Boolean Operations]
source:
  - Fundamentals of Computer Graphics (Marschner & Shirley) Chapter 12
  - Real-Time Rendering (Akenine-Möller) Chapter 14
  - Physically Based Rendering (PBRT) Chapter 3
updated_at: 2026-05-03
---

## 核心定义

隐式曲面（Implicit Surface）用标量场函数 $f(x,y,z)$ 的等值面定义：曲面是满足 $f(x,y,z) = c$ 的所有点的集合（通常 $c=0$）。与参数曲面不同，隐式曲面没有显式的参数化，无法直接求值曲面上的点。但隐式表示有独特优势：可以轻松判断一个点在曲面的内部（$f < 0$）还是外部（$f > 0$），方便进行布尔运算和碰撞检测。常见的隐式曲面类型包括：球面 $f = x^2 + y^2 + z^2 - r^2$、代数曲面（多项式定义）、Blobby/Metaball（多个球体的势场叠加，$f = \sum_i \frac{r_i^2}{|\mathbf{p} - \mathbf{c}_i|^2} - 1$，产生有机的融合效果）、有符号距离场（Signed Distance Field, SDF，$f$ 等于点到曲面的最短距离，内部为负）。

CSG（Constructive Solid Geometry，构造实体几何）通过布尔运算组合基本几何体（球、圆柱、圆锥、立方体等）。CSG 使用并集（Union）、交集（Intersection）、差集（Difference）三种布尔运算，结果用二叉树表示。CSG 的渲染通常通过光线追踪实现：对每条光线，递归地在 CSG 树的每个节点计算光线与子物体的交点，然后根据布尔运算合并交点区间。有符号距离场（SDF）的布尔运算非常简洁：并集 $f_{A \cup B} = \min(f_A, f_B)$，交集 $f_{A \cap B} = \max(f_A, f_B)$，差集 $f_{A - B} = \max(f_A, -f_B)$。SDF 的光线行进（Ray Marching）算法沿光线方向以 SDF 值为步长前进，保证不会穿过曲面。

## 关键结论

- SDF 的梯度等于曲面法线：$\nabla f = \mathbf{n}$（在曲面附近），可以用有限差分近似计算
- Ray Marching 算法：沿光线方向迭代前进，步长 = 当前点的 SDF 值，当 SDF 值小于阈值时认为到达曲面。这种方法保证不会"穿透"曲面
- Metaball 的融合效果来自势场的平滑叠加：当两个球体靠近时，势场在中间区域超过阈值，产生融合的曲面
- CSG 树的深度决定了布尔运算的复杂度，过多的嵌套会导致渲染性能下降
- SDF 的平滑最小值（smooth min）替代硬最小值可以产生平滑的融合效果，广泛用于程序化建模

## 易错点

1. **Ray Marching 的步长选择**：步长太大会导致"穿透"薄壁物体（但 SDF 保证不会穿透），步长太小会导致性能下降。通常设置最大步数和最小距离阈值
2. **SDF 的精度问题**：在远离曲面的区域，SDF 值可能不准确（特别是用网格采样存储的 SDF），导致法线计算错误
3. **CSG 的数值稳定性**：当两个物体的表面非常接近时，布尔运算的交点计算可能出现数值误差，导致"闪烁"或"裂缝"

## 例题

**题目**：两个球体的 SDF 分别为 $f_A = |\mathbf{p} - (0,0,0)| - 1$（单位球）和 $f_B = |\mathbf{p} - (1.5,0,0)| - 1$（中心在 $(1.5,0,0)$ 的单位球）。求并集 SDF 在点 $(0.75, 0, 0)$ 处的值。

**解答**：

第一步，计算点 $(0.75, 0, 0)$ 到两个球心的距离：
$$d_A = |(0.75, 0, 0) - (0, 0, 0)| = 0.75$$
$$d_B = |(0.75, 0, 0) - (1.5, 0, 0)| = 0.75$$

第二步，计算两个 SDF 值：
$$f_A = 0.75 - 1 = -0.25 \quad (\text{点在球 A 内部})$$
$$f_B = 0.75 - 1 = -0.25 \quad (\text{点在球 B 内部})$$

第三步，并集 SDF：
$$f_{A \cup B} = \min(f_A, f_B) = \min(-0.25, -0.25) = -0.25$$

并集 SDF 值为 $-0.25$，表示该点在并集曲面内部，距离表面 $0.25$ 个单位。由于两个球体在该区域重叠，并集曲面的边界由两个球体的表面融合而成。

## 关联页面

[[多边形网格与半边结构]] [[点云与体素]] [[光线追踪原理]] [[曲面表示（贝塞尔/B样条/NURBS）]]
