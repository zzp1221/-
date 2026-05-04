---
title: "树状数组（Fenwick Tree）"
course: 数据结构
chapter: 高级数据结构
difficulty: INTERMEDIATE
tags: [数据结构, 树状数组, Fenwick, BIT, 前缀和]
aliases: [Binary Indexed Tree, Fenwick Tree]
source: "A New Data Structure for Cumulative Frequency Tables (Fenwick 1994); Competitive Programming"
updated_at: 2026-05-02
---

## 核心定义

树状数组（BIT）用数组模拟树结构，支持前缀和查询和单点更新O(log n)，空间O(n)。核心操作：lowbit(x)=x&-x（取二进制最低位的1）。更新：从i开始，每次i+=lowbit(i)。查询：从i开始，每次i-=lowbit(i)。比线段树代码量少且常数小，但功能更受限。

## 关键结论

1. 不支持区间更新（除非用差分数组技巧）2. 轻松扩展到二维(RMQ) 3. lowbit是理解BIT的核心 4. 适用：动态前缀和、求逆序对、二维偏序

## 关联页面

[[线段树SegmentTree]] [[前缀和]] [[逆序对问题]]
