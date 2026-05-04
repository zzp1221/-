---
title: "乘法器设计（Booth算法）"
course: 计算机组成原理
chapter: 运算器
difficulty: ADVANCED
tags: [计算机组成原理, 乘法器, Booth, 运算器, ALU]
aliases: [Booth's Algorithm]
source: "A Signed Binary Multiplication Technique (Booth 1951); Computer Organization and Design (Patterson & Hennessy)"
updated_at: 2026-05-02
---

## 核心定义

Booth算法是有符号二进制乘法的经典算法，利用1...10...0=2^(k+1)-2^m将连续的1替换为一次加法和一次减法。操作规则（取决于乘数当前位Qi和前一位Qi-1）：01→加被乘数；10→减被乘数；00/11→无操作。每次算术右移一位。标准Booth：n次移位+平均n/2次加减。Radix-4 Booth：每次检查3位，n/2次移位。

## 关键结论

1. 现代CPU用Wallace Tree+Booth编码的混合乘法器 2. Radix-4 Booth将部分积数量减半 3. Wallace Tree将部分积求和从O(n²)降到O(log n)

## 关联页面

[[加法器]] [[算术逻辑单元ALU]] [[IEEE754浮点数标准]]
