---
title: 最短路径-Bellman-Ford算法
course: 数据结构
chapter: 图
difficulty: ADVANCED
tags: [图, 最短路径, Bellman-Ford, 负权边, 负权环, 松弛操作]
aliases: [Bellman-Ford Algorithm, BellmanFord, 负权SP]
source:
  - Richard Bellman (1958); Lester Ford (1956)
  - 《算法导论》
updated_at: 2026-05-02

---

## 核心定义

Bellman-Ford 算法是求解单源最短路径的算法，与 Dijkstra 的最大区别在于它可以处理含有负权边的图（但不能有负权环）。算法的核心思想是基于动态规划：最短路径最多包含 n-1 条边（n 为顶点数），因此对所有边进行 n-1 轮松弛操作即可得到最终结果。每轮松弛遍历所有边 e=(u,v,w)，尝试用 dist[u] + w 更新 dist[v]。第 k 轮松弛后 dist[v] 等于从源点出发经过最多 k 条边到达 v 的最短距离。若 n-1 轮后仍有边可以松弛（即还能找到更短路径），则说明图中存在负权环。时间复杂度 O(n * e)，其中 e 为边数。

## 关键结论

- 可以处理负权边，但不能处理负权环（保证最短路有界）
- 时间复杂度 O(VE)，比 Dijkstra 的 O((V+E)log V) 高
- 算法进行 V-1 轮松弛，每轮遍历所有边
- 可用队列优化为 SPFA（Shortest Path Faster Algorithm），平均 O(E)，最坏仍是 O(VE)
- 第 V 轮松弛若仍能更新则说明存在负权环

## 易错点

1. 松弛的轮数必须是 n-1 而非 n：因为最短路最多包含 n-1 条边（无环），第 n 轮如果有更新则表明存在负环
2. 检测负权环的时机：必须在 n-1 轮全做完后再额外做一轮；不能在第 k 轮中有更新就断定有负环
3. SPFA 队列中的节点可能重复入队：需要维护 inQueue[] 标志来防止重复（或维护入队次数判断负环）

## 例题

**例1：** 在一个有 6 个顶点、9 条边的图中，Bellman-Ford 共需执行多少轮松弛？

**解答：** n-1 = 5 轮。每轮对所有 9 条边做松弛尝试。

## 代码示例

```cpp
#include <vector>
using namespace std;

struct Edge { int u, v, w; };

bool bellmanFord(int n, vector<Edge>& edges, int s, vector<int>& dist) {
    dist.assign(n, INT_MAX);
    dist[s] = 0;
    
    // 进行 n-1 轮松弛
    for (int i = 0; i < n - 1; i++) {
        bool updated = false;
        for (Edge& e : edges) {
            if (dist[e.u] != INT_MAX && dist[e.u] + e.w < dist[e.v]) {
                dist[e.v] = dist[e.u] + e.w;
                updated = true;
            }
        }
        if (!updated) break;  // 早停优化
    }
    
    // 第 n 轮检测负权环
    for (Edge& e : edges) {
        if (dist[e.u] != INT_MAX && dist[e.u] + e.w < dist[e.v])
            return false;  // 存在负权环
    }
    return true;
}

// SPFA 版本
bool spfa(int n, vector<vector<pair<int,int>>>& adj, int s, vector<int>& dist) {
    dist.assign(n, INT_MAX);
    dist[s] = 0;
    vector<bool> inQueue(n, false);
    vector<int> cnt(n, 0);  // 入队次数，检测负环
    queue<int> q;
    q.push(s); inQueue[s] = true;
    
    while (!q.empty()) {
        int u = q.front(); q.pop();
        inQueue[u] = false;
        for (auto& [v, w] : adj[u]) {
            if (dist[u] + w < dist[v]) {
                dist[v] = dist[u] + w;
                if (!inQueue[v]) {
                    q.push(v);
                    inQueue[v] = true;
                    if (++cnt[v] > n) return false;  // 负环
                }
            }
        }
    }
    return true;
}
```

## 关联页面

[[最短路径-Dijkstra]] [[最短路径-Floyd]] [[图-DFS]]
