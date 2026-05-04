---
title: Dijkstra最短路径算法
course: 算法设计与分析
chapter: 第四章 贪心算法
difficulty: INTERMEDIATE
tags: [Dijkstra, 最短路径, 贪心算法, 优先队列, 单源最短路径, 图算法]
aliases: [Dijkstra's Algorithm, 迪杰斯特拉算法, SSSP]
source:
  - Dijkstra, A Note on Two Problems in Connexion with Graphs (1959)
  - Cormen, Introduction to Algorithms (CLRS)
updated_at: 2026-05-02
---

## 核心定义

Dijkstra 算法是由 Edsger W. Dijkstra 于 1959 年提出的求解非负权图中单源最短路径（Single-Source Shortest Paths, SSSP）的贪心算法。给定有向/无向带权图 G=(V,E) 和起点 s，算法计算从 s 到所有其他顶点的最短距离。核心思想是贪心地选择当前未确定最短距离的顶点中距离最小的一个，将其标记为"已确定"并松弛其所有邻接边。算法维护一个优先队列（最小堆），每次从堆中取出距离最小的顶点 u（贪心选择），遍历其邻居 v，若通过 u 到达 v 的路径比当前记录的更短，则更新 dist[v] 并放入堆中。使用二叉堆实现时间复杂度为 O((V+E) log V)。Dijkstra 算法的贪心选择性质依赖于非负权边的假设。

## 关键结论

- 贪心策略：每次选择未处理集合中距离最小的顶点，其当前距离即为最短距离（不可再被改进）
- 时间复杂度：二叉堆 O((V+E) log V)，斐波那契堆 O(E + V log V)，朴素数组 O(V^2)（适合稠密图）
- Dijkstra 不能处理负权边：因为贪心选择性质依赖于"松弛操作不能减小已被确定顶点的距离"，而负权边会破坏此性质
- 有负权边的 SSSP 应使用 Bellman-Ford 算法
- Dijkstra 是许多实际导航系统的基础算法，结合启发式即为 A* 搜索算法

## 易错点

1. 对 Dijkstra 使用负权边：即使最终答案"正确"也是偶然，不能依赖。典型反例：s->a 权 -3, a->t 权 2, s->t 权 2。Dijkstra 从 s 出发将 t 确定为 dist=2，但实际上 s->a->t = -1 更短。
2. 忘记在松弛时同时更新优先队列：标准做法是直接向堆中插入新(dist, v)对而非修改旧值。
3. Dijkstra 需要目标：算法计算 s 到所有点的最短路径，而非仅到 t。可添加提前终止优化。

## 例题

**例题1：** 给定图：A-B:4, A-C:2, B-C:1, B-D:5, C-D:8, C-E:10, D-E:2, D-F:6, E-F:3。以 A 为起点求最短路径。

**解答：** dist[A]=0, 其他 INF。从 A 出发松弛 B(4), C(2)。取出 C(2)，松弛 D(2+8=10), E(2+10=12)。取出 B(4)，松弛 D(min(10,4+5=9)), 且 B-C 为 1 但 C 已确定。取出 D(9)，松弛 E(min(12,9+2=11)), F(9+6=15)。取出 E(11)，松弛 F(min(15,11+3=14))。最终 dist: A=0,B=4,C=2,D=9,E=11,F=14。

**例题2：** 解释为什么 Dijkstra 是贪心算法。

**解答：** 每一步选择距离最小的未处理顶点，相当于"当前看来最优"的局部决策；且一经确定永不修改。需要证明这一贪心选择正确（通过归纳法），这依赖于非负权边的假设。符合"贪心选择性质+最优子结构"的贪心框架。

## 代码示例

```python
import heapq

def dijkstra(graph, start, n):
    """
    graph: 邻接表 [(neighbor, weight), ...]
    返回: dist 数组和 prev 数组（用于路径重构）
    """
    dist = [float('inf')] * n
    dist[start] = 0
    prev = [-1] * n
    visited = [False] * n
    
    heap = [(0, start)]
    
    while heap:
        d, u = heapq.heappop(heap)
        if visited[u]:
            continue
        visited[u] = True
        
        for v, w in graph[u]:
            new_dist = d + w
            if new_dist < dist[v]:
                dist[v] = new_dist
                prev[v] = u
                heapq.heappush(heap, (new_dist, v))
    
    return dist, prev

def reconstruct_path(prev, target):
    """从 prev 数组重构路径"""
    path = []
    while target != -1:
        path.append(target)
        target = prev[target]
    return list(reversed(path))

# 示例
n = 6
graph = [
    [(1,4), (2,2)],           # A(0)
    [(0,4), (2,1), (3,5)],    # B(1)
    [(0,2), (1,1), (3,8), (4,10)],  # C(2)
    [(1,5), (2,8), (4,2), (5,6)],   # D(3)
    [(2,10), (3,2), (5,3)],         # E(4)
    [(3,6), (4,3)]                  # F(5)
]
dist, prev = dijkstra(graph, 0, n)
print("最短距离:", dist)
print("A->F 路径:", reconstruct_path(prev, 5))
```

## 关联页面

[[贪心算法概述]] [[Bellman-Ford算法]] [[Floyd-Warshall算法]] [[最小生成树]] [[A星搜索]]
