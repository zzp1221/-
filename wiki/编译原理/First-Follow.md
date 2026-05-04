---
title: First与Follow集
course: 编译原理
chapter: 语法分析
difficulty: INTERMEDIATE
tags: [First集, Follow集, 预测分析, LL1, 语法分析, 首符号集, 后继符号集]
aliases: [FIRST Set, FOLLOW Set, 首符集, 后继集]
source:
  - Alfred V. Aho《Compilers: Principles, Techniques, and Tools》(龙书)
updated_at: 2026-05-02
---

## 核心定义

FIRST 集和 FOLLOW 集是构造 LL(1) 预测分析表的核心数据结构，为文法中的每个非终结符提供前瞻信息。**FIRST(α)** 定义为可从文法符号串 α 推导出的所有可能句子的**首终结符**的集合。形式化：FIRST(α) = {a | α ⇒* aβ, a∈Vₜ} ∪ (若 α ⇒* ε 则 ∪ {ε})。**FOLLOW(A)** 定义为在所有句型中紧跟在非终结符 A 之后可能出现的**终结符**的集合。形式化：FOLLOW(A) = {a | S ⇒* βAaγ, a∈Vₜ}，其中 $（输入结束符）总在 FOLLOW(S) 中。

FIRST 集的计算规则（递归算法）：(1) 若 X 是终结符，FIRST(X) = {X}；(2) 若 X → ε，将 ε 加入 FIRST(X)；(3) 若 X → Y₁Y₂...Yₖ，依次将 FIRST(Yᵢ) − {ε} 加入 FIRST(X)，直到某个 Yᵢ 不能推导出 ε 为止；若所有 Yᵢ 都能推导出 ε，则将 ε 加入 FIRST(X)。FOLLOW 集的计算规则：(1) $ ∈ FOLLOW(S)；(2) 对产生式 A → αBβ，将 FIRST(β)−{ε} 加入 FOLLOW(B)；(3) 对产生式 A → αB 或 A → αBβ 且 β ⇒* ε，将 FOLLOW(A) 加入 FOLLOW(B)。反复应用规则直到各 FOLLOW 集不再增大。

## 关键结论

- FIRST 集反映了从某符号串出发"首先能遇到什么终结符"
- FOLLOW 集反映了在句型中该非终结符后面"跟着什么终结符"
- 当 FIRST(α) 含 ε 时，意味着 α 可能推导为空——此时 FOLLOW(A) 的信息对于选择产生式至关重要
- LL(1) 条件的形式化：对 A → α | β，FIRST(α) ∩ FIRST(β) = ∅；若 ε∈FIRST(α)，则 FIRST(β) ∩ FOLLOW(A) = ∅
- FIRST 和 FOLLOW 的计算是单调的（只增不减），保证算法终止
- FIRST 和 FOLLOW 也是 SLR(1) 和 LALR(1) 等 LR 分析方法的重要组成部分

## 易错点

1. 忘记在 FOLLOW 计算中传递 FOLLOW 集：若 B 出现在产生式末尾（或后面全可推导为空），需将 FOLLOW(A) 加入 FOLLOW(B)，初学者常漏掉此步
2. ε 在 FIRST 集中的传播：需要反复扫描产生式直到 FIRST 集收敛——单次扫描不够
3. FOLLOW 集不包含 ε：ε 不是终结符，不能出现在字符串中；只有 FIRST 集才可能含 ε

## 例题

**例题1**：计算文法 E → TE', E' → +TE' | ε, T → FT', T' → *FT' | ε, F → (E) | id 的 FIRST 和 FOLLOW 集。

**解答**：
FIRST(F) = {(, id}；FIRST(T) = FIRST(F) = {(, id}；FIRST(T') = {*, ε}；FIRST(E) = FIRST(T) = {(, id}；FIRST(E') = {+, ε}。

FOLLOW(E) = {), $}；FOLLOW(E') = FOLLOW(E) = {), $}；FOLLOW(T) = FIRST(E')−{ε} ∪ FOLLOW(E') = {+, ), $}；FOLLOW(T') = FOLLOW(T) = {+, ), $}；FOLLOW(F) = FIRST(T')−{ε} ∪ FOLLOW(T') = {*, +, ), $}。

**例题2**：为什么 FOLLOW 集对 LL(1) 分析重要？试举例。

**解答**：当有 ε-产生式 A → ε 时，FOLLOW(A) 指示何时选择该 ε-产生式。例如文法 S → aA, A → b | ε。FOLLOW(A) = {$}。当读入 a 后栈顶为 A，当前输入为 $ 时，根据 FOLLOW(A) 选择 A → ε。

## 代码示例

```python
def compute_first_follow(productions, start):
    Vt = set('+*()id')  # 简化：假设小写和符号为终结符
    
    first = {nt: set() for nt in productions}
    # 终结符的FIRST
    for nt in productions:
        for rhs in productions[nt]:
            for s in rhs:
                first.setdefault(s, set()).add(s)
    
    changed = True
    while changed:
        changed = False
        for nt in productions:
            for rhs in productions[nt]:
                all_nullable = True
                for s in rhs:
                    before = len(first[nt])
                    first[nt] |= (first.get(s, {s}) - {'ε'})
                    if 'ε' not in first.get(s, {s}):
                        all_nullable = False
                        break
                if all_nullable and 'ε' not in first[nt]:
                    first[nt].add('ε')
                    changed = True
    
    follow = {nt: set() for nt in productions}
    follow[start].add('$')
    changed = True
    while changed:
        changed = False
        for nt in productions:
            for rhs in productions[nt]:
                for i, s in enumerate(rhs):
                    if s in productions:
                        before = len(follow[s])
                        if i + 1 < len(rhs):
                            follow[s] |= (first.get(rhs[i+1], {rhs[i+1]}) - {'ε'})
                        if i + 1 == len(rhs) or 'ε' in first.get(rhs[i+1], set()):
                            follow[s] |= follow[nt]
                        if len(follow[s]) > before:
                            changed = True
    return first, follow

prods = {'E': [['T','E\'']], 'E\'': [['+','T','E\''], ['ε']]}
first, follow = compute_first_follow(prods, 'E')
print(f"FIRST(E)={first.get('E',set())}, FOLLOW(E)={follow['E']}")
```

## 关联页面

[[自顶向下LL1]] [[预测分析表]] [[递归下降]] [[上下文无关文法]]
