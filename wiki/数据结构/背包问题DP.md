---
title: "背包问题（0-1背包与完全背包）"
course: 数据结构
chapter: 动态规划
difficulty: INTERMEDIATE
tags: [数据结构, 背包, DP, 动态规划, 组合优化]
aliases: [Knapsack Problem]
source: "Introduction to Algorithms (CLRS); Programming Pearls (Bentley)"
updated_at: 2026-05-02
---

## 核心定义

0-1背包：容量W，n个物品各重w[i]值v[i]，每件选或不选，求最大总价值。dp[i][j]=前i件物品容量j的最大价值=max(dp[i-1][j], dp[i-1][j-w[i]]+v[i])。可压缩为一维dp（j从大到小遍历）。完全背包：每件物品无限取。dp[i][j]=max(dp[i-1][j], dp[i][j-w[i]]+v[i])（一维时j从小到大）。

## 关键结论

1. 0-1背包一维倒序，完全背包一维正序——方向区别是核心 2. 多重背包可用二进制拆分优化为O(nW log m) 3. 分组背包、混合背包、二维费用背包等变体 4. 背包DP的状态定义模式可迁移到许多问题

## 关联页面

[[动态规划]] [[动态规划方法论]]
