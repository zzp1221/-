---
title: "KMP字符串匹配算法"
course: 数据结构
chapter: 字符串
difficulty: INTERMEDIATE
tags: [数据结构, KMP, 字符串匹配, next数组]
aliases: [Knuth-Morris-Pratt Algorithm]
source: "Fast Pattern Matching in Strings (Knuth, Morris, Pratt 1977)"
updated_at: 2026-05-02
---

## 核心定义

KMP是线性时间的字符串匹配算法，O(n+m)。核心思想：利用部分匹配信息避免回退，构建next数组（失配时模式串应跳转的位置）。next[j]=k：在pattern[0..j-1]中，长度为k的前缀等于长度为k的后缀。匹配过程中主串指针i不回退，只移动模式串指针j。

## 关键结论

1. next数组的构建本身也是一个KMP匹配过程（模式串匹配自身）2. 优化的nextval可跳过相同字符的重复比较 3. BM和Sunday算法在实际中常数更优但最坏仍是O(nm)

## 代码示例

```python
def kmp(s, p):
    nxt = [0] * len(p)
    j = 0
    for i in range(1, len(p)):
        while j > 0 and p[i] != p[j]: j = nxt[j-1]
        if p[i] == p[j]: j += 1
        nxt[i] = j
    j = 0
    for i in range(len(s)):
        while j > 0 and s[i] != p[j]: j = nxt[j-1]
        if s[i] == p[j]: j += 1
        if j == len(p): return i - j + 1
    return -1
```

## 关联页面

[[字符串匹配算法对比]] [[文本检索]]
