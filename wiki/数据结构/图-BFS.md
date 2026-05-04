---
title: 图的广度优先搜索 BFS
course: 数据结构
chapter: 图
difficulty: INTERMEDIATE
tags: [图, BFS, 广度优先搜索, 队列, 最短路径, 无权图]
aliases: [Breadth First Search, BFS遍历, 宽度优先搜索]
source:
  - 严蔚敏《数据结构(C语言版)》
  - 《算法导论》
updated_at: 2026-05-02
---

## 核心定义

广度优先搜索（Breadth First Search, BFS）是图的另一基本遍历算法。BFS 从图中某个起始顶点 v 出发，先访问 v，然后依次访问 v 的所有未被访问的邻接点，再依次从这些邻接点出发访问它们的邻接点，一层一层向外扩展，直至所有可达顶点都被访问。BFS 的本质是树的层序遍历在图上的推广。BFS 使用队列来管理待访问的顶点，时间复杂度与 DFS 相同：邻接矩阵 O(n^2)，邻接表 O(n+e)。BFS 的一个重要应用是无权图的最短路径问题：从起点出发 BFS 各顶点的"层数"就是距离起点的最短距离（边数最少）。

## 关键结论

- BFS 是一层一层向外扩展的遍历方式，使用队列实现
- BFS 可以求解无权图（权值为 1）的最短路径问题：BFS 生成树中顶点的深度即最短距离
- BFS 也可以用于求连通分量（与 DFS 同理）
- 邻接表 BFS 的时间复杂度为 O(n+e)，邻接矩阵为 O(n^2)
- 通过记录 parent 数组可以还原最短路径

## 易错点

1. visited 必须在入队时就标记：若等到出队时才标记，可能导致同一顶点被多次入队，造成大量重复操作甚至无限循环
2. 非连通图的处理：与 DFS 相同，外层需循环检查所有顶点
3. 无权最短路径的前提：BFS 只适用于边权为 1（或无权）的图；若边有权重，需用 Dijkstra 或 SPFA 等算法

## 例题

**例1：** 用 BFS 在无向无权图中求从顶点 s 到顶点 t 的最短距离，描述算法思路。

**解答：** 维护数组 dist 和队列。dist[s]=0，s 入队。当队列不空时：取出队头 v，遍历 v 的邻接点 u——若 u 未被访问（dist 为 INF），则 dist[u]=dist[v]+1，u 入队，parent[u]=v。当 t 出队时 dist[t] 即最短距离。还可通过 parent 数组反向追溯具体路径。

## 代码示例

```cpp
#include <vector>
#include <queue>
using namespace std;

const int MAXN = 1000;
vector<int> adj[MAXN];
bool visited[MAXN];
int dist[MAXN], parent[MAXN];

// BFS 遍历
void bfsTraverse(int start) {
    queue<int> q;
    visited[start] = true;
    q.push(start);
    while (!q.empty()) {
        int v = q.front(); q.pop();
        // 处理顶点 v
        for (int u : adj[v]) {
            if (!visited[u]) {
                visited[u] = true;
                q.push(u);
            }
        }
    }
}

// BFS 求无权最短路径
void bfsShortestPath(int start, int n) {
    fill(visited, visited + n, false);
    fill(dist, dist + n, -1);
    queue<int> q;
    visited[start] = true;
    dist[start] = 0;
    parent[start] = -1;
    q.push(start);
    while (!q.empty()) {
        int v = q.front(); q.pop();
        for (int u : adj[v]) {
            if (!visited[u]) {
                visited[u] = true;
                dist[u] = dist[v] + 1;
                parent[u] = v;
                q.push(u);
            }
        }
    }
}

// 打印从 start 到 target 的路径
void printPath(int target) {
    if (dist[target] == -1) return;  // 不可达
    vector<int> path;
    for (int v = target; v != -1; v = parent[v])
        path.push_back(v);
    reverse(path.begin(), path.end());
    for (int v : path) cout << v << " ";
}
```

```java
public class GraphBFS {
    List<Integer>[] adj;
    boolean[] visited;
    int[] dist, parent;
    
    void bfsShortestPath(int start, int n) {
        visited = new boolean[n];
        dist = new int[n];
        parent = new int[n];
        Arrays.fill(dist, -1);
        Queue<Integer> q = new LinkedList<>();
        visited[start] = true;
        dist[start] = 0;
        q.offer(start);
        while (!q.isEmpty()) {
            int v = q.poll();
            for (int u : adj[v]) {
                if (!visited[u]) {
                    visited[u] = true;
                    dist[u] = dist[v] + 1;
                    parent[u] = v;
                    q.offer(u);
                }
            }
        }
    }
}
```

## 关联页面

[[图-DFS]] [[图的存储-邻接矩阵与邻接表]] [[最短路径-Dijkstra]] [[二叉树遍历]]
