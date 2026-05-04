---
title: "字符串哈希与Rabin-Karp算法"
course: 算法设计与分析
chapter: 字符串算法
difficulty: INTERMEDIATE
tags: [算法, 字符串哈希, Rabin-Karp, 滚动哈希]
aliases: [Rabin-Karp Algorithm]
source: "Introduction to Algorithms (CLRS) 第32章"
updated_at: 2026-05-02
---

## 核心定义

Rabin-Karp使用滚动哈希高效匹配字符串。核心：hash(T[i...i+m-1])可在O(1)从上一个哈希值计算（减去旧字符贡献+加上新字符贡献）。典型哈希：∑t[i]·B^(m-1-i) mod M，其中B为基数(如256/131)，M为大质数。双哈希(double hash)或更大M避免哈希碰撞。平均O(n+m)，最坏O(nm)（需验证碰撞）。用于多模式串匹配、检测字符串相似性和子串判重。

## 关键结论

1. 滚动哈希预处理前缀哈希后O(1)求任意子串哈希 2. 自然溢出(unsigned long long)相当于mod 2^64，可能被卡 3. 双哈希(B1=131,M1=1e9+7,B2=13331,M2=1e9+9)安全性高

## 关联页面

[[KMP字符串匹配]] [[哈希冲突解决]]
