---
title: Floyd-Warshall算法
course: 算法设计与分析
chapter: 第六章 图算法
difficulty: INTERMEDIATE
tags: [Floyd-Warshall, 全源最短路径, 动态规划, 传递闭包, 负权边]
aliases: [Floyd-Warshall Algorithm, 弗洛伊德算法, APSP, All-Pairs Shortest Paths]
source:
  - Cormen, Introduction to Algorithms (CLRS)
  - Floyd, Algorithm 97: Shortest Path (1962)
  - Warshall, A Theorem on Boolean Matrices (1962)
updated_at: 2026-05-02
---

## 核心定义

Floyd-Warshall 算法求解全源最短路径（All-Pairs Shortest Paths, APSP）问题，即计算图中任意两个顶点之间的最短距离。算法基于动态规划，核心递推公式为：d[i][j]^(k) = min(d[i][j]^(k-1), d[i][k]^(k-1) + d[k][j]^(k-1))，其中 d[i][j]^(k) 表示从 i 到 j 且中间顶点仅取自 {1,2,...,k} 的最短路径。通过三重循环逐步扩大允许经过的中间顶点范围，最终 d[i][j]^(n) 即为 i 到 j 的真正最短路径。算法时间复杂度为 O(V^3)，空间复杂度 O(V^2)（可使用原地更新）。Floyd-Warshall 能够正确处理负权边（但不能有负权环），是处理稠密图上全源最短路径的标准算法。

## 关键结论

- Floyd-Warshall 的核心递推：d[i][j] = min(d[i][j], d[i][k] + d[k][j])
- 可以处理负权边：因为每轮 k 考虑的新路径允许经过顶点 k，发现更短路径时更新
- 不可有负权环：负权环使最短距离无下界，算法结束后可通过检查对角线 d[i][i] < 0 来检测负权环
- 传递闭包（Transitive Closure）是 Floyd 变体：将 min/+ 替换为 或/与 操作，计算可达性
- 在稀疏图（E << V^2）上，运行 V 次 Dijkstra 或 Johnson 算法比 Floyd-Warshall 更优

## 易错点

1. 三重循环的顺序必须为 k -> i -> j（k 在最外层），否则递推逻辑错误。若 k 在里层会导致部分中间节点未被充分利用。
2. 初值设置：d[i][i]=0, d[i][j]=w(i,j)（有边时）或 INF（无边时）。忘记设对角线为 0 会导致错误结果。
3. 无穷大溢出：d[i][k] + d[k][j] 若其中一项为 INF 会导致算术溢出，需先判断 INF。

## 例题

**例题1：** 用 Floyd 计算 4 顶点图全源最短路径，边集 (1,2,3), (1,3,8), (2,4,1), (3,2,4), (3,4,1)。

**解答：** d0: 对角线 0，INF 表无边。d1 (k=1)：经过顶点 1 的中转，无更新。d2 (k=2)：d[1][4]=min(d[1][4],d[1][2]+d[2][4])=min(INF,3+1)=4。d3 (k=3)：更新多条路径。最终全源最短路径矩阵。

**例题2：** 使用 Floyd 检测负权环。

**解答：** 算法执行完成后检查对角线元素 d[i][i]。正常情况下 d[i][i]=0（到自己的距离为 0）。若存在负权环经过顶点 i，经过 Floyd 递推后 d[i][i] < 0。例如 d[1][2]=-3, d[2][1]=-2 构成负环，经过 k 循环后 d[1][1] 变为 -5。

## 代码示例

```python
def floyd_warshall(n, edges):
    """
    n: 顶点数 (0-indexed)
    edges: [(u, v, weight), ...]
    """
    INF = float('inf')
    dist = [[INF] * n for _ in range(n)]
    
    # 初始化
    for i in range(n):
        dist[i][i] = 0
    for u, v, w in edges:
        dist[u][v] = min(dist[u][v], w)  # 处理重边取最小
    
    # Floyd-Warshall 核心
    for k in range(n):
        for i in range(n):
            if dist[i][k] == INF:
                continue
            for j in range(n):
                if dist[k][j] == INF:
                    continue
                if dist[i][k] + dist[k][j] < dist[i][j]:
                    dist[i][j] = dist[i][k] + dist[k][j]
    
    # 负环检测
    has_negative_cycle = any(dist[i][i] < 0 for i in range(n))
    
    return dist, has_negative_cycle

def transitive_closure(n, edges):
    """传递闭包：判断每对顶点是否可达"""
    reach = [[False] * n for _ in range(n)]
    for i in range(n):
        reach[i][i] = True
    for u, v in edges:
        reach[u][v] = True
    
    for k in range(n):
        for i in range(n):
            for j in range(n):
                reach[i][j] = reach[i][j] or (reach[i][k] and reach[k][j])
    
    return reach

# 示例
n = 4
edges = [(0,1,3), (0,2,8), (1,3,1), (2,1,4), (2,3,1)]
dist, has_neg = floyd_warshall(n, edges)
for row in dist:
    print([int(x) if x != float('inf') else 'INF' for x in row])
```

## 关联页面

[[Dijkstra算法]] [[Bellman-Ford算法]] [[Johnson算法]] [[动态规划概述]] [[传递闭包]]
