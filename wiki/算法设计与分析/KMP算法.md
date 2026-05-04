---
title: KMP字符串匹配算法
course: 算法设计与分析
chapter: 第八章 字符串匹配
difficulty: INTERMEDIATE
tags: [KMP, 字符串匹配, 前缀函数, 失配数组, 线性时间]
aliases: [Knuth-Morris-Pratt, KMP Algorithm, 前缀函数]
source:
  - Cormen, Introduction to Algorithms (CLRS)
  - Knuth, Morris & Pratt, Fast Pattern Matching in Strings (1977)
updated_at: 2026-05-02

---

## 核心定义

KMP（Knuth-Morris-Pratt）算法是一种线性时间的字符串匹配算法。其核心创新是利用已经部分匹配的信息避免在匹配失败时回溯文本指针。KMP 通过预处理模式串构建前缀函数（Prefix Function）π 数组，也称为 next 数组或失配函数（Failure Function）。π[i] 定义为模式串前缀 P[0..i] 中最长的真前缀同时也是真后缀的长度。在文本匹配过程中，当文本的字符与模式串当前字符不匹配时，根据 π 数组将模式串向右滑动（实际上是回退模式串指针 j = π[j-1]），而文本指针 i 永不回溯。算法分为两阶段：预处理阶段 O(m) 计算 π 数组；匹配阶段 O(n) 完成扫描。总时间复杂度 O(n+m)，空间复杂度 O(m)。

## 关键结论

- KMP 的文本指针绝不回退：这是它优于朴素算法的根本原因，适合处理流式数据
- 前缀函数 π 的计算本身也使用了 KMP 的思想（自我匹配）：用两个指针 i（扫描）和 j（当前最长前缀长度），在失配时 j = π[j-1]
- π 数组的几何意义：π[i] 是模式串前缀 P[0..i] 的 border（既是前缀又是后缀）的最长长度
- KMP 在字符集大且随机性强的场景下效率与朴素算法接近（很少失配），但在重复模式场景下优势明显
- KMP 扩展：Z 算法（Z-function）计算每个位置与整个字符串的 LCP，可用于更灵活的匹配

## 易错点

1. π[0] 恒为 0（单个字符的真前缀/真后缀为空串）。next 数组的索引从 0 还是 1 开始依赖于具体实现约定。
2. 失配回退时要用 π[j-1] 而非 π[j]：因为当前 j 位置已失配，应回到"前缀"的末尾。
3. 计算 π 数组时 i 从 1 开始（第二个字符），因为 π[0] 已知为 0。

## 例题

**例题1：** 模式串 P="ABABCABAB"，计算 π 数组。

**解答：** π[0]=0 (A)、π[1]=0 (AB无公共前后缀)、π[2]=1 (ABA 前后缀 A)、π[3]=2 (ABAB 前后缀 AB)、π[4]=0 (ABABC 无公共前后缀)、π[5]=1 (ABABCA 前后缀 A)、π[6]=2 (ABABCAB 前后缀 AB)、π[7]=3 (ABABCABA 前后缀 ABA)、π[8]=4 (ABABCABAB 前后缀 ABAB)。π = [0,0,1,2,0,1,2,3,4]。

**例题2：** 使用 KMP 在 T="ABABDABACDABABCABAB" 中搜索 P="ABABCABAB"。

**解答：** 预处理 P 得 π。匹配过程：i=0,j=0：T[0]=A=P[0], i=1,j=1; 持续匹配到 i=4,j=4：T[4]=D!=P[4]=C，失配，j=π[4-1]=π[3]=2（回退到 AB）。继续 i=4,j=2: T[4]=D!=P[2]=A，失配，j=π[1]=0。i=4,j=0 继续...最终在位置 10 处发现完全匹配。

## 代码示例

```python
def compute_prefix_function(pattern):
    """计算前缀函数 π O(m)"""
    m = len(pattern)
    pi = [0] * m
    j = 0  # 当前最长的前缀也是后缀的长度
    
    for i in range(1, m):
        while j > 0 and pattern[i] != pattern[j]:
            j = pi[j - 1]
        if pattern[i] == pattern[j]:
            j += 1
        pi[i] = j
    
    return pi

def kmp_search(text, pattern):
    """KMP 字符串匹配 O(n+m)"""
    n, m = len(text), len(pattern)
    if m == 0:
        return [0]
    
    pi = compute_prefix_function(pattern)
    matches = []
    j = 0  # 模式串指针
    
    for i in range(n):
        while j > 0 and text[i] != pattern[j]:
            j = pi[j - 1]  # 回退模式串指针
        if text[i] == pattern[j]:
            j += 1
        if j == m:  # 完全匹配
            matches.append(i - m + 1)
            j = pi[j - 1]  # 找下一个匹配
    
    return matches

def kmp_find_all_overlapping(text, pattern):
    """查找所有重叠匹配"""
    return kmp_search(text, pattern)

print(kmp_search("ABABDABACDABABCABAB", "ABABCABAB"))  # [10]
print(compute_prefix_function("ABABCABAB"))
# [0, 0, 1, 2, 0, 1, 2, 3, 4]
```

## 关联页面

[[Rabin-Karp算法]] [[Boyer-Moore算法]] [[字符串匹配概述]] [[前缀函数]] [[Z算法]]
