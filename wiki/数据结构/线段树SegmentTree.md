---
title: "线段树（Segment Tree）"
course: 数据结构
chapter: 高级数据结构
difficulty: ADVANCED
tags: [数据结构, 线段树, 区间查询, RMQ, 懒标记]
aliases: [Segment Tree]
source: "Introduction to Algorithms (CLRS) 第14章; Competitive Programming (Halim)"
updated_at: 2026-05-02
---

## 核心定义

线段树是二叉树结构，每个节点代表一个区间。用于区间查询（和/最小值/最大值/gcd）和区间更新。根节点覆盖[0,n-1]，叶子节点是单个元素。构建O(n)、查询O(log n)、更新O(log n)，空间O(4n)。懒标记(lazy propagation)支持区间更新（将更新推迟到真正需要时下推）。

## 关键结论

1. 相比树状数组，支持更多区间操作（区间查询+更新+自定义合并）2. 动态开点节省空间 3. 持久化线段树支持查询历史版本

## 关联页面

[[树状数组Fenwick]] [[树]] [[二叉树]]
