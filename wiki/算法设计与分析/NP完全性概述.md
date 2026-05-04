---
title: NP完全性概述
course: 算法设计与分析
chapter: 第七章 计算复杂性理论
difficulty: ADVANCED
tags: [NP完全性, P类, NP类, NPC, 规约, 计算复杂性, 判定问题]
aliases: [NP-Completeness, P vs NP, NPC, NP-Hard]
source:
  - Cormen, Introduction to Algorithms (CLRS)
  - Garey & Johnson, Computers and Intractability (1979)
updated_at: 2026-05-02

---

## 核心定义

NP完全性（NP-Completeness）理论是计算复杂性理论的核心内容，研究问题的内在困难程度。判定问题（Decision Problem）是输出为"是"或"否"的问题。P 类（Polynomial Time）包含所有能在多项式时间内用确定型图灵机求解的判定问题。NP 类（Nondeterministic Polynomial Time）包含所有能在多项式时间内用非确定型图灵机求解的判定问题，等价定义为"解可在多项式时间内被验证"。显然 P ⊆ NP，但 P 是否等于 NP 是计算机科学最大的未解之谜。一个判定问题 L 是 NPC（NP-Complete）的，如果 L ∈ NP 且所有 NP 问题都可以多项式时间规约到 L。如果一个问题至少和 NPC 一样难（不一定在 NP 中），则称为 NP-Hard（NP难）。第一个被证明的 NPC 问题是 Cook-Levin 定理中的 SAT（布尔可满足性问题）。证明新问题的 NPC 性需两步：证明它属于 NP，将一个已知 NPC 问题多项式时间规约到它。

## 关键结论

- P ⊆ NP ⊆ PSPACE ⊆ EXPTIME（各级真包含关系尚未完全证明）
- Cook-Levin 定理（1971）：SAT 是第一个被证明的 NPC 问题，奠定了 NP 完全性理论
- 规约（Reduction）：将问题 A 的实例在多项式时间内转化为问题 B 的实例，使得 A 的答案与 B 的答案相同
- 经典 NPC 问题：SAT、3-SAT、团问题（Clique）、顶点覆盖（Vertex Cover）、哈密顿回路、子集和、0-1背包（判定版）、旅行商问题（TSP）
- 若 P = NP：所有 NPC 问题（包括密码学所依赖的整数分解）都可多项式时间解决，将对计算机科学和社会产生颠覆性影响

## 易错点

1. NPC 和 NP-Hard 的区别：NPC 要求问题本身属于 NP 类（解可验证），NP-Hard 不要求。例如 TSP 的优化版本是 NP-Hard 但不是 NPC（因为不是判定问题）。
2. 规约方向不能搞反：证明问题 B 是 NPC，需要将已知 NPC 问题 A 规约到 B（A ≤_p B），而不是将 B 规约到 A。
3. "多项式时间"的系数可能极大：O(n^100) 也属于多项式时间，但这类算法在实践中不可行。

## 例题

**例题1：** 证明二分图顶点覆盖 <= 二分图最大匹配。

**解答：** Konig 定理：在二分图中，最小顶点覆盖的大小等于最大匹配的大小。虽然最大匹配（P 问题）和顶点覆盖（NPC 问题）一般不等价，但在二分图这一特殊结构上两者相等，使得二分图顶点覆盖也是多项式可解的。这展示了问题结构的限制可以将 NPC 降级为 P。

**例题2：** 证明 3-SAT <=_p 团问题（Clique），从而证明 Clique 是 NPC。

**解答：** 给定 3-SAT 公式 φ = C1 ∧ C2 ∧ ... ∧ Ck，每个子句 3 个文字。构造图 G：每个文字出现的每次出现为一个顶点（共有 3k 个顶点），若两个文字来自不同子句且不互斥（x 和 ¬x 互斥），则在它们之间连边。则 φ 可满足 <=> G 中存在大小为 k 的团。由于 3-SAT 是 NPC，Clique 也是 NPC。

## 代码示例

```python
# NP 问题验证示例：子集和问题的验证器
def verify_subset_sum(nums, target, certificate):
    """
    验证 certificate 是否是子集和问题的合法解
    certificate: 选择的元素索引列表
    O(n) 时间验证，用于说明子集和属于 NP
    """
    total = 0
    for idx in certificate:
        if idx < 0 or idx >= len(nums):
            return False  # 非法索引
        total += nums[idx]
    return total == target

# 验证旅行商问题
def verify_tsp(dist_matrix, limit, certificate):
    """验证给定路径长度是否 <= limit"""
    n = len(dist_matrix)
    if len(certificate) != n:
        return False
    if len(set(certificate)) != n:
        return False  # 不走重复城市
    total = 0
    for i in range(n - 1):
        total += dist_matrix[certificate[i]][certificate[i + 1]]
    total += dist_matrix[certificate[-1]][certificate[0]]
    return total <= limit

# 示例
nums = [3, 1, 4, 2, 2]
cert = [0, 2, 4]  # 选 nums[0]+nums[2]+nums[4]=3+4+2=9
print(verify_subset_sum(nums, 9, cert))  # True
```

## 关联页面

[[P类与NP类]] [[规约]] [[SAT问题]] [[近似算法概述]] [[计算复杂性下界]]
