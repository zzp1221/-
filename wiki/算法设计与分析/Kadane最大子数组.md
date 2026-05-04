---
title: "最大子数组问题（Kadane算法）"
course: 算法设计与分析
chapter: 动态规划
difficulty: INTERMEDIATE
tags: [算法, 最大子数组, Kadane, DP]
aliases: [Kadane's Algorithm]
source: "Programming Pearls (Bentley) 第8章"
updated_at: 2026-05-02
---

## 核心定义

给定整数数组找和最大的连续子数组。Kadane O(n)：dp[i]=以nums[i]结尾的最大子数组和=max(nums[i], dp[i-1]+nums[i])，答案=max(dp[0..n-1])。空间优化为O(1)：cur_max=max(x, cur_max+x)。扩展：二维矩阵O(n³)降维DP；环形数组取max(普通Kadane, 总和-最小子数组)。

## 关联页面

[[动态规划]] [[动态规划方法论]] [[分治法]]
