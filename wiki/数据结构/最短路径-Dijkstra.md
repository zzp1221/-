---
title: 最短路径-Dijkstra算法
course: 数据结构
chapter: 图
difficulty: INTERMEDIATE
tags: [图, 最短路径, Dijkstra, 贪心算法, 单源最短路径]
aliases: [Dijkstra Algorithm, SSSP, 单源最短路径]
source:
  - Edsger W. Dijkstra 论文 (1959)
  - 《算法导论》
updated_at: 2026-05-02
---

## 核心定义

Dijkstra 算法是求解单源最短路径的经典贪心算法，由荷兰计算机科学家 Edsger W. Dijkstra 于 1959 年提出。算法解决的问题是：在加权有向图（或无向图）中，从一个源点 s 出发，求 s 到所有其他顶点的最短路径长度。算法的前提是所有边的权值非负。其核心思想是：维护一个集合 S（已确定最短路径的顶点集合）和一个距离数组 dist。每次从 V-S 中选出 dist 最小的顶点 u 加入 S，然后用 u 来"松弛"其所有邻接点 v：若 dist[v] > dist[u] + w(u,v)，则更新 dist[v] = dist[u] + w(u,v)。算法保证当顶点加入 S 时其 dist 就是最终的最短距离。朴素实现 O(n^2)，优先队列优化 O(e log n)。

## 关键结论

- 只适用于非负权图——负权会导致已确定最短路径的顶点可能被后续"松弛"推翻
- dist 数组的初始化：dist[s]=0，其他为 INF；每步选最小 dist 的未确定顶点加入已确定集合
- 松弛操作（Relaxation）是核心：if(dist[v] > dist[u] + w) dist[v] = dist[u] + w
- 优先队列优化（二叉堆）：O((V+E) log V)，适合稀疏图
- 不需要 dist 更新的顶点可以跳过（用 visited 标记已确定）

## 易错点

1. 负权边不能用 Dijkstra：即使图中只有一条负权边也不行，因为一旦顶点被标记为"已确定"就永远不变，负权边可能推翻这个结论
2. 优先队列中旧距离值未更新：当 dist[v] 被更新时，不能直接在优先队列中修改；需要插入新的 (新距离, v) 并允许旧记录存在但通过 visited 跳过
3. 无向图的处理：在无向图中每条边需要两个方向都加入邻接表；Dijkstra 在无向图上同样适用

## 例题

**例1：** 为什么 Dijkstra 算法不适用于负权边？给出反例。

**解答：** 考虑顶点 A(源), B, C。边 A-B 权重 5，A-C 权重 6，B-C 权重 -2。Dijkstra 先确定 A->B=5（最小），然后将 B 加入 S，计算 A->C 通过 B = 5+(-2)=3。但此时 C 可能在 B 之前就被"确定"为 6（如果 C 的初始 6 小于某中间值...）。实际上应该等到 B 确定后通过 B 松弛 C 得到真正的 3，但 Dijkstra 可能在 B 被确定前就把 C 以 6 确定为最终值。正确的最短路 A->C 应为 3。

## 代码示例

```cpp
#include <vector>
#include <queue>
using namespace std;
typedef pair<int,int> pii;

vector<int> dijkstra(int n, vector<vector<pii>>& adj, int s) {
    vector<int> dist(n, INT_MAX);
    vector<bool> visited(n, false);
    priority_queue<pii, vector<pii>, greater<pii>> pq;
    
    dist[s] = 0;
    pq.push({0, s});
    
    while (!pq.empty()) {
        int u = pq.top().second; pq.pop();
        if (visited[u]) continue;
        visited[u] = true;
        
        for (auto& [v, w] : adj[u]) {
            if (!visited[v] && dist[u] + w < dist[v]) {
                dist[v] = dist[u] + w;
                pq.push({dist[v], v});
            }
        }
    }
    return dist;
}
```

```java
public int[] dijkstra(int n, List<int[]>[] adj, int s) {
    int[] dist = new int[n];
    boolean[] visited = new boolean[n];
    Arrays.fill(dist, Integer.MAX_VALUE);
    PriorityQueue<int[]> pq = new PriorityQueue<>((a,b) -> a[1]-b[1]);
    dist[s] = 0;
    pq.offer(new int[]{s, 0});
    
    while (!pq.isEmpty()) {
        int u = pq.poll()[0];
        if (visited[u]) continue;
        visited[u] = true;
        for (int[] edge : adj[u]) {
            int v = edge[0], w = edge[1];
            if (!visited[v] && dist[u] + w < dist[v]) {
                dist[v] = dist[u] + w;
                pq.offer(new int[]{v, dist[v]});
            }
        }
    }
    return dist;
}
```

## 关联页面

[[最短路径-Floyd]] [[最短路径-BellmanFord]] [[最小生成树-Prim]] [[图-BFS]]
