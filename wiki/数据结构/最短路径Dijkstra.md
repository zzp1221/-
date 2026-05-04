---
title: "最短路径算法（Dijkstra）"
course: 数据结构
chapter: 图论
difficulty: INTERMEDIATE
tags: [数据结构, Dijkstra, 最短路径, 贪心, 优先队列]
aliases: [Dijkstra's Algorithm]
source: "A Note on Two Problems in Connection with Graphs (Dijkstra 1959); Introduction to Algorithms (CLRS) 第24章"
updated_at: 2026-05-02
---

## 核心定义

Dijkstra算法解决非负权图的单源最短路径问题。贪心策略：每次从未确定最短距离的顶点中选择距离最小的，松弛其所有邻边。朴素实现O(V²)，二叉堆优化O((V+E)log V)，斐波那契堆优化O(E+V log V)。不能处理负权边（负权边需要用Bellman-Ford）。

## 关键结论

1. Dijkstra的关键是不存在负权边（贪心选择性质成立）2. 稠密图(E≈V²)用朴素数组，稀疏图用堆 3. 扩展：双向Dijkstra加速点对点查询 4. A*算法是Dijkstra的启发式推广

## 关联页面

[[最小生成树]] [[拓扑排序]] [[图遍历BFS与DFS]]
