---
title: "强连通分量与Kosaraju算法"
course: 数据结构
chapter: 图论
difficulty: ADVANCED
tags: [数据结构, SCC, 强连通分量, Kosaraju, Tarjan]
aliases: [Strongly Connected Component]
source: "Introduction to Algorithms (CLRS) 第22章"
updated_at: 2026-05-02
---

## 核心定义

强连通分量是有向图中的极大子图，其中任意两顶点互相可达。Kosaraju算法O(V+E)：1.对原图做DFS，按完成时间入栈 2.反转所有边(转置图) 3.按出栈顺序在转置图上做DFS，每棵DFS树为一个SCC。Tarjan算法一次DFS即可，用dfn和low数组判断SCC根。应用：2-SAT、社交网络群体发现。

## 关键结论

1. SCC的逆拓扑序构成一个DAG（凝聚图）2. Kosaraju两遍DFS简洁易懂，Tarjan一遍DFS更高效 3. 有向图至少有一个源SCC和一个汇SCC 4. 2-SAT问题可线性求解归约为SCC

## 关联页面

[[图遍历BFS与DFS]] [[拓扑排序]] [[图论基础]]
