---
title: "QuadTree与R-Tree"
course: 数据结构
chapter: 空间数据结构
difficulty: ADVANCED
tags: [数据结构, QuadTree, R-Tree, 空间索引, GIS]
aliases: [Quadtree, R-Tree, Spatial Index]
source: "Finkel & Bentley 1974 (Quadtree); Guttman 1984 (R-Tree); Samet《Foundations of Multidimensional Structures》"
updated_at: 2026-05-02
---

## 核心定义

Quadtree(四叉树)将2D空间递归划分为4个象限：NW/NE/SW/SE，直到每一象限中的点数<=1。插入：跟踪象限直到叶子——分裂如果超过容量。范围搜索：检查每个象限是否与查询矩形相交。时间复杂度：插入/删除O(log N)平均(均匀分布)。R-Tree(矩形树)是B树在空间维度上的扩展：每个节点包含一组MBR(Minimum Bounding Rectangle,最小包围矩形)，搜索和插入按面积扩展最小的原则选择合适的子节点分裂。

## 应用与变体

R-tree是多数空间数据库(SpatiaLite/PostGIS的GiST索引)的底层结构。R*-tree通过强制重插入(forced reinsert)改进空间利用率。STR tree(Sort-Tile-Recursive)提供批量加载方案。Quadtree变体：Point Quadtree(分裂部分)、PR Quadtree(基于矩形分裂)、PM Quadtree(多边形地图)。OctTree是四叉树在3D的扩展(每个节点8个子空间)——用于3D游戏引擎的空间分区和点云处理。

## 关键结论

1. R-tree适合存储静态空间数据(建筑/道路)——插入后索引质量在单次加载最好 2. R-tree的删除导致重叠增加需要定期重建 3. 四叉树擅长均匀分布的点数据(城市poi分布) 4. Hilbert R-tree以Hilbert曲线顺序存储——提高空间局部性 5. KD-tree是另一种空间索引——基于k维二分而非象限划分

## 关联知识点

[[数据结构-B树与B+树]] [[数据结构-A*算法与启发式搜索]] [[计算机图形学-空间数据结构与加速]]
