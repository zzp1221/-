---
title: B+树
course: 数据结构
chapter: 树
difficulty: ADVANCED
tags: [树, B+树, 索引, 数据库, 文件系统, 范围查询]
aliases: [B+Tree, B+索引]
source:
  - 《算法导论》
  - 《数据库系统概念》
updated_at: 2026-05-02
---

## 核心定义

B+ 树是 B 树的一种变体，广泛应用于数据库索引和文件系统（如 MySQL 的 InnoDB 引擎）。与 B 树的关键区别有：(1) B+ 树的非叶子结点只存储索引关键字和子树指针，不存储实际数据记录，所有数据记录（或指向数据的指针）都存储在叶子结点中；(2) 所有叶子结点通过链表指针按关键字顺序连接，形成有序的线性结构，这使得范围查询非常高效；(3) 非叶子结点中的关键字数量与子树数量相同（而不像 B 树是 n-1 个关键字）。查找操作必须走到叶子结点才能确定是否存在（或确定最终取值）。B+ 树通过将全部数据下沉到叶子层并使叶子链表化，天生适合磁盘 I/O 优化和批量区间扫描。

## 关键结论

- 所有关键字均出现在叶子结点中，非叶结点仅为索引
- 非叶子结点关键字数等于子树数（n 棵子树对应 n 个分隔关键字）
- 叶子结点按关键码有序，并通过链表双向或多向连接，支持 O(log n) 点查询和 O(log n + k) 区间查询
- B+ 树插入若引起叶子分裂，父结点仅同步增加一个索引分隔键，数据全在叶子
- 数据库常用 B+ 树而非 B 树，因为 B+ 树更利于范围扫描（顺序遍历叶子链表）
- 叶子结点内部使用顺序存储（二分查找），非叶结点内也是二分查找确定走向

## 易错点

1. B+ 树中叶子链表维护：插入新元素时可能需要在分裂后维护叶子链（调整前驱后继指针），很多同学忽略这一步
2. 查找必须走到叶子：即使非叶结点中包含了查询关键字，仍需要走到叶子层才能获取实际数据记录（或确认记录确实存在）
3. B+ 树与 B 树的应用场景区分：B+ 树叶子有链表适合范围查询和顺序遍历，B 树可以"提前结束"，但数据库领域几乎清一色用 B+ 树

## 例题

**例1：** 为什么数据库索引通常使用 B+ 树而非二叉搜索树（如 AVL）？

**解答：** (1) B+ 树是多路搜索树，树的高度远低于二叉搜索树，磁盘 I/O 次数少；(2) B+ 树叶子结点形成有序链表，支持高效的范围查询和顺序扫描；(3) B+ 树结点容量可与磁盘页大小对齐，一次 I/O 加载多个键值。

## 代码示例

```cpp
#include <vector>
#include <algorithm>
using namespace std;

template<typename T, int ORDER>
class BPlusTree {
    struct Node {
        vector<T> keys;
        vector<Node*> children;
        Node* next;  // 叶子结点链表指针
        bool isLeaf;
        Node(bool leaf) : isLeaf(leaf), next(nullptr) {}
    };
    
    Node* root;
    
public:
    BPlusTree() { root = new Node(true); }
    
    // 在叶子的有序链表中搜索（示例：范围查询）
    vector<T> rangeSearch(T low, T high) {
        vector<T> result;
        Node* cur = root;
        // 走到叶子结点（简化：假设根即叶子或只一层）
        while (!cur->isLeaf) {
            int i = 0;
            while (i < cur->keys.size() && low >= cur->keys[i]) i++;
            cur = cur->children[i];
        }
        // 遍历叶子链表
        while (cur) {
            for (int i = 0; i < cur->keys.size(); i++) {
                if (cur->keys[i] >= low && cur->keys[i] <= high)
                    result.push_back(cur->keys[i]);
                if (cur->keys[i] > high) return result;
            }
            cur = cur->next;
        }
        return result;
    }
};
```

## 关联页面

[[B树]] [[二叉排序树]] [[平衡二叉树-AVL]] [[查找]] [[哈希表]]
