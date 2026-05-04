---
title: 根树与m叉树
course: 离散数学
chapter: 树
difficulty: INTERMEDIATE
tags: [根树, m叉树, 二叉树, 完全二叉树, 满二叉树, Huffman编码, 最优二叉树]
aliases: [Rooted Tree, m-ary Tree, Binary Tree, 有根树]
source:
  - Kenneth H. Rosen《离散数学及其应用》
updated_at: 2026-05-02
---

## 核心定义

根树（Rooted Tree）是在无向树的基础上选定一个顶点作为**根**（Root），并约定所有边都"指向远离根的方向"后形成的有向树结构。在根树中，若存在从 u 到 v 的有向边，则称 u 是 v 的**父亲**（Parent），v 是 u 的**孩子**（Child）。根是唯一没有父亲的顶点；叶子是没有孩子的顶点。**m叉树**（m-ary Tree）是每个顶点至多有 m 个孩子的根树；**满m叉树**（Full m-ary Tree）是每个内部顶点恰有 m 个孩子；**完全m叉树**（Complete m-ary Tree）是所有层（除了可能的最后一层）都被填满，且最后一层的所有顶点尽量靠左排列。特别地，m=2 时为**二叉树**（Binary Tree），是计算机科学中最核心的数据结构之一。二叉树与有序树不同——二叉树严格区分左孩子和右孩子。**Huffman编码**利用二叉树构造最优前缀码：给定每个符号的出现频率，自底向上贪心地合并频率最小的两棵树，产生最优二叉树。

## 关键结论

- 对于满 m 叉树，若有 i 个内部顶点和 ℓ 个叶子，则 ℓ = (m−1)i + 1——这是解根树计数问题的核心公式
- 含有 n 个顶点的完全二叉树的深度为 ⌊log₂ n⌋（根深度为0）
- m 叉树的高度 h 满足：h ≥ ⌈logₘ ℓ⌉（以叶子数为界），最大高度 ℓ−1（退化为链）
- 二叉树遍历分前序（Preorder: 根-左-右）、中序（Inorder: 左-根-右）、后序（Postorder: 左-右-根）、层序（Level Order）
- Huffman编码产生最优前缀码，编码长度为期望编码长度的下界（熵）
- 平衡二叉树（AVL树、红黑树）保证 O(log n) 的查找/插入/删除复杂度

## 易错点

1. 混淆"满二叉树"与"完全二叉树"：满二叉树每个内部顶点恰有两个孩子；完全二叉树除了可能的最后一层外所有层满，且最后层左对齐
2. 将二叉树节点的"高度"和"深度"混淆：深度是从根到该节点的路径长度（自上而下），高度是从该节点到最深叶子的路径长度（自下而上）
3. 在二叉树的属性计算中将根算作深度1：标准定义中根的深度为0

## 例题

**例题1**：一棵满二叉树有 15 个内部顶点，求叶子数。

**解答**：对满二叉树 m=2，ℓ = (m−1)i + 1 = (2−1)×15 + 1 = 16。总顶点数 = i + ℓ = 31。这是一棵深度为 4（根深度0）的满二叉树。

**例题2**：用Huffman算法为频率 A:0.4, B:0.3, C:0.15, D:0.1, E:0.05 构造最优二叉树。

**解答**：合并最小两个：E(0.05) + D(0.1) = 0.15。现在最小：C(0.15) + ED(0.15) = 0.30。现在：A(0.4) 和 B(0.3) 和 CED(0.30)。合并 B + CED = 0.60。最后 A + BCED = 1.0。编码（左右自定）：A:0, B:10, C:110, D:1110, E:1111。平均码长 = 1×0.4 + 2×0.3 + 3×0.15 + 4×0.1 + 4×0.05 = 2.05。

## 代码示例

```python
from heapq import heappush, heappop, heapify
from collections import Counter

class HuffmanNode:
    def __init__(self, char, freq):
        self.char = char
        self.freq = freq
        self.left = self.right = None
    
    def __lt__(self, other):
        return self.freq < other.freq

def huffman_encoding(text):
    freq = Counter(text)
    heap = [HuffmanNode(c, f) for c, f in freq.items()]
    heapify(heap)
    
    while len(heap) > 1:
        left = heappop(heap)
        right = heappop(heap)
        merged = HuffmanNode(None, left.freq + right.freq)
        merged.left, merged.right = left, right
        heappush(heap, merged)
    
    def build_codes(node, code=""):
        if node.char is not None:
            codes[node.char] = code
            return
        build_codes(node.left, code + "0")
        build_codes(node.right, code + "1")
    
    codes = {}
    build_codes(heap[0])
    return codes

print(huffman_encoding("ABRACADABRA"))
```

## 关联页面

[[无向树]] [[生成树与最小生成树]] [[图类型]] [[函数-单射-满射-双射]]
