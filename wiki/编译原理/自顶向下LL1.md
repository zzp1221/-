---
title: 自顶向下LL(1)分析
course: 编译原理
chapter: 语法分析
difficulty: INTERMEDIATE
tags: [LL1, 自顶向下, 预测分析, 回溯, 左递归消除, 提取左公因子]
aliases: [LL(1) Parsing, Top-Down Parsing, 预测分析法]
source:
  - Alfred V. Aho《Compilers: Principles, Techniques, and Tools》(龙书)
updated_at: 2026-05-02
---

## 核心定义

LL(1) 分析是一种自顶向下（Top-Down）的确定性语法分析方法——从开始符号出发，自左向右扫描输入，每次根据**当前的一个输入符号**（Lookahead of 1）选择唯一的产生式进行推导。名称中第一个 L 表示从左到右扫描（Left-to-right），第二个 L 表示产生最左推导（Leftmost Derivation），括号中的 1 表示前瞻一个符号。

LL(1) 分析的可行性条件：文法必须是 LL(1) 文法——对任何非终结符 A 和其任意两条不同产生式 A → α | β，满足：(1) FIRST(α) ∩ FIRST(β) = ∅（首符集不相交）；(2) 若 ε ∈ FIRST(β)，则 FIRST(α) ∩ FOLLOW(A) = ∅。这两个条件保证分析器在任何时候都能根据当前输入符号唯一地选择产生式。

LL(1) 文法的预处理包括：(a) **消除左递归**：将 A → Aα | β 改写为 A → βA', A' → αA' | ε（直接左递归）；(b) **提取左公因子**（Left Factoring）：将 A → αβ₁ | αβ₂ 改写为 A → αA', A' → β₁ | β₂，避免因公共前缀导致的回溯。LL(1) 分析可以用递归下降（手写）或表驱动（自动生成）两种方式实现。预测分析表 M[A, a] 指示当栈顶为非终结符 A 且当前输入符号为 a 时应使用的产生式。

## 关键结论

- LL(1) 文法是 LL(k) 文法中最实用的子类——k=1 时兼顾了分析能力和实现复杂度
- 并非所有上下文无关文法都是 LL(1)（甚至有些确定性语言没有 LL(1) 文法），但大多数编程语言的语法可以被设计为 LL(1) 或接近 LL(1)
- 左递归文法是 LL(1) 分析的"杀手"——会导致无限递归，必须先行消除
- FIRST 集和 FOLLOW 集是 LL(1) 分析的核心数据结构，它们的计算是构造预测分析表的前提
- LL(1) 分析的优势：直观、易于手工实现（递归下降）、错误诊断信息友好
- LL(1) 的劣势：表达能力不如 LR(1)，某些自然语法结构需要重写才能适应

## 易错点

1. 仅消除了直接左递归而忽略了间接左递归：A → Bα, B → Aβ 也构成左递归，需系统性地查找和消除
2. 提取左公因子后忘记计算新非终结符的 FIRST/FOLLOW 集——这对构造最终的正确分析表至关重要
3. LL(1) 条件中对 ε-产生式的处理：不能仅仅检查 FIRST(α) ∩ FIRST(β)，必须考虑 ε 的情况

## 例题

**例题1**：判断文法 S → aS | bS | ε 是否为 LL(1)。

**解答**：FIRST(aS)={a}, FIRST(bS)={b}, FIRST(ε)={ε}。由于 ε ∈ FIRST(ε)，需检查 FOLLOW(S)={$} 与 FIRST(aS)={a} 和 FIRST(bS)={b} 的交集。{a}∩{$}=∅, {b}∩{$}=∅。各项条件满足，故该文法是 LL(1)。构造预测分析表：M[S,a]=S→aS, M[S,b]=S→bS, M[S,$]=S→ε。

**例题2**：消除左递归并提取左公因子：S → Aa | b, A → Ac | Sd | ε。

**解答**：先替换 S 到 A 中：A → Ac | Aad | bd | ε。消除 A 的直接左递归：A → bdA' | A', A' → cA' | adA' | ε。再将 S 中的 A 替换：S → Aa | b = (bdA' | A')a | b = bdA'a | A'a | b。最终文法无左递归且已提取左公因子，可构造预测分析表。

## 代码示例

```python
def compute_first(productions, symbol, first_cache={}):
    """计算FIRST集"""
    if symbol in first_cache:
        return first_cache[symbol]
    first = set()
    if symbol.islower() or symbol in '+-*()':
        first.add(symbol)
    else:
        for rhs in productions.get(symbol, []):
            if rhs[0] == 'ε':
                first.add('ε')
            else:
                for s in rhs:
                    f = compute_first(productions, s, first_cache)
                    first |= (f - {'ε'})
                    if 'ε' not in f:
                        break
                else:
                    first.add('ε')
    first_cache[symbol] = first
    return first

# 文法: E → TE', E' → +TE' | ε, T → FT', T' → *FT' | ε, F → (E) | id
prods = {'E': [['T','E\'']], 'E\'': [['+','T','E\''], ['ε']],
         'T': [['F','T\'']], 'T\'': [['*','F','T\''], ['ε']],
         'F': [['(','E',')'], ['id']]}
first_E = compute_first(prods, 'E')
print(f"FIRST(E) = {first_E}")  # {'(', 'id'}
```

## 关联页面

[[First-Follow]] [[递归下降]] [[预测分析表]] [[上下文无关文法]] [[自底向上LR0]]
