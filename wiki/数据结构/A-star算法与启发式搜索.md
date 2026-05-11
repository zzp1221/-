---
title: "A*算法与启发式搜索"
course: 数据结构
chapter: 图算法
difficulty: INTERMEDIATE
tags: [数据结构, A*, 启发式, 寻路, 最短路径]
aliases: [A* Search, Heuristic Search, Pathfinding]
source: "Hart, Nilsson & Raphael 1968 (A*); Russell & Norvig《AI: Modern Approach》Ch 3; Amit Patel的A* Introduction"
updated_at: 2026-05-02
---

## 核心定义

A*搜索是最优优先最佳优先搜索算法的代表。评价函数f(n)=g(n)+h(n)：g(n)是从起点到n的实际代价，h(n)是从n到目标的启发式估计代价(heuristic)。使用优先队列(最小二叉堆)不断扩展f最小的节点。可接受性(admissibility)：h(n)不高估实际代价时A*找到最优解(h应乐观)。一致性/单调性(consistency)：满足三角不等式h(n)<=cost(n,n')+h(n')。一致性保证图搜索不需要重打开已关闭的节点。

## 启发函数设计

常见启发式：网格寻路——曼哈顿距离、对角线距离、欧几里得距离。欧几里得距离可接受但不一致(计算浮点误差可丢失一致性)。有效分支因子(b*)衡量启发式的质量——b*越接近1越好。打破路径平局(tie-breaking)：给h略微增加(仍保持可接受)——使搜索偏向目标方向减少探索节点。Jump Point Search(JPS)通过对称消除和强制neighbors剪枝在均匀网格上极大加速A*(不扩展无关节点)。

## 关键结论

1. 启发式越好(h更精确)搜索节点越少 2. A*的空间复杂度O(b^d)是主要瓶颈——IDA*(迭代加深A*)缓解 3. A*在游戏寻路、拼图求解、DNA序列对齐等领域有广泛应用 4. 具有monotone heuristic的A*等价于在re-weighted图上的Dijkstra 5. epsilon-A*通过放松最优性显著减少搜索时间

## 关联知识点

[[数据结构-最短路径算法Dijkstra/Bellman-Ford]] [[算法设计与分析-动态规划]] [[人工智能-搜索算法]]
