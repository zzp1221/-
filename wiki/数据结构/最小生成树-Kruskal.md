---
title: 最小生成树-Kruskal算法
course: 数据结构
chapter: 图
difficulty: INTERMEDIATE
tags: [图, 最小生成树, Kruskal, 贪心算法, 并查集, 边排序]
aliases: [Kruskal Algorithm, MST-Kruskal]
source:
  - Joseph Kruskal 论文 (1956)
  - 《算法导论》
updated_at: 2026-05-02
---

## 核心定义

Kruskal 算法是求解最小生成树（MST）的另一经典贪心算法。算法思想：将所有边按权值从小到大排序，初始时每个顶点自成一个连通分量；依次考虑每条边，若该边连接的是两个不同的连通分量（即不会形成环），则选择该边并将两个分量合并；否则跳过该边。重复直到选够 n-1 条边（n 为顶点数）。判断是否形成环使用并查集（Union-Find）数据结构。算法的时间复杂度主要取决于排序：O(e log e)，加上并查集操作 O(e * alpha(v))，总体 O(e log e)，适合稀疏图。与 Prim 相比，Kruskal 可以直接在边集上操作，不需要维护顶点集合的距离信息。

## 关键结论

- Kruskal 直接对边排序并贪心选取，借助并查集判断连接性
- 时间复杂度 O(e log e)（排序主导），适合稀疏图（e 较小）
- 核心操作：对所有边按权重排序 -> 依次加入 -> 通过并查集判断是否形成环路
- 当 e 接近 n^2 时排序开销大，此时 Prim 的 O(n^2) 朴素实现更有优势
- 并查集的路径压缩和按秩合并可使边的判断接近 O(1)

## 易错点

1. 使用并查集时忘记先检查是否同集：加入边前必须调用 find(u) != find(v)，否则会形成环路
2. 排序的起点：边的排序必须按权值升序，不能降序。如果按降序贪心（称之为"反 Kruskal"）是一种不同算法（从完全图删最大边）
3. 最小生成树的唯一性：若所有边权互不相同则 MST 唯一；若有相同权值的边，可能产生多个不同的 MST（总权重相同）

## 例题

**例1：** 在 Kruskal 算法中，若当前考虑边 e = (u,v,w)，在何种条件下选择 e 不会产生环？

**解答：** 当 u 和 v 当前属于不同的连通分量，即 find(u) != find(v) 时，选择 e 不会形成环。

## 代码示例

```cpp
#include <vector>
#include <algorithm>
using namespace std;

struct Edge {
    int u, v, w;
    bool operator<(const Edge& o) const { return w < o.w; }
};

class UnionFind {
    vector<int> parent, rank;
public:
    UnionFind(int n) : parent(n), rank(n, 0) {
        for (int i = 0; i < n; i++) parent[i] = i;
    }
    int find(int x) {
        return parent[x] == x ? x : parent[x] = find(parent[x]);
    }
    void unite(int x, int y) {
        int rx = find(x), ry = find(y);
        if (rx == ry) return;
        if (rank[rx] < rank[ry]) parent[rx] = ry;
        else if (rank[rx] > rank[ry]) parent[ry] = rx;
        else { parent[ry] = rx; rank[rx]++; }
    }
};

vector<Edge> kruskal(int n, vector<Edge>& edges) {
    sort(edges.begin(), edges.end());
    UnionFind uf(n);
    vector<Edge> mst;
    for (Edge& e : edges) {
        if (uf.find(e.u) != uf.find(e.v)) {
            uf.unite(e.u, e.v);
            mst.push_back(e);
            if (mst.size() == n - 1) break;
        }
    }
    return mst;
}
```

```java
public class Kruskal {
    static class Edge implements Comparable<Edge> {
        int u, v, w;
        public int compareTo(Edge o) { return w - o.w; }
    }
    
    public static List<Edge> kruskal(int n, List<Edge> edges) {
        Collections.sort(edges);
        UnionFind uf = new UnionFind(n);
        List<Edge> mst = new ArrayList<>();
        for (Edge e : edges) {
            if (uf.find(e.u) != uf.find(e.v)) {
                uf.unite(e.u, e.v);
                mst.add(e);
                if (mst.size() == n - 1) break;
            }
        }
        return mst;
    }
}
```

## 关联页面

[[最小生成树-Prim]] [[并查集]] [[最短路径-Dijkstra]] [[排序]]
