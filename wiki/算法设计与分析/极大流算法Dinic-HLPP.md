---
title: "极大流算法(Dinic/HLPP)"
course: 算法设计与分析
chapter: 图算法
difficulty: ADVANCED
tags: [算法, 网络流, Dinic, HLPP, 最大流]
aliases: [Maximum Flow, Dinic's Algorithm, HLPP]
source: "Dinic 1970; Goldberg & Tarjan 1988 (Push-Relabel); CLRS §26; Ahuja, Magnanti & Orlin《Network Flows》"
updated_at: 2026-05-02
---

## 核心定义

网络最大流问题：有向图G=(V,E)，源点s汇点t，每条边有容量c，求从s到t的最大可行流量。Ford-Fulkerson方法(O(E max_flow)，整形容量)不断找增广路径——但可通过反边(back edge)取消之前的流量分配。Edmonds-Karp用BFS寻找最短增广路径保证O(VE^2)复杂度。Dinic算法通过分层图(level graph)在一次BFS后执行多次DFS(blocking flow)推送流量，复杂度O(EV^2)一般图/O(E sqrt(V))单位容量图。

## Push-Relabel/HLPP

Push-Relabel(推进-重标记)颠覆了传统增广路径方法。每个节点有高度(height label)和超额流量(excess flow)。Push操作将溢出流推送到高度低的邻居。Relabel操作提升节点高度使push可能。Highest Label Preflow-Push(HLPP,最高标号先出)选择最高高度的溢出节点处理达到O(V^2 sqrt(E))复杂度。理论优势明显——但常数大。Gap heuristics(间隙启发式)极大加速实际运行。HLPP在并行化上有独特优势(局部push不依赖全局路径)。

## 关键结论

1. Dinic在竞赛编程中广泛应用(易于实现,实践中非常快) 2. Push-Relabel的泛化可做更一般的minimum cost flow 3. 最大流=最小割(Min-Cut Max-Flow Theorem)有深刻的组合意义 4. 动态树(Link-Cut Tree)可加速Dinic到O(VE log V) 5. 当前实际最快的实现一般基于IBFS(incremental BFS)的变体

## 关联知识点

[[算法设计与分析-图算法总览]] [[算法设计与分析-线性规划与单纯形法]] [[数据结构-图的最小生成树]]
