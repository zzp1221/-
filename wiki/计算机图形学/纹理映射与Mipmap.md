---
title: 纹理映射与Mipmap
course: 计算机图形学
chapter: 光照与着色
difficulty: BASIC
tags: [纹理映射, Mipmap, 纹理过滤, 纹理采样, UV坐标]
aliases: [Texture Mapping, Mipmap, UV Mapping, Texture Filtering]
source:
  - Fundamentals of Computer Graphics (Marschner & Shirley) Chapter 11
  - GAMES101 课程 Lecture 9-10
  - Real-Time Rendering (Akenine-Möller) Chapter 6
updated_at: 2026-05-03
---

## 核心定义

纹理映射（Texture Mapping）是将二维图像（纹理）"贴"到三维物体表面的技术。每个三角形顶点关联一个二维纹理坐标 $(u, v)$（UV 坐标），光栅化阶段对 UV 坐标进行插值，片元着色器中使用插值后的 UV 坐标采样纹理得到颜色。UV 坐标通常在 $[0, 1]$ 范围内，$(0,0)$ 对应纹理左下角，$(1,1)$ 对应右上角。超出范围的 UV 可以通过寻址模式处理：重复（Repeat/Tile）、镜像（Mirror）、夹取（Clamp）。

纹理过滤（Texture Filtering）决定了纹理像素（texel）到屏幕像素的映射方式。最近邻过滤（Nearest Neighbor）取最近的纹素，速度快但有锯齿。双线性过滤（Bilinear Interpolation）对最近的 4 个纹素做加权平均，结果平滑。Mipmap（多级纹理）是预计算的纹理金字塔，每级分辨率减半。在渲染时根据屏幕像素覆盖的纹理范围选择合适的 Mipmap 级别，避免远处纹理的锯齿和摩尔纹。三线性过滤（Trilinear Filtering）在相邻两级 Mipmap 之间再做一次线性插值。各向异性过滤（Anisotropic Filtering）在非正方形的纹理采样区域（如倾斜的地面）中沿主方向多次采样，比三线性过滤质量更高。Mipmap 的额外存储开销约为原始纹理的 $1/3$（$\sum_{i=1}^{\infty} (1/4)^i = 1/3$）。

## 关键结论

- Mipmap 解决的是纹理的过采样（minification）问题：当一个屏幕像素覆盖多个纹素时，Mipmap 选择低分辨率级别来平均
- Mipmap 无法很好地处理各向异性情况（一个方向缩小很多，另一个方向不变），各向异性过滤通过沿主方向多次采样解决
- 纹理坐标的不连续性（如 UV 接缝处）会导致法线和光照的不连续，需要在接缝处复制顶点
- 纹理可以存储任意数据：颜色（diffuse map）、法线（normal map）、粗糙度（roughness map）、金属度（metallic map）等
- 纹理采样在 GPU 上有专用硬件（Texture Unit），支持硬件加速的过滤和 Mipmap 选择

## 易错点

1. **Mipmap 级别选择错误**：在手动实现 Mipmap 选择时，$\text{level} = \log_2(\text{像素覆盖的纹理范围})$，忘记取对数会导致选择错误的级别
2. **UV 接缝处的法线断裂**：UV 坐标在接缝处不连续（如球体的经度 $0°$ 和 $360°$ 重合处），如果共享顶点，插值后的法线方向会错误
3. **纹理格式选择不当**：法线贴图应使用 sRGB 格式存储但在线性空间采样，或者使用 BC5 等压缩格式。颜色纹理通常存储在 sRGB 空间，采样时自动转换到线性空间

## 例题

**题目**：一个 $256 \times 256$ 的纹理，屏幕上的一个像素在该纹理上覆盖了一个 $8 \times 8$ 的区域。问：应该采样 Mipmap 的第几级？该级的分辨率是多少？

**解答**：

第一步，计算 Mipmap 级别。屏幕像素覆盖的纹理范围取最大维度：
$$D = \max(8, 8) = 8$$

Mipmap 级别：
$$L = \log_2(D) = \log_2(8) = 3$$

第二步，计算第 3 级 Mipmap 的分辨率：
$$\text{分辨率} = \frac{256}{2^3} = \frac{256}{8} = 32 \times 32$$

该像素应该采样第 3 级 Mipmap，分辨率为 $32 \times 32$。

如果使用三线性过滤，会在第 3 级（$32 \times 32$）和第 4 级（$16 \times 16$）之间插值，插值权重取决于 $L$ 的小数部分。本例中 $L = 3.0$，小数部分为 0，完全使用第 3 级。

## 关联页面

[[光照模型（Lambert/Phong/Blinn-Phong）]] [[法线贴图与凹凸贴图]] [[PBR物理渲染原理]] [[光栅化算法]]
