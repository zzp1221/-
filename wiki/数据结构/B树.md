---
title: B树
course: 数据结构
chapter: 树
difficulty: ADVANCED
tags: [树, B树, 多路搜索树, 平衡, 外存, 磁盘IO]
aliases: [B-Tree, 多路平衡查找树]
source:
  - Rudolf Bayer 和 Edward McCreight 论文 (1971)
  - 《算法导论》
updated_at: 2026-05-02
---

## 核心定义

B 树（B-Tree）是一种多路平衡搜索树，专为磁盘或其他直接访问的辅助存储设备（如固态硬盘）而设计。一棵 m 阶 B 树满足以下性质：(1) 每个结点最多有 m 棵子树（m-1 个关键字）；(2) 根结点至少有两个子树（除非是叶子）；(3) 非根非叶结点至少有 ceil(m/2) 棵子树；(4) 所有叶子结点在同一层；(5) 结点内关键字有序排列。B 树通过增加分支数来降低树的高度，从而减少磁盘 IO 次数，特别适合外存索引场景。与 AVL/红黑树不同，B 树允许一个结点存储多个关键字。B 树的查找、插入、删除时间复杂度均为 O(log_m n)（树高）。

## 关键结论

- m 阶 B 树结点最多 m-1 个关键字，最少 ceil(m/2)-1 个（根除外）
- B 树通过"矮胖"结构减少磁盘 IO：一次磁盘块读写包含多个 key
- 查找：在结点内二分查找，然后按指针往下搜索
- 插入：总在叶子进行；若结点满则需要分裂，分裂可能向上递归
- 删除：可能涉及借位（从兄弟结点借）或合并（与兄弟合并），也可能向上递归
- 实际数据库中 B 树结点大小通常设为一个磁盘页的大小（如 4KB）

## 易错点

1. m 阶 B 树中 m 是"最大子树数"而非"最大关键字数"：最大关键字数为 m-1
2. 分裂时中间关键字的去向：结点满时产生新结点，mid 位置的关键字被提升到父结点中，mid 左边的留在原结点，mid 右边的移到新结点
3. 结点内关键字有序且各子树的范围满足：若结点有关键字 [k1, k2, ..., kd]，对应 d+1 棵子树，第 i 棵子树中所有元素介于 k_{i-1} 和 k_i 之间

## 例题

**例1：** 在一棵 5 阶 B 树中，非根非叶结点最少含有多少个关键字？

**解答：** 5 阶 B 树，非根非叶结点最少有 ceil(5/2) = 3 棵子树，最少有 ceil(5/2)-1 = 2 个关键字。

## 代码示例

```cpp
#include <vector>
#include <algorithm>
using namespace std;

template<typename T, int M>  // M 为阶数
class BTree {
    struct Node {
        vector<T> keys;           // 关键字数组
        vector<Node*> children;   // 子结点指针数组
        bool isLeaf;
        Node(bool leaf) : isLeaf(leaf) {}
    };
    
    Node* root;
    
public:
    BTree() { root = new Node(true); }
    
    // 在结点中二分查找 key 的位置
    int findIndex(Node* node, T key) {
        int idx = distance(node->keys.begin(),
            lower_bound(node->keys.begin(), node->keys.end(), key));
        return idx;
    }
    
    // 分裂满的孩子结点（child 是 parent 的第 idx 个孩子）
    void splitChild(Node* parent, int idx, Node* child) {
        int mid = (M - 1) / 2;
        Node* newNode = new Node(child->isLeaf);
        
        // 把 mid 右边的 key 移到新结点
        for (int i = mid + 1; i < M - 1; i++)
            newNode->keys.push_back(child->keys[i]);
        
        // 把 mid 右边的子树移到新结点
        if (!child->isLeaf)
            for (int i = mid + 1; i < M; i++)
                newNode->children.push_back(child->children[i]);
        
        // 提升 mid 到父结点
        parent->keys.insert(parent->keys.begin() + idx, child->keys[mid]);
        parent->children.insert(parent->children.begin() + idx + 1, newNode);
        
        // 截断原 child
        child->keys.resize(mid);
        if (!child->isLeaf)
            child->children.resize(mid + 1);
    }
    
    void insertNonFull(Node* node, T key) {
        int i = node->keys.size() - 1;
        if (node->isLeaf) {
            // 插入到叶子结点的合适位置
            node->keys.push_back(key);
            while (i >= 0 && key < node->keys[i]) {
                node->keys[i + 1] = node->keys[i];
                i--;
            }
            node->keys[i + 1] = key;
        } else {
            // 找到要插入的子树
            while (i >= 0 && key < node->keys[i]) i--;
            i++;
            if (node->children[i]->keys.size() == M - 1) {
                splitChild(node, i, node->children[i]);
                if (key > node->keys[i]) i++;
            }
            insertNonFull(node->children[i], key);
        }
    }
    
    void insert(T key) {
        if (root->keys.size() == M - 1) {
            Node* newRoot = new Node(false);
            newRoot->children.push_back(root);
            splitChild(newRoot, 0, root);
            root = newRoot;
        }
        insertNonFull(root, key);
    }
};
```

## 关联页面

[[B+树]] [[二叉排序树]] [[平衡二叉树-AVL]] [[红黑树]] [[查找]]
