---
title: Johnson全源最短路径算法
course: 算法设计与分析
chapter: 第六章 图算法
difficulty: ADVANCED
tags: [Johnson算法, 全源最短路径, Bellman-Ford, Dijkstra, 重赋权, 势函数]
aliases: [Johnson's Algorithm, APSP, All-Pairs Shortest Paths]
source:
  - Cormen, Introduction to Algorithms (CLRS)
  - Johnson, Efficient Algorithms for Shortest Paths in Sparse Networks (1977)
updated_at: 2026-05-02

---

## 核心定义

Johnson 算法是求解稀疏图上全源最短路径（APSP）的高效算法，由 Donald B. Johnson 于 1977 年提出。在 |E| << |V|^2 的稀疏图上，运行 V 次 Dijkstra 算法的复杂度 O(V (V+E) log V) 优于 Floyd-Warshall 的 O(V^3)，但 Dijkstra 不能处理负权边。Johnson 算法的核心创新在于通过"重赋权"（Reweighting）技术，将图中可能存在负权的边转换为非负权边，同时保持最短路径的偏序关系不变。重赋权方法：引入一个辅助顶点 s 连接到所有原顶点，边权为 0；运行一次 Bellman-Ford 算法（从 s 出发）计算出每个顶点的势函数 h(v) = dist_s(v)；然后定义新的边权 w'(u,v) = w(u,v) + h(u) - h(v)。关键性质是 (1) w' >= 0（由三角不等式保证）；(2) 对任意路径 p，w'(p) = w(p) + h(source) - h(target)，故新旧权重差仅依赖于路径端点与路径内部边无关。重赋权后，对每个源顶点运行 Dijkstra 算法求最短路径，最后将结果减去势函数差还原。总时间复杂度：Bellman-Ford O(VE) + V * Dijkstra O(V log V + E log V) = O(VE + V^2 log V + V E log V) = O(V^2 log V + V E log V) = O(V E log V)（对稀疏图优于 Floyd 的 O(V^3)）。

## 关键结论

- Johnson 算法 = Bellman-Ford（重赋权）+ V 次 Dijkstra（求解），是稀疏图上 APSP 的最优算法
- 重赋权基于势函数（Potential Function）：h(v) = 从超级源点 s 到 v 的最短距离
- w'(u,v) = w(u,v) + h(u) - h(v) >= 0 的保证源于不等式 h(v) <= h(u) + w(u,v)（最短路径的三角不等式）
- 原最短路径与重赋权后最短路径的偏移为常数：w'(p) = w(p) + h(u_source) - h(v_target)
- 若图中存在负权环，Bellman-Ford 在预处理阶段即可检测并报告

## 易错点

1. 重赋权公式的符号：w'(u,v) = w(u,v) + h(u) - h(v)，注意 h(u) 加、h(v) 减。若写反会导致负权边不消失。
2. 超级源点 s 必须能到达所有顶点（添加的边权为 0），否则某些顶点的 h(v) = INF，重赋权失败。
3. Dijkstra 使用优先队列而非朴素数组：在稀疏图 (E ~ V) 时 O(log V) 因子不大，但在稠密图中 O(VE log V) ≈ O(V^3 log V) 反而不如 Floyd 的 O(V^3)。

## 例题

**例题1：** 图含 4 个顶点和边：A->B:-2, B->C:3, C->A:1, A->D:4, D->C:2。使用 Johnson 算法求全源最短路径。

**解答：** 添加超级源 S->A,B,C,D 权 0。Bellman-Ford 求 h: h(A)=0, h(B)=-2, h(C)=1, h(D)=4。重赋权：w'(A->B)=-2+0-(-2)=0；w'(B->C)=3+(-2)-1=0；w'(C->A)=1+1-0=2；w'(A->D)=4+0-4=0；w'(D->C)=2+4-1=5。所有权非负。对每个源顶点 Dijkstra 后还原可得最终 APSP。

**例题2：** 证明 w'(u,v) >= 0（即 h(v) <= h(u) + w(u,v)）。

**解答：** h(v) 是从 s 到 v 的最短路径距离。从 s 到 v 的某条路径可以经过 (s->...->u) 然后 (u->v)，其长度为 h(u) + w(u,v)。由于 h(v) 是 s 到 v 的最短路，必然有 h(v) <= h(u) + w(u,v)。移项即 w(u,v) + h(u) - h(v) >= 0，故 w'(u,v) >= 0。

## 代码示例

```python
import heapq

def johnson(n, edges):
    """
    n: 顶点数
    edges: [(u, v, w), ...]
    返回 dist[i][j] (INF表示不可达) 或 None (存在负权环)
    """
    # 添加超级源点 s = n
    aug_edges = edges + [(n, i, 0) for i in range(n)]
    
    # 1. Bellman-Ford 计算 h 值并检测负权环
    h = [float('inf')] * (n + 1)
    h[n] = 0
    for _ in range(n):  # |V|-1 轮 = n 轮 (因为加了超级源点)
        updated = False
        for u, v, w in aug_edges:
            if h[u] != float('inf') and h[u] + w < h[v]:
                h[v] = h[u] + w
                updated = True
        if not updated:
            break
    else:
        # 检查负环
        for u, v, w in aug_edges:
            if h[u] != float('inf') and h[u] + w < h[v]:
                return None  # 负权环
    
    h = h[:n]  # 去掉超级源点
    
    # 2. 重赋权后的图
    graph = [[] for _ in range(n)]
    for u, v, w in edges:
        graph[u].append((v, w + h[u] - h[v]))
    
    # 3. 对每个顶点运行 Dijkstra
    dist = [[float('inf')] * n for _ in range(n)]
    for s in range(n):
        d = [float('inf')] * n
        d[s] = 0
        heap = [(0, s)]
        while heap:
            du, u = heapq.heappop(heap)
            if du > d[u]:
                continue
            for v, w in graph[u]:
                nd = du + w
                if nd < d[v]:
                    d[v] = nd
                    heapq.heappush(heap, (nd, v))
        # 还原真实距离
        for t in range(n):
            if d[t] != float('inf'):
                dist[s][t] = d[t] - h[s] + h[t]
    return dist

# 示例
n = 4
edges = [(0,1,-2), (1,2,3), (2,0,1), (0,3,4), (3,2,2)]
dist = johnson(n, edges)
for row in dist:
    print([int(x) if x != float('inf') else 'INF' for x in row])
```

## 关联页面

[[Dijkstra算法]] [[Bellman-Ford算法]] [[Floyd-Warshall算法]] [[最短路径]] [[稀疏图]]
