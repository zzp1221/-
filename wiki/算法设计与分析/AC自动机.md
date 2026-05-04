---
title: "Aho-Corasick自动机"
course: 算法设计与分析
chapter: 字符串算法
difficulty: ADVANCED
tags: [算法, AC自动机, 多模式匹配, Trie, 自动机]
aliases: [Aho-Corasick Automaton]
source: "Efficient String Matching: An Aid to Bibliographic Search (Aho & Corasick 1975)"
updated_at: 2026-05-02
---

## 核心定义

AC自动机是Trie+KMP的结合，一次扫描文本找出所有模式串。构建：1.将模式串建Trie 2.BFS遍历Trie构建失败指针(fail link)=KMP的next数组在Trie上的推广：节点u的fail=v表示v的最长后缀在Trie中是u的后缀。匹配时若当前节点无对应字符的子节点，沿fail跳转到有该子节点处。每个节点的output存储以此为后缀的所有模式串。

## 关键结论

1. 构建O(总模式串长度)，匹配O(|text|+匹配数) 2. 应用：敏感词过滤、多模式搜索、DNA序列检索 3. 优化为Trie Graph：所有字符都有转移（无需while跳fail）

## 关联页面

[[字典树Trie]] [[KMP字符串匹配]] [[自动机理论]]
