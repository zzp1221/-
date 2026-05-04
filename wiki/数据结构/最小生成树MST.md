---
title: "最小生成树（Prim与Kruskal）"
course: 数据结构
chapter: 图论
difficulty: INTERMEDIATE
tags: [数据结构, 最小生成树, Prim, Kruskal, MST]
aliases: [Minimum Spanning Tree]
source: "Introduction to Algorithms (CLRS) 第23章"
updated_at: 2026-05-02
---

## 核心定义

最小生成树是连接图中所有顶点的权值最小的无环子图。Kruskal算法：按边权排序，贪心选取不构成环的边。使用并查集判环，O(E log E)。适合稀疏图。Prim算法：从任意顶点开始，每次选择与当前树相连的最小权边对应的顶点加入。用优先队列O((V+E)log V)。适合稠密图。

## 关键结论

1. 权值都不同时MST唯一 2. Kruskal适用于边少（稀疏图），Prim适用于边多（稠密图）3. MST的割性质和环性质是正确性基础 4. 应用：网络布线、聚类分析、近似TSP

## 关联页面

[[并查集UnionFind]] [[最短路径Dijkstra]] [[图论基础]]
