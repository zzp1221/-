---
title: 平衡二叉树-AVL
course: 数据结构
chapter: 树
difficulty: ADVANCED
tags: [树, 平衡二叉树, AVL, 旋转, 平衡因子, LL, RR, LR, RL]
aliases: [AVL Tree, 自平衡二叉搜索树]
source:
  - Adelson-Velsky 和 Landis 论文 (1962)
  - 严蔚敏《数据结构(C语言版)》
updated_at: 2026-05-02
---

## 核心定义

AVL 树（以发明者 Adelson-Velsky 和 Landis 命名）是最早被发明的自平衡二叉搜索树。AVL 树或者是一棵空树，或者是满足以下条件的二叉搜索树：任意结点的左右子树高度差的绝对值不超过 1。将结点的左右子树高度之差定义为平衡因子（BF, Balance Factor），则 AVL 树中所有结点的平衡因子只能取 -1、0、1。当插入或删除操作导致某些结点的平衡因子绝对值超过 1 时，需要通过旋转操作恢复平衡。旋转分为四种类型：LL（右单旋）、RR（左单旋）、LR（先左后右双旋）、RL（先右后左双旋）。AVL 树保证了查找操作的最坏时间复杂度为 O(log n)，因为高度始终与 log n 成正比。

## 关键结论

- AVL 树是高度平衡的 BST，|BF| <= 1
- 查找最坏时间复杂度 O(log n)，因为树高严格 h <= 1.44 * log2(n+2)
- 四种旋转：LL（插入在左子树的左子树中）、RR、LR、RL
- 插入操作：最多 1 次旋转可恢复平衡，时间复杂度 O(log n)
- 删除操作：可能需要多次旋转（O(log n) 次），时间复杂度 O(log n)
- 每个结点需存储高度或平衡因子，空间开销小

## 易错点

1. LR 和 RL 的旋转方向搞反：LR 是"先左后右"——先对左子树做左旋（变成 LL），再对整体做右旋；但确切说是先对插入结点所在的左子树的右孩子做左旋，然后对根做右旋
2. 平衡因子更新时机及计算：旋转后需要从下往上更新旋转涉及结点的平衡因子（先更新子树后更新根）；不同的旋转模式有不同的更新公式
3. 单旋 vs 双旋的判断基础：当插入导致"从根到插入点的路径上"出现不平衡结点 A，看插入位置在 A 的左子树的左侧（LL）、左子树的右侧（LR）等来判断类型

## 例题

**例1：** 依次插入 {3, 2, 5, 1, 8} 到空的 AVL 树中，画出最终结果。

**解答：** 插入 3（根）；插入 2（3左）；插入 5（3右），平衡；插入 1（2左），3 的 BF 变为 -2（左重），类型 LL，对 3 做右旋，2 成为新根，1 在左；插入 8（5右），5 的 BF=-1，3 的 BF=1，平衡。最终：2 为根，左右孩子为 1 和 3，3 的右孩子为 5，5 的右孩子为 8。

## 代码示例

```cpp
#include <algorithm>
using namespace std;

template<typename T>
struct AVLNode {
    T key;
    AVLNode *left, *right;
    int height;
    AVLNode(T k) : key(k), left(nullptr), right(nullptr), height(1) {}
};

template<typename T>
class AVL {
    AVLNode<T>* root;
    
    int height(AVLNode<T>* node) {
        return node ? node->height : 0;
    }
    
    int balanceFactor(AVLNode<T>* node) {
        return node ? height(node->left) - height(node->right) : 0;
    }
    
    void updateHeight(AVLNode<T>* node) {
        node->height = max(height(node->left), height(node->right)) + 1;
    }
    
    // 右旋（处理 LL）
    AVLNode<T>* rotateR(AVLNode<T>* y) {
        AVLNode<T>* x = y->left;
        AVLNode<T>* t = x->right;
        x->right = y;
        y->left = t;
        updateHeight(y);
        updateHeight(x);
        return x;
    }
    
    // 左旋（处理 RR）
    AVLNode<T>* rotateL(AVLNode<T>* x) {
        AVLNode<T>* y = x->right;
        AVLNode<T>* t = y->left;
        y->left = x;
        x->right = t;
        updateHeight(x);
        updateHeight(y);
        return y;
    }
    
    AVLNode<T>* insert(AVLNode<T>* node, T key) {
        if (!node) return new AVLNode<T>(key);
        if (key < node->key)
            node->left = insert(node->left, key);
        else if (key > node->key)
            node->right = insert(node->right, key);
        else
            return node;  // 不插入重复值
        
        updateHeight(node);
        int bf = balanceFactor(node);
        
        // LL：左子树的左边插入
        if (bf > 1 && key < node->left->key)
            return rotateR(node);
        // RR：右子树的右边插入
        if (bf < -1 && key > node->right->key)
            return rotateL(node);
        // LR：左子树的右边插入
        if (bf > 1 && key > node->left->key) {
            node->left = rotateL(node->left);
            return rotateR(node);
        }
        // RL：右子树的左边插入
        if (bf < -1 && key < node->right->key) {
            node->right = rotateR(node->right);
            return rotateL(node);
        }
        return node;
    }
    
public:
    AVL() : root(nullptr) {}
    void insert(T key) { root = insert(root, key); }
};
```

```java
public class AVL<T extends Comparable<T>> {
    class Node {
        T key; Node left, right; int height;
        Node(T k) { key = k; height = 1; }
    }
    Node root;
    
    int height(Node n) { return n == null ? 0 : n.height; }
    int bf(Node n) { return height(n.left) - height(n.right); }
    
    void updateHeight(Node n) {
        n.height = Math.max(height(n.left), height(n.right)) + 1;
    }
    
    Node rotateR(Node y) {
        Node x = y.left; y.left = x.right; x.right = y;
        updateHeight(y); updateHeight(x);
        return x;
    }
    
    Node rotateL(Node x) {
        Node y = x.right; x.right = y.left; y.left = x;
        updateHeight(x); updateHeight(y);
        return y;
    }
    
    public void insert(T key) { root = insert(root, key); }
    
    Node insert(Node node, T key) {
        if (node == null) return new Node(key);
        int cmp = key.compareTo(node.key);
        if (cmp < 0) node.left = insert(node.left, key);
        else if (cmp > 0) node.right = insert(node.right, key);
        else return node;
        
        updateHeight(node);
        int balance = bf(node);
        
        if (balance > 1 && key.compareTo(node.left.key) < 0) return rotateR(node);
        if (balance < -1 && key.compareTo(node.right.key) > 0) return rotateL(node);
        if (balance > 1 && key.compareTo(node.left.key) > 0) {
            node.left = rotateL(node.left); return rotateR(node);
        }
        if (balance < -1 && key.compareTo(node.right.key) < 0) {
            node.right = rotateR(node.right); return rotateL(node);
        }
        return node;
    }
}
```

## 关联页面

[[红黑树]] [[二叉排序树]] [[B树]] [[二叉树]]
