---
title: "B树与B+树全面对比"
course: 数据结构
chapter: 高级数据结构
difficulty: INTERMEDIATE
tags: [数据结构, B树, B+树, 索引, 数据库, 文件系统]
aliases: [B-Tree, B+Tree]
source: "Introduction to Algorithms (CLRS) 第18章; The Ubiquitous B-Tree (Comer 1979)"
updated_at: 2026-05-02
---

## 核心定义

B树是平衡多路搜索树，每个节点可以有多个键和子节点。m阶B树性质：每个节点最多m-1个键和m个子节点，根至少1个键，非根节点至少⌈m/2⌉-1个键，所有叶子在同一层。B+树变体：所有键值存于叶子节点，内部节点只存索引。叶子节点通过链表连接支持范围查询。

## 关键结论

1. B+树扇出更大（内节点不存数据）→树更矮→IO更少 2. B+树叶子链表天然支持范围查询，B树需要中序遍历 3. B+树是数据库索引的标准结构（MySQL InnoDB、PostgreSQL）4. B树更适合键值直接存于内部节点的场景

## 关联页面

[[B+树存储引擎]] [[红黑树RBT]] [[数据库索引设计]]
