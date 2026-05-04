---
title: Bellman-Ford算法
course: 算法设计与分析
chapter: 第六章 图算法
difficulty: INTERMEDIATE
tags: [Bellman-Ford, 最短路径, 负权边, 负环检测, 动态规划, 松弛]
aliases: [Bellman-Ford Algorithm, 贝尔曼-福特算法]
source:
  - Cormen, Introduction to Algorithms (CLRS)
  - Bellman, On a Routing Problem (1958)
  - Ford, Network Flow Theory (1956)
updated_at: 2026-05-02
---

## 核心定义

Bellman-Ford 算法求解单源最短路径问题，最大的特点是能够处理带有负权边的图（Dijkstra 无法处理）。算法基于动态规划思想，核心操作是进行 |V|-1 轮对所有边的松弛（Relaxation）操作。松弛操作的定义：若 dist[u] + w(u,v) < dist[v]，则更新 dist[v]。经过 k 轮松弛后，dist[v] 存储了从源点出发经过不超过 k 条边到达 v 的最短距离。由于任何简单路径最多包含 |V|-1 条边，|V|-1 轮松弛足以找到所有最短路径。完成 |V|-1 轮后，若还能继续松弛（即存在负权环），则可以检测到负权环的存在。时间复杂度 O(VE)，空间复杂度 O(V)。

## 关键结论

- Bellman-Ford 可以处理负权边（Dijkstra 不能），但不能有负权环（负权环使最短距离无下界）
- |V|-1 轮松弛的正确性基于最短路径最多包含 |V|-1 条边的性质（简单路径无环）
- 可在每轮松弛后添加提前终止优化：若某轮无任何 dist 被更新，则算法已收敛可提前结束
- 队列优化版本（Shortest Path Faster Algorithm, SPFA）在稀疏图上效率更高，但最坏仍 O(VE)
- 负环检测是 Bellman-Ford 的重要功能，以此判断套汇、差分约束系统可行性等问题

## 易错点

1. dist 数组初始化为 INF（非 0），源点 dist[s]=0。否则所有值永远为 0。
2. 第 |V| 轮仍松弛则存在负环，但不能定位负环上的具体路径：需要额外的 parent 链追踪。
3. 图中可能不止一个负环，只有一个能通过第 |V| 轮松弛被"触发"。

## 例题

**例题1：** 给定图：S->A:6, S->B:7, A->C:5, A->D:-4, B->A:8, B->C:-3, B->D:9, C->A:-2, D->C:7, D->T:2, C->T:4。求 S 到 T 最短路径。

**解答：** |V|=6，需 5 轮松弛。经过各轮迭代累积最短路径。最终 dist[T] 应是最短距离（具体数值由递推得出）。注意路径可能含负权，需走完整 5 轮。

**例题2：** 检测图是否有负权环：S->A:1, A->B:-1, B->A:-1。从 S 运行 Bellman-Ford。

**解答：** |V|=3。第一轮后 dist[S]=0,dist[A]=1,dist[B]=0。第二轮后 dist[A] 可从 B 松驰为 0-1=-1，dist[A] 更新到 -1。第三轮（第 |V| 轮）仍能松弛 -> 检测到 A-B 之间的负环。

## 代码示例

```python
def bellman_ford(n, edges, source):
    """
    n: 顶点数
    edges: [(u, v, weight), ...]
    """
    dist = [float('inf')] * n
    dist[source] = 0
    prev = [-1] * n  # 用于路径重构和负环检测
    
    # |V|-1 轮松弛
    for i in range(n - 1):
        updated = False
        for u, v, w in edges:
            if dist[u] != float('inf') and dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                prev[v] = u
                updated = True
        if not updated:
            break  # 提前终止优化
    
    # 负环检测：第 |V| 轮
    negative_cycle = False
    for u, v, w in edges:
        if dist[u] != float('inf') and dist[u] + w < dist[v]:
            negative_cycle = True
            break
    
    return dist, prev, negative_cycle

def reconstruct_path(prev, target):
    path = []
    while target != -1:
        path.append(target)
        target = prev[target]
    return list(reversed(path))

# 示例
n = 5
edges = [
    (0,1,6), (0,2,7), (1,2,8), (1,3,5), (1,4,-4),
    (2,3,-3), (2,4,9), (3,1,-2), (4,3,7)
]
dist, prev, has_neg = bellman_ford(n, edges, 0)
print("最短距离:", dist)
print("有负环:", has_neg)
```

## 关联页面

[[Dijkstra算法]] [[Floyd-Warshall算法]] [[最短路径]] [[动态规划概述]] [[SPFA]]
