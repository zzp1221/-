---
title: "词法分析与自动机"
course: 编译原理
chapter: 词法分析
difficulty: INTERMEDIATE
tags: [编译原理, 词法分析, DFA, NFA, 正则]
aliases: [Lexical Analysis, DFA]
source: "Compilers: Principles, Techniques, and Tools (Dragon Book) 第3章"
updated_at: 2026-05-02
---

## 核心定义

词法分析将字符序列转换为Token序列。正则表达式→NFA(Thompson构造法)→DFA(子集构造法)→最小化DFA(Hopcroft算法)。Token结构：<类型, 属性值>。DFA模拟：根据当前状态和输入字符查转移表，接受状态识别Token。最大匹配(Maximal Munch)：尽量匹配最长Token。Flex/Lex是基于DFA的词法生成器。

## 关键结论

1. NFA→DFA态射可能引起指数爆炸(理论上2^n，实际通常多项式) 2. DFA最小化确保每个等价状态类合并(唯一最小DFA) 3. 超前搜索(lookahead)解决关键字vs标识符歧义

## 关联页面

[[正则语言与泵引理]] [[有限自动机]] [[语法分析]]
