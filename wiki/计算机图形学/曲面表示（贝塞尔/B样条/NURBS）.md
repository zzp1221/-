---
title: 曲面表示（贝塞尔/B样条/NURBS）
course: 计算机图形学
chapter: 几何表示
difficulty: INTERMEDIATE
tags: [贝塞尔曲面, B样条, NURBS, 参数曲面, 控制点]
aliases: [Bezier Surface, B-Spline, NURBS Surface, Parametric Surface]
source:
  - Fundamentals of Computer Graphics (Marschner & Shirley) Chapter 15
  - GAMES101 课程 Lecture 11
  - Real-Time Rendering (Akenine-Möller) Chapter 14
updated_at: 2026-05-03
---

## 核心定义

贝塞尔曲面（Bezier Surface）是贝塞尔曲线在二维参数域上的推广。$m \times n$ 阶贝塞尔曲面由 $(m+1)(n+1)$ 个控制点定义：$\mathbf{S}(u,v) = \sum_{i=0}^{m}\sum_{j=0}^{n} B_{i,m}(u) B_{j,n}(v) \mathbf{P}_{ij}$，其中 $B_{i,n}(t) = \binom{n}{i}t^i(1-t)^{n-i}$ 是 Bernstein 基函数。贝塞尔曲面继承了贝塞尔曲线的凸包性质和端点插值性质。de Casteljau 算法可以扩展到曲面：先对控制网格的一行应用 de Casteljau 算法，再对结果列应用。

B 样条曲面（B-Spline Surface）使用分段多项式基函数，提供局部控制性：移动一个控制点只影响曲面的局部区域。B 样条的节点向量（knot vector）定义了参数域的分段，均匀节点向量对应均匀 B 样条。NURBS（Non-Uniform Rational B-Splines，非均匀有理 B 样条）是 B 样条的进一步推广，每个控制点附加一个权重 $w_i$：$\mathbf{S}(u,v) = \frac{\sum_{i,j} w_{ij} N_{i,p}(u) N_{j,q}(v) \mathbf{P}_{ij}}{\sum_{i,j} w_{ij} N_{i,p}(u) N_{j,q}(v)}$。NURBS 的关键优势是可以精确表示圆锥曲线（圆、椭圆、抛物线、双曲线），这是非有理 B 样条做不到的。NURBS 是 CAD/CAM 工业标准，广泛用于汽车、飞机等的外形设计。

## 关键结论

- 贝塞尔曲面是 NURBS 的特例（权重均为 1，节点向量为 $[0,...,0,1,...,1]$）
- B 样条的局部支撑性：$p$ 阶 B 样条基函数 $N_{i,p}(t)$ 在 $p+1$ 个节点区间上非零，移动一个控制点只影响曲面的局部区域
- NURBS 的权重 $w_i$ 控制曲面靠近控制点的程度：$w_i \to \infty$ 时曲面趋近控制点 $\mathbf{P}_i$
- 贝塞尔曲面片可以通过 G1/C1 连续性条件拼接为光滑曲面
- 曲面的法线可以通过偏导数的叉积计算：$\mathbf{n} = \frac{\partial \mathbf{S}}{\partial u} \times \frac{\partial \mathbf{S}}{\partial v}$

## 易错点

1. **节点向量的理解**：NURBS 的节点向量中，重复节点会降低基函数的连续性。$p$ 阶 B 样条在节点处最多 $C^{p-1}$ 连续，如果节点重复 $k$ 次，连续性降为 $C^{p-k}$
2. **有理 vs 非有理的混淆**：NURBS 是"有理"的（分子分母都是多项式），这使得它在透视变换下具有不变性，但计算比非有理 B 样条复杂
3. **权重为零的陷阱**：如果某个控制点的权重 $w_i = 0$，该控制点对曲面没有影响，但在计算中可能导致除零错误

## 例题

**题目**：一个 $2 \times 2$ 阶贝塞尔曲面的控制点网格为：
$$\mathbf{P}_{00}=(0,0,0), \mathbf{P}_{01}=(1,0,0), \mathbf{P}_{02}=(2,0,0)$$
$$\mathbf{P}_{10}=(0,1,0), \mathbf{P}_{11}=(1,1,1), \mathbf{P}_{12}=(2,1,0)$$
$$\mathbf{P}_{20}=(0,2,0), \mathbf{P}_{21}=(1,2,0), \mathbf{P}_{22}=(2,2,0)$$

求参数 $(u,v) = (0.5, 0.5)$ 处的曲面点。

**解答**：

第一步，计算 $u = 0.5$ 处的 Bernstein 基函数（$n=2$）：
$$B_{0,2}(0.5) = (1-0.5)^2 = 0.25$$
$$B_{1,2}(0.5) = 2 \times 0.5 \times (1-0.5) = 0.5$$
$$B_{2,2}(0.5) = 0.5^2 = 0.25$$

$v = 0.5$ 处的基函数相同（对称）。

第二步，对每行控制点在 $u$ 方向插值：
$$\mathbf{Q}_0 = 0.25(0,0,0) + 0.5(1,0,0) + 0.25(2,0,0) = (1, 0, 0)$$
$$\mathbf{Q}_1 = 0.25(0,1,0) + 0.5(1,1,1) + 0.25(2,1,0) = (1, 1, 0.5)$$
$$\mathbf{Q}_2 = 0.25(0,2,0) + 0.5(1,2,0) + 0.25(2,2,0) = (1, 2, 0)$$

第三步，对结果在 $v$ 方向插值：
$$\mathbf{S}(0.5, 0.5) = 0.25(1,0,0) + 0.5(1,1,0.5) + 0.25(1,2,0) = (1, 1, 0.25)$$

曲面在 $(0.5, 0.5)$ 处的点为 $(1, 1, 0.25)$，即曲面中心略微隆起（$z=0.25$），反映了中心控制点 $\mathbf{P}_{11}$ 的 $z=1$ 值的影响。

## 关联页面

[[插值方法（线性/球面/贝塞尔）]] [[细分曲面]] [[多边形网格与半边结构]] [[隐式曲面与CSG]]
