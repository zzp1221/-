---
title: "AVL树旋转操作详解"
course: 数据结构
chapter: 高级数据结构
difficulty: INTERMEDIATE
tags: [数据结构, AVL, 平衡二叉树, 旋转, 平衡因子]
aliases: [AVL Tree]
source: "An Algorithm for the Organization of Information (Adelson-Velsky & Landis 1962)"
updated_at: 2026-05-02
---

## 核心定义

AVL树是最早的自平衡BST，定义平衡因子BF=左子树高-右子树高，|BF|≤1。四种旋转：LL(右单旋)：左子树的左子树插入导致不平衡。RR(左单旋)：右子树的右子树插入导致不平衡。LR(先左后右)：左子树的右子树插入导致不平衡。RL(先右后左)：右子树的左子树插入导致不平衡。

## 关键结论

1. 插入最多2次旋转（LR/RL需两次），删除可能需要O(log n)次旋转 2. AVL比红黑树更严格平衡→查找更快但插入删除旋转更多 3. 适合查找远多于插入删除的场景 4. 实际工程中红黑树更常见

## 关联页面

[[红黑树RBT]] [[二叉搜索树]] [[2-3树与B树]]
