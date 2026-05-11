---
title: "Treap与Splay Tree"
course: 数据结构
chapter: 高级数据结构
difficulty: ADVANCED
tags: [数据结构, Treap, Splay Tree, 平衡树, 随机化]
aliases: [Treap, Splay Tree]
source: "Aragon & Seidel 1989 (Treap); Sleator & Tarjan 1985 (Splay Tree); CP3 (Halim) Ch 8"
updated_at: 2026-05-02
---

## 核心定义

Treap(Tree+Heap)是二叉搜索树(BST)与堆的结合：每个节点有两个键——BST键(满足搜索树性质)和随机优先级(满足max-heap性质)。Treap通过旋转维护堆性质，期望高度O(log n)，插入/删除/查找均为O(log n)期望时间。Splay Tree是自调整(self-adjusting)二叉搜索树——每次访问(查找、插入、删除)后将访问节点splay旋转到根。splay操作依赖zig、zig-zig和zig-zag三种旋转模式的组合。

## 分摊分析

Splay Tree没有显式的平衡条件——通过splay操作隐式改善结构。分摊时间O(log n)通过势能方法(potential method)证明：势能定义为各节点size=log(子树大小)之和。splay使访问频率高的节点更接近根——实现工作集性质(working set property)和静态最优性(static optimality)。Treap的随机性保证了期望高度O(log n)——不需rebalancing操作。Treap支持快速的split(按key)/merge(合并两棵树——要求最大key<最小key)。

## 关键结论

1. Treap是最容易实现的平衡树结构(无complex rotation逻辑) 2. Splay的摊销O(log n)不保证每个操作都是O(log n) 3. Splay Tree不适合实时系统(单个操作可能退化O(n)) 4. Treap可用来实现可持久化BST(因旋转是局部的) 5. Implicit Treap用树位置显式建立数组——支持split/merge的数组实现

## 关联知识点

[[数据结构-平衡二叉搜索树AVL与红黑树]] [[数据结构-Disjoint Set Union深度]] [[算法设计与分析-摊销分析]]
