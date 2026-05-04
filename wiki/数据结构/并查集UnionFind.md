---
title: "并查集（Disjoint Set Union）"
course: 数据结构
chapter: 高级数据结构
difficulty: INTERMEDIATE
tags: [数据结构, 并查集, DSU, 路径压缩, 按秩合并]
aliases: [Union-Find, Disjoint Set Union]
source: "Efficiency of a Good But Not Linear Set Union Algorithm (Tarjan 1975); Introduction to Algorithms (CLRS) 第21章"
updated_at: 2026-05-02
---

## 核心定义

并查集维护不相交集合，支持Union(合并)和Find(查找所属集合)操作。优化：路径压缩（Find时将查找路径上所有节点直接挂到根下）和按秩合并（Union时将矮树挂到高树下）。两者同时使用时均摊时间复杂度O(α(n))，其中α是反阿克曼函数（实际<5）。

## 关键结论

1. α(n)在可观测宇宙范围内≤4，近乎O(1) 2. 只有路径压缩或只有按秩合并是O(log n) 3. 应用：Kruskal MST、连通分量、等价关系

## 代码示例

```python
class DSU:
    def __init__(self, n):
        self.p = list(range(n))
        self.r = [0] * n
    def find(self, x):
        if self.p[x] != x:
            self.p[x] = self.find(self.p[x])
        return self.p[x]
    def union(self, x, y):
        x, y = self.find(x), self.find(y)
        if x == y: return
        if self.r[x] < self.r[y]: x, y = y, x
        self.p[y] = x
        if self.r[x] == self.r[y]: self.r[x] += 1
```

## 关联页面

[[最小生成树]] [[连通分量]] [[图论基础]]
