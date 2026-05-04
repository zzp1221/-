---
title: LR(1)与LALR(1)分析
course: 编译原理
chapter: 语法分析
difficulty: ADVANCED
tags: [LR(1), LALR(1), 规范LR, 前瞻LR, 向前看符号, 同心项集]
aliases: [Canonical LR(1), Lookahead LR(1), LALR]
source:
  - Alfred V. Aho《Compilers: Principles, Techniques, and Tools》(龙书)
updated_at: 2026-05-02

---

## 核心定义

**LR(1)**（规范 LR）是最强大的确定型自底向上分析方法。与 LR(0)/SLR(1) 不同，LR(1) 项带有一个**前瞻符号**（Lookahead）：形如 [A → α·β, a]，其中 a 是一个终结符（或 $），表示仅当后面的输入符号为 a 时，才可沿该产生式进行归约。LR(1) 的 CLOSURE 运算：若 [A → α·Bβ, a] 在项集中，则对 B 的每个产生式 B → γ 和每个 b ∈ FIRST(βa)，将 [B → ·γ, b] 加入闭包。LR(1) 项集规范族的构造通过反复闭包和 GOTO 实现。LR(1) 分析能力是 LR 族中最强的——任何确定型上下文无关语言都存在 LR(1) 文法。

**LALR(1)**（Lookahead-LR）是 LR(1) 的实用折中方案：将 LR(1) 项集规范族中具有**相同核心项**（Core Items，即忽略前瞻符号的项）的状态合并，从而大幅减少状态数量（与 SLR(1) 的状态数相同级别），同时保持比 SLR(1) 更强的分析能力。LALR(1) 是 YACC/Bison 默认使用的分析方法。

LR(1) vs LALR(1) vs SLR(1) 的分析能力排序：LR(1) > LALR(1) > SLR(1)。LALR(1) 的缺点在于合并同心项集可能引入**归约-归约冲突**（但绝不会引入移进-归约冲突）。

## 关键结论

- LR(1) 是规范 LR 分析：状态数可能非常多（对 Pascal 级别语言可达几千），实际编译器中很少直接使用
- LALR(1) 合并同心项集后状态数与 SLR(1) 相同但分析能力更强——是实用编译器的标准选择
- 任何 SLR(1) 文法也是 LALR(1) 文法；任何 LALR(1) 文法也是 LR(1) 文法
- LR(1) / LALR(1) 的构造都是 ALR 分析表自动生成工具（如 YACC）的基础
- LR(1) 项中的前瞻符号解决了 SLR(1) 中 FOLLOW 集过于粗糙导致的冲突
- LALR(1) 合并同心集不会引入移进-归约冲突：若合并后有移进-归约冲突，合并前必然已存在

## 易错点

1. LR(1) 闭包计算中前瞻符号的传播：FIRST(βa) 是多符号串的首符集，计算时需注意 a 是单个终结符
2. LALR(1) 合并不是简单的状态合并——需正确合并前瞻符号的并集，前瞻符号的冲突可能导致归约-归约冲突
3. 混淆"同心"（Same Core）的概念：核心项不包括前瞻符号——两个 LR(1) 状态同心当它们的核心项集合完全相同

## 例题

**例题1**：比较 LR(0), SLR(1), LR(1), LALR(1) 对以下文法的接受能力：S → aSb | ab。

**解答**：增广后 S'→S。该文法实际上是 LL(1) 的，也是 SLR(1) 的。构造 LR(0) 可能有冲突但 FOLLOW(S)={b,$} 可解决——SLR(1) 接受。LALR(1) 和 LR(1) 自然也接受。展示了一个所有 LR 变体都能接受的简单文法。

**例题2**：构造增广文法 S'→S, S→L=R | R, L→*R | id, R→L 的 LR(1) 项集并指出与 LALR(1) 的差异。

**解答**：此文法不是 SLR(1)（因为有 FOLLOW(R) 导致冲突），但 LR(1) 可以分析。LR(1) 的状态数多于 LALR(1)。合并同心集后（如核心为 {L→*·R, R→·L} 的状态），将两个 LR(1) 状态的前瞻符号分别合并。在此例中 LALR(1) 未引入新的冲突，故该文法是 LALR(1) 的。

## 代码示例

```python
# LALR(1) 的核心：通过先构造 LR(1) 项集再合并同心集
def lalr1_core_merge(lr1_states):
    """合并具有相同核心项的LR(1)状态"""
    core_to_merged = {}
    for state_id, items in enumerate(lr1_states):
        # 核心项: 忽略前瞻符号
        core = frozenset((lhs, tuple(rhs), dot) 
                         for (lhs, rhs, dot, _) in items)
        if core in core_to_merged:
            # 合并前瞻符号
            existing = core_to_merged[core]
            for item in items:
                lhs, rhs, dot, la = item
                existing.setdefault((lhs, tuple(rhs), dot), set()).add(la)
        else:
            core_to_merged[core] = {}
            for item in items:
                lhs, rhs, dot, la = item
                core_to_merged[core][(lhs, tuple(rhs), dot)] = {la}
    return core_to_merged

# 演示：两个不同LR(1)状态但同心核心的合并
print("LALR(1)合并同心项集: 状态数减少，分析能力接近LR(1)")
```

## 关联页面

[[自底向上LR0与SLR1]] [[YACC]] [[推导与归约与语法树]] [[编译概述]]
