---
title: 图的深度优先搜索 DFS
course: 数据结构
chapter: 图
difficulty: INTERMEDIATE
tags: [图, DFS, 深度优先搜索, 递归, 回溯, 连通分量]
aliases: [Depth First Search, DFS遍历]
source:
  - 严蔚敏《数据结构(C语言版)》
  - 《算法导论》
updated_at: 2026-05-02
---

## 核心定义

深度优先搜索（Depth First Search, DFS）是图的最基本的遍历算法之一。DFS 从图中某个起始顶点 v 出发，首先访问 v，然后从 v 的未被访问的邻接点中选择一个出发继续进行深度优先遍历，直到与 v 连通的所有顶点都被访问；若图中还有未被访问的顶点，则另选一个开始点重复上述过程，直至图中所有顶点都被访问。DFS 的本质是树的先根遍历在图上的推广。DFS 的实现方式有两种：(1) 递归实现（利用系统栈）；(2) 迭代实现（显式使用栈）。DFS 过程中需要维护 visited 数组标记已访问的顶点。邻接矩阵表示的 DFS 时间复杂度为 O(n^2)，邻接表表示的 DFS 时间复杂度为 O(n+e)。

## 关键结论

- DFS 遵循"一条路走到底"的原则，直到无路可走再回溯
- 递归实现简洁，利用系统调用栈；迭代实现需显式维护一个栈
- DFS 可以计算连通分量：每调用一次 DFS 说明发现一个新的连通分量
- DFS 生成树：通过 DFS 遍历可以得到 DFS 树（森林），树边和回边是重要概念（用于检测环、拓扑排序等）
- 邻接表存储时时间复杂度为 O(n+e)，n 为顶点数，e 为边数

## 易错点

1. 非连通图的处理：DFS 外层必须有一个循环遍历所有顶点，对每个未访问的顶点调用 DFS 子过程，否则会漏掉非连通分量
2. visited 标记的时机：必须在访问顶点之前标记（而非之后），否则在有环的图中会产生无限递归
3. 递归版与迭代版的栈行为不完全一致：迭代版在顶点入栈时标记 visited，递归版在进入函数时标记；但邻接点的遍历顺序恰好相反（除非显式反向入栈）

## 例题

**例1：** 用邻接表表示的有向图中，从顶点 0 出发做 DFS，问 DFS 过程能否访问所有顶点？若否，如何处理？

**解答：** 不一定。若图不是强连通或无向有穷路径可达，从单个起点只能访问其所在连通/可达分量。处理方法是在外层对所有未访问顶点循环调用 DFS。

## 代码示例

```cpp
#include <vector>
#include <stack>
using namespace std;

const int MAXN = 1000;
vector<int> adj[MAXN];  // 邻接表
bool visited[MAXN];

// 递归 DFS
void dfsRecursive(int v) {
    visited[v] = true;
    // 处理顶点 v（如打印）
    
    for (int neighbor : adj[v])
        if (!visited[neighbor])
            dfsRecursive(neighbor);
}

// 迭代 DFS
void dfsIterative(int start) {
    stack<int> st;
    st.push(start);
    while (!st.empty()) {
        int v = st.top(); st.pop();
        if (visited[v]) continue;
        visited[v] = true;
        // 处理顶点 v
        for (int neighbor : adj[v])
            if (!visited[neighbor])
                st.push(neighbor);
    }
}

// 对全图做 DFS（处理非连通）
void dfsTraverse(int n) {
    fill(visited, visited + n, false);
    for (int i = 0; i < n; i++)
        if (!visited[i])
            dfsRecursive(i);
}
```

```java
public class GraphDFS {
    List<Integer>[] adj;
    boolean[] visited;
    
    void dfsRecursive(int v) {
        visited[v] = true;
        for (int neighbor : adj[v])
            if (!visited[neighbor])
                dfsRecursive(neighbor);
    }
    
    void dfsIterative(int start) {
        Stack<Integer> stack = new Stack<>();
        stack.push(start);
        while (!stack.isEmpty()) {
            int v = stack.pop();
            if (visited[v]) continue;
            visited[v] = true;
            for (int neighbor : adj[v])
                if (!visited[neighbor])
                    stack.push(neighbor);
        }
    }
}
```

## 关联页面

[[图-BFS]] [[图的存储-邻接矩阵与邻接表]] [[拓扑排序]] [[关键路径]] [[二叉树遍历]]
