---
title: LR(0)与SLR(1)分析
course: 编译原理
chapter: 语法分析
difficulty: ADVANCED
tags: [LR(0), SLR(1), 自底向上, 移进-归约, LR项, 项目集规范族, 分析表]
aliases: [LR(0) Parsing, SLR(1) Parsing, 简单LR分析]
source:
  - Alfred V. Aho《Compilers: Principles, Techniques, and Tools》(龙书)
updated_at: 2026-05-02

---

## 核心定义

LR 分析是一类自底向上（Bottom-Up）语法分析方法——从输入串出发，逐步归约（Reduction）文法符号直到抵达开始符号。LR(0) 和 SLR(1) 是其两个早期变体。核心数据结构为 **LR 项**（LR Item）：一个产生式加上一个点号 `·` 标记当前分析进度。A → α·β 表示已看到 α，期望接下来看到 β。

**LR(0) 自动机**的构造：(1) 增广文法：添加 S' → S 作为新的开始产生式；(2) CLOSURE(I) 函数：若 A → α·Bβ 在 I 中，则对 B 的每个产生式 B → γ，将 B → ·γ 加入 I；(3) GOTO(I, X) 函数：CLOSURE({A → αX·β | A → α·Xβ ∈ I})。从初始项 S' → ·S 出发，反复应用 CLOSURE 和 GOTO，生成所有 LR(0) 项集，即**项目集规范族**（Canonical Collection of LR(0) Items）。

**LR(0) 分析表** 由 ACTION 和 GOTO 两部分组成。对每个状态（项集）Iᵢ：(a) 若 A → α·aβ ∈ Iᵢ 且 GOTO(Iᵢ, a) = Iⱼ，则 ACTION[i, a] = "sj"（移进到状态 j）；(b) 若 A → α· ∈ Iᵢ，则对所有终结符 a，ACTION[i, a] = "rj"（按产生式 j 归约）；(c) 若 S' → S· ∈ Iᵢ，则 ACTION[i, $] = "acc"（接受）。

**SLR(1)** 改进了 LR(0) 的归约策略：归约项 A → α· 只在 FOLLOW(A) 中的终结符上触发归约——这样减少了 LR(0) 中频繁的移进-归约冲突。

## 关键结论

- LR(0) 分析能力最弱：几乎任何有用文法都会产生移进-归约冲突或归约-归约冲突
- SLR(1) 利用 FOLLOW 集改进了 LR(0) 的归约策略，比 LR(0) 强但不如 LR(1)
- LR(0) 项集的构造是确定性有穷自动机（识别活前缀的 DFA）
- 活前缀（Viable Prefix）是从开始符号推出的句型中不超过句柄右端的任意前缀
- 移进-归约冲突：同一状态同时要求移进和归约；归约-归约冲突：同一状态可归约为两个不同的非终结符
- SLR(1) 文法是 LR(0) 文法的真超类——许多有用语法是 SLR(1) 但不是 LR(0)

## 易错点

1. LR(0) 项在闭包计算时忘记迭代：CLOSURE 需反复添加直到不再扩展——单次扫描不够
2. SLR(1) 构造时将归约项应用于所有终结符（与 LR(0) 一样）而非仅 FOLLOW 集——这是 LR(0) 分析表而非 SLR(1)
3. 误以为 LR(0) 能分析常见编程语言：几乎所有有用文法都需要 SLR(1) 或更强的分析器

## 例题

**例题1**：为增广文法 S'→S, S→(S)S | ε 构造 LR(0) 项集规范族。

**解答**：I₀ = CLOSURE({S'→·S}) = {S'→·S, S→·(S)S, S→·ε} 即 {S'→·S, S→·(S)S, S→ε·}（注意 S→·ε 即 S→ε·）。GOTO(I₀, S)=I₁={S'→S·}, GOTO(I₀, '(')=I₂={S→(·S)S, S→·(S)S, S→·ε}, ... 最终共有若干状态。

**例题2**：比较 LR(0) 与 SLR(1) 在文法 E → E+T | T, T → id 上的分析能力差异。

**解答**：增广：E'→E。I₀={E'→·E, E→·E+T, E→·T, T→·id}。GOTO(I₀, id)产生状态含 T→id·。在该状态，LR(0) 对所有输入符号均执行归约 T→id（产生归约-移进冲突若其他项要求移进）。SLR(1) 只对 FOLLOW(T)={+ , $} 执行归约，避免了冲突。此文法恰是 SLR(1) 可接受的。

## 代码示例

```python
def closure(items, productions):
    """计算LR(0)项的闭包"""
    changed = True
    while changed:
        changed = False
        new_items = set(items)
        for lhs, rhs, dot in items:
            if dot < len(rhs) and rhs[dot].isupper():
                B = rhs[dot]
                for prod_rhs in productions.get(B, []):
                    item = (B, tuple(prod_rhs), 0)
                    if item not in new_items:
                        new_items.add(item)
                        changed = True
        items = new_items
    return frozenset(items)

# 增广文法: S' -> S, S -> (S)S | ε
prods = {'S\'': [['S']], 'S': [['(', 'S', ')', 'S'], ['ε']]}
start_items = closure({('S\'', ('S',), 0)}, prods)
print(f"I₀ 项数: {len(start_items)}")
```

## 关联页面

[[LR1与LALR1]] [[YACC]] [[推导与归约与语法树]] [[自顶向下LL1]]
