---
title: Rabin-Karp字符串匹配算法
course: 算法设计与分析
chapter: 第八章 字符串匹配
difficulty: INTERMEDIATE
tags: [Rabin-Karp, 字符串匹配, 哈希, 滚动哈希, 指纹算法]
aliases: [Rabin-Karp Algorithm, 滚动哈希, Rolling Hash]
source:
  - Cormen, Introduction to Algorithms (CLRS)
  - Karp & Rabin, Efficient Randomized Pattern-Matching Algorithms (1987)
updated_at: 2026-05-02

---

## 核心定义

Rabin-Karp 算法是一种基于哈希的字符串匹配算法。其核心思想是利用滚动哈希（Rolling Hash）技术，将文本中每个长度为 m 的窗口（m 为模式串长度）计算其哈希值，与模式串的哈希值进行比较；只有哈希值相等时才进行逐字符验证（避免哈希碰撞导致误判）。滚动哈希的关键在于能在 O(1) 时间内从当前窗口的哈希值计算下一个窗口的哈希值，无需重新计算：hash(txt[i+1..i+m]) = (d * (hash(txt[i..i+m-1]) - txt[i] * h) + txt[i+m]) mod q，其中 d 为基数（通常取字符集大小），q 为大质数（防止溢出和减少碰撞）。算法的平均时间复杂度为 O(n+m)，最坏情况（大量哈希碰撞）下退化到 O(nm)。Rabin-Karp 特别适合检测多模式串或抄袭检测场景（可为所有文本片段预先计算指纹）。

## 关键结论

- 滚动哈希公式：H[i+1] = ((H[i] - s[i] * h) * d + s[i+m]) mod q，其中 h = d^{m-1} mod q
- 选择大质数 q 可以显著降低哈希碰撞概率：q 越大碰撞越少，但过大可能导致溢出
- 时间复杂度：预处理哈希 O(m)，扫描匹配 O(n) 期望（每次哈希计算 O(1)），验证 O(m)（仅在碰撞时）
- 多模式匹配扩展：可将所有模式串的哈希值存入集合，一次扫描完成多个模式的匹配
- 应用场景：抄袭检测（将文档分割为 k-gram 并比较指纹集）、DNA 序列分析、文件去重

## 易错点

1. 滚动哈希公式中减去前导字符时的系数 h：h = d^{m-1} mod q，必须用取模后结果参与计算。
2. 负数的取模处理：在 Python/Java 等语言中负数取模的结果可能为负，需调整为正值：(result + q) % q。
3. 哈希碰撞后需要逐字符验证，不可跳过：不验证会导致误报（False Positive）。

## 例题

**例题1：** 文本 T="ABABCABAB", 模式 P="ABAB"。用 d=26, q=101 计算并模拟 Rabin-Karp 搜索过程。

**解答：** m=4。计算 hash(P) 和 h = 26^3 mod 101 = 17576 mod 101 = 0 + 17576...计算之后获得 hash(P)。滑窗计算各窗口 hash，相等的窗口为位置 0（ABAB）和位置 5（ABAB），进一步验证均为真匹配。

**例题2：** 分析 Rabin-Karp 的最坏情况。如何降低最坏概率？

**解答：** 最坏情况发生在所有窗口的哈希值都等于模式串的哈希值（哈希碰撞贯穿），导致每次都要逐字符验证，复杂度 O(nm)。例如模式全是 a，文本也全是 a。降低方法：增大 q（如使用 10^9+7 或更大的质数）、使用双哈希（对两个不同的质数同时进行哈希）。

## 代码示例

```python
def rabin_karp(text, pattern, d=256, q=101):
    """
    d: 字符集大小（ASCII 256）
    q: 大质数
    """
    n, m = len(text), len(pattern)
    if m > n:
        return []
    
    # 计算 h = d^{m-1} mod q
    h = 1
    for _ in range(m - 1):
        h = (h * d) % q
    
    # 计算模式串的哈希值和文本首个窗口的哈希值
    p_hash = 0
    t_hash = 0
    for i in range(m):
        p_hash = (d * p_hash + ord(pattern[i])) % q
        t_hash = (d * t_hash + ord(text[i])) % q
    
    matches = []
    for i in range(n - m + 1):
        # 哈希值相等，逐字符验证
        if p_hash == t_hash:
            if text[i:i + m] == pattern:
                matches.append(i)
        
        # 滑动窗口，计算下一个哈希值
        if i < n - m:
            t_hash = (d * (t_hash - ord(text[i]) * h) + ord(text[i + m])) % q
            if t_hash < 0:  # 处理负数取模
                t_hash += q
    
    return matches

# 多模式匹配版本
def rabin_karp_multi(text, patterns, d=256, q=101):
    """同时匹配多个模式串"""
    patterns_set = set(patterns)
    pattern_hashes = {}
    max_len = 0
    
    for p in patterns_set:
        if len(p) not in pattern_hashes:
            pattern_hashes[len(p)] = set()
        # 计算 p 的哈希值
        h = 0
        for ch in p:
            h = (d * h + ord(ch)) % q
        pattern_hashes[len(p)].add((h, p))
        max_len = max(max_len, len(p))
    
    results = {p: [] for p in patterns}
    # 对每种长度分别匹配
    for m, ph_set in pattern_hashes.items():
        if m > len(text):
            continue
        # ... 类似单模式匹配但检查集合
        h_val = 1  # 同上的滚动哈希匹配逻辑
        # (略去重复代码)
    
    return results

print(rabin_karp("ABABCABAB", "ABAB"))  # [0, 5]
```

## 关联页面

[[KMP算法]] [[Boyer-Moore算法]] [[字符串匹配概述]] [[哈希表]] [[滚动哈希]]
