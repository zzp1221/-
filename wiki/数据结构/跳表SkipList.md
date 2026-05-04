---
title: "跳表（Skip List）"
course: 数据结构
chapter: 高级数据结构
difficulty: ADVANCED
tags: [数据结构, 跳表, 概率数据结构, Redis]
aliases: [Skip List]
source: "Skip Lists: A Probabilistic Alternative to Balanced Trees (Pugh 1990); Redis ZSet实现"
updated_at: 2026-05-02
---

## 核心定义

跳表是概率平衡的链表扩展，通过多层索引实现O(log n)查找。Redis ZSet用跳表实现。每层是有序链表，每个节点以概率p=0.5随机决定是否出现在上一层。期望高度log_2(n)，查找/插入/删除O(log n)，空间O(n)(期望2n)。

## 关键结论

1. 相比平衡树：实现简单、支持范围查询、并发控制更容易 2. Redis ZSet=跳表(范围查询)+哈希表(O(1)成员查找) 3. 插入时random_level决定新节点层数

## 关联页面

[[平衡二叉树-AVL]] [[B+树]] [[Redis数据结构]]
