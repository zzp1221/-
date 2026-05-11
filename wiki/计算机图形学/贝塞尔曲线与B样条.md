---
title: "贝塞尔曲线与B样条"
course: 计算机图形学
chapter: 曲线与曲面
difficulty: INTERMEDIATE
tags: [图形学, 贝塞尔, B样条, NURBS, 曲线]
aliases: [Bezier Curves, B-Splines, NURBS]
source: "Bezier 1966 (UNISURF); de Casteljau 1959; Piegl & Tiller《The NURBS Book》; Farin《Curves and Surfaces for CAGD》"
updated_at: 2026-05-02
---

## 核心定义

贝塞尔曲线(Bézier curves)由控制点P_0,...,P_n定义(通过Bernstein多项式基函数加权)：C(t)=Σ B_i^n(t)*P_i，其中B_i^n(t)=C(n,i)*t^i*(1-t)^(n-i)是Bernstein多项式。de Casteljau算法(几何评估——通过递归线性插值：P_i^(k)= (1-t)*P_i^(k-1) + t*P_(i+1)^(k-1))避免直接计算Bernstein多项式。贝塞尔曲线在一个控制点的小变动影响整条曲线(无局部控制)。凸包性质：曲线完全位于控制多边形的凸包内(用于碰撞检测的快速粗检)。

## B样条与NURBS

B样条(B-spline)通过节点向量(knot vector)定义基函数的支持范围——每个控制点的影响局限在少量区间内(局部控制)。基函数由Cox-de Boor递推定义。NURBS(Non-Uniform Rational B-Spline)添加权重将B样条投影到rational空间(用齐次坐标——每个控制点带权w_i)。NURBS可精确表示圆锥曲线(圆/椭圆/双曲线)——贝塞尔只能近似。NURBS用于CAD/CAM和影视制作(尤其在工业设计Rhino和汽车设计CATIA)。T样条(T-splines)允许无限顶点分辨率(非矩形控制grid——局部精化而无需引入冗余控制点)。

## 关键结论

1. 贝塞尔是B样条的特例(knot vector无内部节点) 2. B样条次数=order-1(与控制点数无关) 3. Clamped knots endpoint interpolation B样条通过首末控制点(重复节点) 4. NURBS的权重大于1时拉伸曲线更靠近控制点,权重小于1时推离 5. 有理形式存在权重可能导致设计困难——通常保持单位权重(用控制点/次数控制形状)

## 关联知识点

[[计算机图形学-骨骼动画与蒙皮]] [[计算机图形学-PBR材质系统]] [[数据结构-数值计算与逼近理论]]
