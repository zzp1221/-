---
title: "Disjoint Set Union深度"
course: 数据结构
chapter: 高级数据结构
difficulty: INTERMEDIATE
tags: [数据结构, 并查集, DSU, 路径压缩, 按秩合并]
aliases: [Union-Find, DSU, Path Compression]
source: "Tarjan 1975 (Union-Find); CLRS §21; Sedgewick《Algorithms》Ch 1.5"
updated_at: 2026-05-02
---

## 核心定义

Disjoint Set Union(DSU/并查集/Union-Find)维护不相交集合的集合。核心操作：MakeSet(x)(创建新集合)、Find(x)(找到x所在集合的代表元/根)、Union(x,y)(合并两集合)。基础实现使用parent数组(parent[x]=父节点)。路径压缩(path compression)——Find时将x到根的路径上所有节点直接指向根。按秩合并(union by rank)——总将rank小的树接在rank大的树下(保持树浅)。组合两种优化得到O(alpha(N))的近乎线性的均摊时间。alpha(N)是阿克曼函数的逆——对所有实际N < 5。

## 高级扩展

带权并查集(weighted DSU)在边上存储信息(如食物链中的'x eats y'关系)——Find时沿着路径累积权重。可回滚并查集(rollback DSU)——仅使用按秩合并(不用路径压缩)以支持撤销操作(使用栈记录合并操作)。可持久化并查集(persistent DSU)——用持久化数组实现。在线/离线版本——处理动态连接的连接性查询(加边+查询连通性)。按元素数量(size)合并有时比按秩(height)更常用(效果相近但更简单)。

## 关键结论

1. 实际中只用路径压缩或只用按秩合并都是O(log N)级 2. 按大小合并保证树高不超过logN 3. DSU不能高效处理删边——边删除是困难问题(需用动态树Link-Cut Tree) 4. 离线DSU解决'在一段时间内存在边'的问题(通过扫描时间线) 5. DSU是Kruskal算法和许多图处理算法的基础

## 关联知识点

[[数据结构-图的最小生成树]] [[数据结构-Treap与Splay Tree]] [[算法设计与分析-在线算法与竞争比]]
