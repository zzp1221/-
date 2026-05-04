---
title: "LL与LR分析算法对比"
course: 编译原理
chapter: 语法分析
difficulty: ADVANCED
tags: [编译原理, LL, LR, 语法分析, 语法分析器]
aliases: [LL Parsing, LR Parsing]
source: "Compilers: Principles, Techniques, and Tools (Dragon Book) 第4章; Parsing Techniques (Grune & Jacobs)"
updated_at: 2026-05-02
---

## 核心定义

语法分析检查Token序列是否符合文法并构建语法树。LL(k)自上而下分析：从开始符号出发，每次根据下k个lookahead符号预测产生式。需消除左递归和提取左公因子。LL(1)计算FIRST/FOLLOW集合构建预测表。LR(k)自下而上分析：从输入Token开始，通过移进(shift)和归约(reduce)最终到达开始符号。LR项集族构造DFA，解决移进-归约冲突和归约-归约冲突。

## 关键结论

1. LL文法⊂LR文法（LR可以处理更多文法）2. LL手工构造方便(递归下降)，LR需生成器(YACC/Bison) 3. LR(0)→SLR→LR(1)→LALR(1)功能递增，LALR(1)是实用折中(YACC使用)

## 关联页面

[[语法分析概览]] [[语法树]] [[算符优先分析]]
