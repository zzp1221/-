---
title: "字典树（Trie）"
course: 数据结构
chapter: 字符串
difficulty: INTERMEDIATE
tags: [数据结构, Trie, 字典树, 前缀树, 自动补全]
aliases: [Prefix Tree]
source: "Algorithms on Strings, Trees, and Sequences (Gusfield); 算法导论"
updated_at: 2026-05-02
---

## 核心定义

Trie（字典树/前缀树）是用于存储字符串集合的树形结构。每个节点代表一个字符串前缀，边代表添加一个字符。根节点为空串。插入和查找O(L)（L为字符串长度）。应用：自动补全、IP路由（最长前缀匹配）、拼写检查、词频统计。压缩Trie：合并单子节点路径减少节点数。AC自动机：KMP+Trie多模式匹配。

## 关键结论

1. 空间换时间，节点数可到O(总字符数) 2. 孩子表示法用哈希表(灵活)或定长数组(快但费空间) 3. 基数树(Radix Tree)合并单子节点节省空间 4. 双数组Trie在中文分词中广泛使用

## 关联页面

[[哈希表-开放定址法]] [[字符串匹配]] [[自动机理论]]
