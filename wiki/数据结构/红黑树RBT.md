---
title: "红黑树（Red-Black Tree）"
course: 数据结构
chapter: 高级数据结构
difficulty: ADVANCED
tags: [数据结构, 红黑树, 平衡树, STL, TreeMap]
aliases: [Red-Black Tree]
source: "Introduction to Algorithms (CLRS) 第13章; A Dichromatic Framework for Balanced Trees (Guibas & Sedgewick 1978)"
updated_at: 2026-05-02
---

## 核心定义

红黑树是自平衡二叉搜索树，满足五条性质：1.节点红或黑 2.根为黑 3.叶子(NIL)为黑 4.红节点的子节点必黑（无连续红）5.任一节点到其所有后代叶子的黑高相等。最坏高度≤2log(n+1)，查找/插入/删除均O(log n)。C++ std::map、Java TreeMap、Linux CFS调度器均使用红黑树。

## 关键结论

1. 旋转次数少于AVL（插入最多2次旋转），适合频繁插入删除 2. 红黑树的五条性质保证了近似平衡 3. 左倾红黑树(LLRB)用2-3树类比简化实现 4. Linux CFS用红黑树按vruntime组织进程

## 关联页面

[[平衡二叉树-AVL]] [[二叉搜索树]] [[B+树]]
