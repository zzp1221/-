---
title: 最小生成树-Prim算法
course: 数据结构
chapter: 图
difficulty: INTERMEDIATE
tags: [图, 最小生成树, Prim, 贪心算法, 连通图]
aliases: [Prim Algorithm, Minimum Spanning Tree, MST]
source:
  - Robert C. Prim 论文 (1957)
  - 《算法导论》
updated_at: 2026-05-02
---

## 核心定义

Prim 算法是求解加权连通无向图最小生成树（MST）的经典贪心算法之一。算法思想：从任意一个顶点开始，逐步将顶点纳入生成树集合 U。在每一步中，从连接 U 和 V-U 的所有边中选择一条权值最小的边，将该边及其 V-U 端顶点加入 U。重复直到 U = V（所有顶点都被纳入）。Prim 算法的贪心选择性质是安全的（可通过 cut 理论证明）。朴素实现的时间复杂度为 O(n^2)，适合稠密图。使用优先队列（最小堆）优化后，邻接表表示的 Prim 时间复杂度为 O(e log n)（或 O(e log v)）。

## 关键结论

- Prim 算法与 Dijkstra 算法结构相似，但关键区别在于距离的定义：Prim 是到已选集合的最短距离，Dijkstra 是到起点的最短累加距离
- 朴素实现（无优先队列）O(n^2)，适合稠密图
- 优先队列优化 O(e log n)，适合稀疏图
- 维护 lowcost 数组（或 minDist），表示每个 V-U 顶点到 U 的最小边权
- 当图为非连通时不存在生成树，Prim 会部分终止

## 易错点

1. Prim 与 Dijkstra 的混淆：两者的代码结构高度相似，但更新规则不同。Prim 取 min(lowcost[v], weight(u,v))，Dijkstra 取 min(dist[v], dist[u]+weight(u,v))
2. 负权边的处理：Prim 对负权边没有问题（因为 MST 总是取最小权值边），但需注意与 Dijkstra 的区别——Dijkstra 不能处理负权边
3. 初始顶点的 lowcost 需设为 0（表示已纳入 U）：否则第一轮选择时会出错

## 例题

**例1：** 给定加权无向图，用 Prim 算法从顶点 A 出发求 MST，写出每步选择的边。

**解答：** 选 A 入 U，找 A 的所有邻边中最小者加入；将新顶点的邻边中到 U 距离最小的加入；重复直到 n-1 条边选定。每步都检测所有跨越 U 和 V-U 的边中的最小者。

## 代码示例

```cpp
#include <vector>
#include <queue>
using namespace std;
typedef pair<int,int> pii;  // (距离, 顶点)

vector<int> prim(int n, vector<vector<pii>>& adj) {
    vector<int> parent(n, -1);
    vector<int> key(n, INT_MAX);
    vector<bool> inMST(n, false);
    priority_queue<pii, vector<pii>, greater<pii>> pq;
    
    key[0] = 0;
    pq.push({0, 0});
    
    while (!pq.empty()) {
        int u = pq.top().second;
        pq.pop();
        if (inMST[u]) continue;
        inMST[u] = true;
        
        for (auto& [v, w] : adj[u]) {
            if (!inMST[v] && w < key[v]) {
                parent[v] = u;
                key[v] = w;
                pq.push({w, v});
            }
        }
    }
    return parent;  // parent[i] 表示 i 在 MST 中的父结点
}
```

```java
public class Prim {
    public static int[] prim(int n, List<int[]>[] adj) {
        int[] parent = new int[n];
        int[] key = new int[n];
        boolean[] inMST = new boolean[n];
        Arrays.fill(key, Integer.MAX_VALUE);
        Arrays.fill(parent, -1);
        
        PriorityQueue<int[]> pq = new PriorityQueue<>((a,b) -> a[1]-b[1]);
        key[0] = 0;
        pq.offer(new int[]{0, 0});
        
        while (!pq.isEmpty()) {
            int u = pq.poll()[0];
            if (inMST[u]) continue;
            inMST[u] = true;
            for (int[] edge : adj[u]) {
                int v = edge[0], w = edge[1];
                if (!inMST[v] && w < key[v]) {
                    parent[v] = u;
                    key[v] = w;
                    pq.offer(new int[]{v, w});
                }
            }
        }
        return parent;
    }
}
```

## 关联页面

[[最小生成树-Kruskal]] [[最短路径-Dijkstra]] [[图-BFS]] [[并查集]]
