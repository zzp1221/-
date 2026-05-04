---
title: "A*启发式搜索算法"
course: 算法设计与分析
chapter: 搜索算法
difficulty: ADVANCED
tags: [算法, A*, 启发式搜索, 路径规划]
aliases: [A* Search]
source: "A Formal Basis for the Heuristic Determination of Minimum Cost Paths (Hart, Nilsson & Raphael 1968)"
updated_at: 2026-05-02
---

## 核心定义

A*是Dijkstra和贪心最佳优先搜索的结合。代价函数f(n)=g(n)+h(n)：g(n)为起点到n的实际代价，h(n)为n到目标的启发式估计。若h(n)≤真实代价则保证最优（admissible），若h(n)≤h*(n)且满足三角不等式则一致性(consistent)→每个节点最多入队一次。常见启发式：网格地图的曼哈顿距离(四方向)/欧氏距离(八方向)/切比雪夫距离。

## 关键结论

1. h(n)=0时A*退化为Dijkstra 2. h(n)越紧(不影响可采纳性)搜索越快 3. 加权A*(Weighted A*)牺牲最优性换取速度 4. 应用：游戏AI寻路、机器人路径规划、拼图求解

## 关联页面

[[最短路径Dijkstra]] [[图遍历BFS与DFS]]
