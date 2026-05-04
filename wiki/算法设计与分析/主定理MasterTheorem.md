---
title: "主定理（Master Theorem）"
course: 算法设计与分析
chapter: 算法分析
difficulty: ADVANCED
tags: [算法, 主定理, 复杂度分析, 递归]
aliases: [Master Theorem]
source: "Introduction to Algorithms (CLRS) 第4章"
updated_at: 2026-05-02
---

## 核心定义

主定理求解T(n)=aT(n/b)+f(n)递归式复杂度(a≥1,b>1)。比较f(n)和n^log_b(a)的增长：情况1(叶子主导)：f(n)=O(n^(log_b(a)-ε))→T(n)=Θ(n^log_b(a))。情况2(均衡)：f(n)=Θ(n^log_b(a)·log^k n)→T(n)=Θ(n^log_b(a)·log^(k+1)n)。情况3(根主导)：f(n)=Ω(n^(log_b(a)+ε))+正则条件→T(n)=Θ(f(n))。

## 关键结论

1. log_b(a)>c→情况1，=c→情况2，<c→情况3 2. T(n)=2T(n/2)+n log n属于情况2：T(n)=Θ(n log² n) 3. T(n)=2T(n/2)+n/log n不适用（差值不是多项式级）

## 关联页面

[[渐进记号与大O记号]] [[递归]] [[分治法]]
