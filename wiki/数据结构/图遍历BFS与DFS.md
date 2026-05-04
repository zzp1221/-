---
title: "图遍历（BFS与DFS）"
course: 数据结构
chapter: 图论
difficulty: BASIC
tags: [数据结构, BFS, DFS, 图遍历, 连通分量]
aliases: [Breadth-First Search, Depth-First Search]
source: "Introduction to Algorithms (CLRS) 第22章"
updated_at: 2026-05-02
---

## 核心定义

BFS(广度优先搜索)：使用队列，按距离逐层访问节点，得到最短路径（无权图）。时间复杂度O(V+E)。应用：最短路径、连通分量、二分图检测。DFS(深度优先搜索)：使用栈（递归），沿路径深入直到无法继续再回溯。记录发现时间d[v]和完成时间f[v]。边的分类：树边、回边、前向边、交叉边。

## 关键结论

1. BFS求最短路径（无权图），DFS不适合求最短路径 2. DFS的括号结构(finish time)是拓扑排序和SCC的基础 3. 图太大时用迭代DFS避免栈溢出 4. 双向BFS可显著加速（分支因子减半）

## 关联页面

[[最短路径Dijkstra]] [[拓扑排序]] [[强连通分量]] [[图和图的基本概念]]
