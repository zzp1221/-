---
title: 最短路径-Floyd算法
course: 数据结构
chapter: 图
difficulty: INTERMEDIATE
tags: [图, 最短路径, Floyd, 动态规划, 多源最短路径, 三重循环]
aliases: [Floyd-Warshall Algorithm, APSP, 多源最短路径]
source:
  - Robert Floyd 论文 (1962); Stephen Warshall 论文 (1962)
  - 《算法导论》
updated_at: 2026-05-02
---

## 核心定义

Floyd-Warshall 算法（简称 Floyd 算法）是利用动态规划思想求解图中所有顶点对之间最短路径（All-Pairs Shortest Path, APSP）的经典算法。算法维护一个 n*n 的距离矩阵 D，D[i][j] 表示从 i 到 j 的最短距离。初始时 D[i][j] = w(i,j)（若 i 到 j 有边），否则为 INF。算法通过三重循环，依次尝试将每个顶点 k 作为"中转点"：若经过 k 的路径更短，即 D[i][j] > D[i][k] + D[k][j]，则更新 D[i][j]。算法结束后 D[i][j] 即为 i 到 j 的最短距离。Floyd 的时间复杂度为 O(n^3)，空间复杂度为 O(n^2)，适用于稠密图或顶点数不很大的情况。算法可以处理负权边，但不能处理负权环。

## 关键结论

- 核心递推公式：D[k][i][j] = min(D[k-1][i][j], D[k-1][i][k] + D[k-1][k][j])，可空间优化到二维
- 时间复杂度 O(n^3)，实现极为简洁（三重 for 循环）
- 可处理负权边（但无负权环），Dijkstra 不能处理负权
- 可通过 path 矩阵记录中转点以重构具体路径
- 对于稀疏图，n 次 Dijkstra O(n*(e+n)log n) 可能更优

## 易错点

1. 三重循环的顺序：必须 k -> i -> j（中转点在最外层），顺序错误会导致结果不正确。原因：Floyd 的动态规划依赖阶段 k
2. 检测负权环：算法执行完后检查对角线元素，若 D[i][i] < 0，说明存在负权环
3. Dijkstra vs Floyd 的适用场景：Dijkstra O(n*(e+n)log n) 对稀疏图更优；Floyd O(n^3) 实现简单，适合稠密图或 n 较小 (<500) 的情况

## 例题

**例1：** 使用 Floyd 算法后，若 D[i][i] < 0 意味着什么？

**解答：** 意味着图中存在从 i 出发回到 i 的负权环（因为自己到自己的最短距离变成了负数），此时最短路径无下界，算法失效。

## 代码示例

```cpp
#include <vector>
using namespace std;
const int INF = 1e9;

void floyd(int n, vector<vector<int>>& dist) {
    for (int k = 0; k < n; k++)
        for (int i = 0; i < n; i++)
            for (int j = 0; j < n; j++)
                if (dist[i][k] != INF && dist[k][j] != INF)
                    dist[i][j] = min(dist[i][j], dist[i][k] + dist[k][j]);
}

// 带路径记录版本
void floydWithPath(int n, vector<vector<int>>& dist, vector<vector<int>>& path) {
    for (int k = 0; k < n; k++)
        for (int i = 0; i < n; i++)
            for (int j = 0; j < n; j++)
                if (dist[i][k] + dist[k][j] < dist[i][j]) {
                    dist[i][j] = dist[i][k] + dist[k][j];
                    path[i][j] = k;  // 记录中转点
                }
}
```

```java
public class Floyd {
    static final int INF = (int)1e9;
    
    public static void floyd(int n, int[][] dist) {
        for (int k = 0; k < n; k++)
            for (int i = 0; i < n; i++)
                for (int j = 0; j < n; j++)
                    if (dist[i][k] != INF && dist[k][j] != INF)
                        dist[i][j] = Math.min(dist[i][j], dist[i][k] + dist[k][j]);
    }
}
```

## 关联页面

[[最短路径-Dijkstra]] [[最短路径-BellmanFord]] [[动态规划]] [[图的存储-邻接矩阵与邻接表]]
