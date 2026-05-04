---
title: 加速结构（BVH/KD-Tree）
course: 计算机图形学
chapter: 光线追踪
difficulty: INTERMEDIATE
tags: [BVH, KD-Tree, 加速结构, 空间划分, 层次包围盒]
aliases: [Bounding Volume Hierarchy, KD-Tree, Spatial Acceleration Structure]
source:
  - Fundamentals of Computer Graphics (Marschner & Shirley) Chapter 12
  - GAMES101 课程 Lecture 14-15
  - Physically Based Rendering (PBRT) Chapter 4
updated_at: 2026-05-03
---

## 核心定义

加速结构（Acceleration Structure）是光线追踪中用于快速排除大量不需要求交的物体的数据结构。没有加速结构时，每条光线需要与所有物体求交，复杂度为 $O(N)$。使用加速结构后可以降低到 $O(\log N)$。两种主要的加速结构是 BVH（Bounding Volume Hierarchy，层次包围盒）和 KD-Tree（K-Dimensional Tree，k 维树）。

BVH 将物体组织为树状层次结构：每个节点存储一个包围盒（通常是轴对齐包围盒 AABB），叶节点包含少量物体（如 1-4 个三角形）。构建 BVH 时，递归地将物体集合分为两个子集，选择分裂轴和分裂位置。常用的分裂策略：沿最长轴分裂（Longest Axis）、SAH（Surface Area Heuristic，表面积启发式，选择使代价最小的分裂位置）。SAH 的代价函数为 $C = C_t + P_L \cdot N_L \cdot C_i + P_R \cdot N_R \cdot C_i$，其中 $C_t$ 是遍历代价，$P_L, P_R$ 是子节点包围盒的表面积比例，$N_L, N_R$ 是子节点的物体数，$C_i$ 是求交代价。KD-Tree 是空间划分结构：每次将空间沿某个坐标轴一分为二，物体可能跨越分裂平面（此时物体被裁剪到两侧）。KD-Tree 的遍历通常使用栈或递归，维护"近"子节点和"远"子节点的访问顺序。

## 关键结论

- BVH 是物体划分（每个物体只属于一个节点），KD-Tree 是空间划分（物体可能被裁剪到多个节点）。BVH 的包围盒可能重叠，KD-Tree 的空间单元不重叠
- SAH 是 BVH 构建的最优策略，比简单的中点分裂或等分分裂质量更高，但构建时间更长
- BVH 遍历时先检查近子节点，如果命中且交点在远子节点的包围盒内，才遍历远子节点。这利用了光线追踪的空间局部性
- 现代 GPU 光线追踪（如 RTX）使用硬件加速的 BVH 遍历，支持动态场景的 BVH 更新
- KD-Tree 在静态场景中通常比 BVH 更快（更紧凑的空间划分），但构建时间更长且不支持物体裁剪以外的动态更新

## 易错点

1. **BVH 的不平衡问题**：如果分裂策略不当（如总是沿同一轴分裂），BVH 可能严重不平衡，导致遍历效率下降。SAH 可以缓解这个问题
2. **KD-Tree 的物体裁剪误差**：跨越分裂平面的物体被裁剪后，裁剪边界可能引入额外的交点。需要使用保守裁剪或标记裁剪边界
3. **包围盒求交的早期退出**：光线-AABB 求交需要计算与三个轴的 slab 交集，如果某个轴的区间为空则可以提前退出，避免不必要的计算

## 例题

**题目**：一个 BVH 的根节点包围盒表面积为 100，左子节点表面积为 40（包含 10 个三角形），右子节点表面积为 60（包含 20 个三角形）。SAH 代价参数 $C_t = 1$，$C_i = 1$。计算此分裂的 SAH 代价。

**解答**：

第一步，计算子节点的表面积概率：
$$P_L = \frac{S_L}{S_{parent}} = \frac{40}{100} = 0.4$$
$$P_R = \frac{S_R}{S_{parent}} = \frac{60}{100} = 0.6$$

第二步，计算 SAH 代价：
$$C = C_t + P_L \cdot N_L \cdot C_i + P_R \cdot N_R \cdot C_i$$
$$= 1 + 0.4 \times 10 \times 1 + 0.6 \times 20 \times 1$$
$$= 1 + 4 + 12 = 17$$

SAH 代价为 17。如果物体平均分配（各 15 个）且表面积也平均（各 50），代价为 $1 + 0.5 \times 15 + 0.5 \times 15 = 16$。当前分裂的代价略高，可以尝试其他分裂策略。

## 关联页面

[[光线追踪原理]] [[全局光照与路径追踪]] [[实时光线追踪（DXR/RTX）]] [[多边形网格与半边结构]]
