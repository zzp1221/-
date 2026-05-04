---
title: 常见NPC问题
course: 算法设计与分析
chapter: 第七章 计算复杂性理论
difficulty: ADVANCED
tags: [NPC问题, NP完全, Karp21, SAT, TSP, 顶点覆盖, 团问题, 子集和]
aliases: [Common NPC Problems, Karp's 21 Problems]
source:
  - Garey & Johnson, Computers and Intractability (1979)
  - Karp, Reducibility Among Combinatorial Problems (1972)
updated_at: 2026-05-02

---

## 核心定义

常见的 NP 完全问题是从 SAT 出发通过多项式规约不断扩展的问题家族。Richard Karp 在 1972 年发表了具有里程碑意义的论文，证明了 21 个经典组合问题的 NP 完全性。这些问题分布于图论、集合、数列、调度、网络等领域。以下是最核心的 NPC 问题：SAT（布尔可满足性），3-SAT（每个子句最多 3 个文字的 SAT），团问题（Clique），顶点覆盖（Vertex Cover），独立集（Independent Set），哈密顿回路（Hamiltonian Cycle），旅行商问题（TSP 判定版），子集和（Subset Sum），划分问题（Partition），0-1 背包（判定版），装箱问题（Bin Packing），图着色（Graph Coloring），集合覆盖（Set Cover）等。这些问题在理论上构成了 NPC 问题的"规约网络"，在实践中识别 NPC 问题有助于避免"求解精确最优"的徒劳而转向近似算法或启发式。

## 关键结论

- SAT 是第一个被证明的 NPC 问题（Cook-Levin 定理），是 NPC 规约树形结构中的根节点
- 3-SAT 在许多规约中用作"中间源"：因为每个子句文字有限，更容易规约到其他组合问题
- 团问题、顶点覆盖、独立集三者之间可以通过图的补图相互规约，被视为同一等价类
- 子集和问题是"弱 NPC"：存在伪多项式时间 DP 算法 O(n*sum)；强 NPC 问题没有伪多项式算法（如 TSP）
- 一些 NPC 问题在特殊图类上变得多项式可解：如在二分图中的顶点覆盖、在弦图中的着色

## 易错点

1. 混淆 NPC 问题和 NP-Hard 问题：判定型的哈密顿回路是 NPC，而带权的优化 TSP 是 NP-Hard（非 NPC 因为不在 NP 判定问题类中）。
2. "伪多项式时间"不等于多项式时间：O(nW) 的 DP 算法在 W 以 bit 衡量时是指数时间。
3. 判定版和优化版的 NPC 属性不同：优化版通常是 NP-Hard 而非 NPC。需仔细区分。

## 例题

**例题1：** 证明 3-SAT <=_p 团问题（Clique）。

**解答：** 给定 3-SAT 公式 φ = C1 ∧ C2 ∧ ... ∧ Ck，每个 Ci = (l_{i,1} ∨ l_{i,2} ∨ l_{i,3})。构造无向图 G：每个文字出现作为一个顶点（共 3k 个顶点）。两个顶点之间连边 iff 它们来自不同子句且不互斥（x 和 ¬x 不连边，其他情况都连边）。则 φ 可满足当且仅当 G 存在大小为 k 的团。构造在多项式时间内完成，故 3-SAT <=_p Clique。

**例题2：** 判断 2-SAT 为什么是 P 问题。

**解答：** 2-SAT（每个子句最多 2 个文字）可以通过蕴含图（Implication Graph） + SCC 在多项式时间内求解。将每个文字 x 和其否定 ¬x 分别作为两个顶点，将子句 (a∨b) 转化为边 (¬a→b) 和 (¬b→a)。则公式可满足当且仅当没有变量 x 使得 x 和 ¬x 在同一强连通分量中。这使用 Tarjan/Kosaraju 可在 O(n+m) 时间内完成。

## 代码示例

```python
# 子集和问题的 NP 验证器（属于 NP 的证明）
def verify_subset_sum(nums, target, certificate):
    """
    验证 certificate 是否为子集和问题的合法解
    certificate: 布尔数组表示哪些元素被选中
    验证时间 O(n)，证明子集和属于 NP
    """
    if len(certificate) != len(nums):
        return False
    total = sum(nums[i] for i in range(len(nums)) if certificate[i])
    return total == target

# 3-SAT 的验证器
def verify_3sat(clauses, assignment):
    """
    clauses: 列表，每个是三元组(lit1, lit2, lit3)，负文字用负数
    assignment: 字典 {var_id: True/False}
    """
    for lit1, lit2, lit3 in clauses:
        val1 = assignment[abs(lit1)] if lit1 > 0 else not assignment[abs(lit1)]
        val2 = assignment[abs(lit2)] if lit2 > 0 else not assignment[abs(lit2)]
        val3 = assignment[abs(lit3)] if lit3 > 0 else not assignment[abs(lit3)]
        if not (val1 or val2 or val3):
            return False
    return True

# 2-SAT 求解器 O(n+m)
def solve_2sat(n_vars, clauses):
    """使用 SCC 求解 2-SAT"""
    # 每个变量 i 映射为 2i (True) 和 2i+1 (False)
    N = 2 * n_vars
    graph = [[] for _ in range(N)]
    
    for a, b in clauses:
        # 处理文字的正负
        def idx(lit):
            return 2 * (abs(lit) - 1) + (0 if lit > 0 else 1)
        u = idx(-a)  # ¬a -> b
        v = idx(b)
        graph[u].append(v)
        u = idx(-b)  # ¬b -> a
        v = idx(a)
        graph[u].append(v)
    
    # 求 SCC（可使用 Tarjan/Kosaraju）
    # 检查是否存在 i 使得 2i 和 2i+1 在同一 SCC
    # 若存在则无解；否则通过拓扑序赋值（省略具体实现）
    pass

print(verify_subset_sum([3, 1, 4, 2], 9, [True, False, True, True]))
```

## 关联页面

[[NP完全性概述]] [[SAT问题]] [[规约]] [[近似算法概述]] [[计算复杂性下界]]
