---
title: "NP完全性与归约"
course: 算法设计与分析
chapter: 计算复杂性
difficulty: ADVANCED
tags: [算法, NP, P vs NP, 归约, 计算复杂性]
aliases: [NP-Completeness, P vs NP]
source: "Introduction to Algorithms (CLRS) 第34章"
updated_at: 2026-05-02
---

## 核心定义

P类：可在多项式时间求解的问题。NP类：可在多项式时间验证解的问题。NP-Hard：不弱于任何NP问题(所有NP问题可归约到它)。NP-Complete：既是NP又是NP-Hard。Cook定理：SAT是第一个被证明为NP-Complete的问题。归约：将问题A的实例在多项式时间内转化(不是解决)为问题B的实例，证明B至少和A一样难。经典NPC问题：SAT、3-SAT、团(Clique)、顶点覆盖、哈密顿回路、子集和、旅行商(TSP)。

## 关键结论

1. P⊆NP，P=?NP是计算机科学的未解千禧年问题 2. 证明NPC：先证属于NP，再归约已知NPC到该问题 3. 工程实践：遇到NPC用近似算法、参数化算法或启发式

## 关联页面

[[计算模型与复杂度类]] [[回溯法]] [[分支限界法]]
