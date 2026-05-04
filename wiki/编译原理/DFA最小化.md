---
title: DFA最小化
course: 编译原理
chapter: 词法分析
difficulty: INTERMEDIATE
tags: [DFA最小化, Hopcroft算法, Moore算法, 等价状态, 状态合并, Myhill-Nerode]
aliases: [DFA Minimization, 最小化DFA, DFA化简]
source:
  - Alfred V. Aho《Compilers: Principles, Techniques, and Tools》(龙书)
updated_at: 2026-05-02
---

## 核心定义

DFA 最小化（DFA Minimization）是将给定的 DFA 转化为等价的状态数最少的 DFA 的过程。两个状态 p 和 q 称为**等价**（Equivalent）当且仅当对所有输入串 w，δ*(p,w)∈F ⇔ δ*(q,w)∈F——即从 p 和 q 出发无法被任何串区分。DFA 最小化的核心思想是将等价状态合并。对于任何正则语言，其最小 DFA 在同构意义下是**唯一**的，且最小 DFA 的状态数恰好等于该语言的 Myhill-Nerode 等价类的个数。

主要算法包括：
- **Moore 算法**（O(n²)）：从接受/非接受状态的初始划分开始，迭代地细化划分：若同一划分块中的两个状态在某个输入符号下转移到不同划分块，则必须分开。
- **Hopcroft 算法**（O(n log n)）：是 Moore 算法的优化，通过始终选择较小的划分块进行拆分来减少不必要的检查。

最小化步骤：(1) 移除不可达状态；(2) 将剩余状态划分为等价类（初始分为 F 和 Q\F 两类）；(3) 迭代细化直到划分稳定；(4) 每个等价类合并为一个状态，构建最小 DFA。

## 关键结论

- DFA 最小化的理论基础是 Myhill-Nerode 定理：L 是正则语言当且仅当 L 仅有有限多个等价类，且最小 DFA 的状态数与等价类一一对应
- 初始划分（Π₀={F, Q\F}）是关键：接受状态和非接受状态必须分开——这是最粗糙的划分
- 划分细化的终止条件：当某轮迭代后划分不再改变，即达到最细划分（即等价类）
- Hopcroft 算法是历史上第一个 O(n log n) 的最小化算法，本质使用"分割者-接收者"策略
- 最小化后的 DFA 状态数可能远小于原 DFA，也排除了隐性等价和冗余状态
- 不可达状态（从初始状态无法到达的状态）应先移除，避免干扰最小化过程

## 易错点

1. 初始划分的错误：只分了 F（接受）和 Q\F（非接受）两类，但忘记先移除不可达状态
2. 细化条件不完整：对于同一划分块中的 p, q，若存在符号 a 使 δ(p,a) 和 δ(q,a) 落在不同的当前划分块中，则 p 和 q 必须分开
3. 忘记"等价类代表"的唯一性：合并后选择代表状态时需保持转移的一致性

## 例题

**例题1**：最小化 DFA: Q={A,B,C,D,E,F}, Σ={0,1}, 初始 A, F={C,D,E}。转移表：δ(A,0)=B,δ(A,1)=C;δ(B,0)=A,δ(B,1)=D;δ(C,0)=E,δ(C,1)=F;δ(D,0)=E,δ(D,1)=F;δ(E,0)=E,δ(E,1)=F;δ(F,0)=F,δ(F,1)=F。

**解答**：Π₀ = {C,D,E}, {A,B,F}。分析 {A,B,F} 在输入 0: A→B(∈第二类), B→A(∈第二类), F→F(∈第二类)，无法区分。在输入 1: A→C(∈第一类), B→D(∈第一类), F→F(∈第二类)，A 和 B 转到第一类、F 转到第二类，故 {A,B,F} 被分为 {A,B} 和 {F}。Π₁ = {C,D,E}, {A,B}, {F}。继续分析 {A,B}：输入 0 分别到 B,A（均在 {A,B}），输入 1 分别到 C,D（均在 {C,D,E}），无法区分。{C,D,E}：输入 0 全部到 E（同），输入 1 全部到 F（同），无法区分。Π₁ 稳定。

合并后最小 DFA 状态：S1={A,B}（初始）, S2={C,D,E}（接受）, S3={F}（非接受死状态）。3 个状态。

## 代码示例

```python
def moore_minimization(states, alphabet, transitions, start, accepts):
    """Moore算法最小化DFA"""
    # 移除不可达状态
    reachable = {start}
    queue = [start]
    while queue:
        s = queue.pop(0)
        for a in alphabet:
            t = transitions.get((s, a))
            if t and t not in reachable:
                reachable.add(t)
                queue.append(t)
    
    # 初始划分: 接受 vs 非接受
    partition = [accepts & reachable, reachable - accepts]
    partition = [p for p in partition if p]  # 去空
    
    # 迭代细化
    changed = True
    while changed:
        changed = False
        new_partition = []
        for block in partition:
            if len(block) <= 1:
                new_partition.append(block)
                continue
            # 按转移目标所在的分块分组
            groups = {}
            for state in sorted(block):
                signature = tuple(
                    next((i for i, p in enumerate(partition) 
                          if transitions.get((state, a)) in p), -1)
                    for a in alphabet
                )
                groups.setdefault(signature, set()).add(state)
            new_partition.extend(groups.values())
            if len(groups) > 1:
                changed = True
        partition = new_partition
    
    return [{min(b): b} for b in partition]  # 返回等价类
```

## 关联页面

[[DFA]] [[NFA转DFA]] [[词法分析]] [[正规式与正规文法]]
