---
title: "DFA最小化（Hopcroft算法）"
course: 编译原理
chapter: 词法分析
difficulty: ADVANCED
tags: [编译原理, DFA, 最小化, Hopcroft, 等价类]
aliases: [DFA Minimization]
source: "Compilers: Principles, Techniques, and Tools (Dragon Book) 第3章"
updated_at: 2026-05-02
---

## 核心定义

DFA最小化将状态划分为等价类(equivalent states)——两个状态不等价若存在某输入使转移结果在不同等价类。Hopcroft算法O(n log n)：维护当前划分，迭代选择最小组分裂——对每个输入字符检查某等价类内的状态是否一致转出到相同等价类。Myhill-Nerode定理：最小DFA的状态数=L的等价类数。最小化保证得到唯一最小的DFA。

## 关键结论

1. 最小DFA大小=语言在Myhill-Nerode等价关系下的指数 2. Hopcroft算法迭代式优化，Moore算法更直观但O(n²) 3. DFA最小化后正则表达式引擎的词法token生成效率更高

## 关联页面

[[词法分析与DFA]] [[正则语言与泵引理]]
