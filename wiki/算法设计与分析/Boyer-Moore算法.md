---
title: Boyer-Moore字符串匹配算法
course: 算法设计与分析
chapter: 第八章 字符串匹配
difficulty: ADVANCED
tags: [Boyer-Moore, 字符串匹配, 坏字符规则, 好后缀规则, 跳跃]
aliases: [Boyer-Moore Algorithm, BM算法]
source:
  - Boyer & Moore, A Fast String Searching Algorithm (1977)
  - Cormen, Introduction to Algorithms (CLRS)
updated_at: 2026-05-02

---

## 核心定义

Boyer-Moore（BM）算法是实践中最高效的字符串匹配算法之一，尤其适合大字符集和较长模式串。其核心创新是从模式串的末尾向前匹配（从右向左比较），并利用两种启发式规则决定模式串的跳跃距离："坏字符规则"（Bad Character Rule）——当文本字符 c 与模式串当前位置字符不匹配时，将模式串向右滑动使得 c 与模式串中最右侧的相同字符对齐；"好后缀规则"（Good Suffix Rule）——当已经匹配的后缀子串（好后缀）在模式串其他地方也出现时，将模式串滑动与之前缀对齐。取两规则中滑动的较大值作为实际跳跃距离。BM 算法在最好情况下可达 O(n/m) 的时间复杂度（n 为文本长度，m 为模式长度），最坏情况 O(nm)（通过 Galil 优化可达线性），平均性能显著优于 KMP。

## 关键结论

- BM 算法从右向左匹配，利用匹配失败时已获得的信息计算最大跳跃距离
- 坏字符规则：Δ1[c] = m - 1 - max{j | P[j]=c}（c 不在模式中时 Δ1[c]=m）
- 好后缀规则：若好后缀 t 在模式中另一次出现（在更左侧），对齐它；否则找 t 的最长后缀也是模式前缀的情况
- BM-Horspool 简化版仅使用坏字符规则，实现更简单且实践中表现很好
- BM 算法被广泛应用于文本编辑器（如 GNU grep）和搜索引擎

## 易错点

1. 坏字符规则中若 c 的最右出现位置在当前失配位置的右侧，不能左移模式串，因此取 max(1, j - last(c))。
2. 好后缀规则需要预处理两个数组（suffix 和 prefix），实现比坏字符复杂得多。Horspool 和 Sunday 的简化算法在实践中更常见。
3. BM 算法的预处理 O(m + |Σ|)（坏字符表）和 O(m)（好后缀表），匹配阶段平均仅需 O(n/m) 次比较。

## 例题

**例题1：** 用 BM 算法在 T="HERE IS A SIMPLE EXAMPLE" 中搜索 P="EXAMPLE"。模拟坏字符规则的跳跃。

**解答：** 坏字符表（|Σ|=26简化，仅展示部分）：E=5, X=1, A=4, M=3, P=2, L=0。第一次对齐：T 中 'S' vs P 末 'E' 不匹配。S 不在 P 中，Δ1['S'] = 7，模式串跳 7 位。第二次对齐在正确位置附近...经过数次跳跃找到匹配。

**例题2：** 比较 KMP、BM、Sunday 算法在不同场景的优劣。

**解答：** KMP 稳定 O(n+m)，适合小字符集和重复模式；BM 实际中最快（大字符集、长模式），最坏 O(nm) 但实践中很少出现；Sunday 算法是 BM 的进一步简化，对随机文本效率极高。现代匹配引擎（如 grep）多采用 BM 或其变体。

## 代码示例

```python
def boyer_moore_horspool(text, pattern):
    """BM-Horspool 简化版，仅用坏字符规则"""
    n, m = len(text), len(pattern)
    if m == 0:
        return [0]
    if m > n:
        return []
    
    # 坏字符表：字符 -> 跳跃距离
    bad_char = {}
    for i in range(m - 1):
        bad_char[pattern[i]] = m - 1 - i
    
    matches = []
    i = 0
    while i <= n - m:
        j = m - 1
        while j >= 0 and text[i + j] == pattern[j]:
            j -= 1
        if j < 0:
            matches.append(i)
            i += 1  # 找到匹配后跳一步
        else:
            shift = bad_char.get(text[i + j], m)
            i += shift
    
    return matches

def boyer_moore_sunday(text, pattern):
    """Sunday 算法：检查窗口后一个字符"""
    n, m = len(text), len(pattern)
    if m == 0:
        return [0]
    if m > n:
        return []
    
    # 偏移表：字符在模式中最右出现位置距末尾的距离
    offset = {ch: m - i for i, ch in enumerate(pattern)}
    
    matches = []
    i = 0
    while i <= n - m:
        if text[i:i + m] == pattern:
            matches.append(i)
            i += 1
        else:
            if i + m >= n:
                break
            next_char = text[i + m]
            shift = offset.get(next_char, m + 1)
            i += shift
    
    return matches

# 坏字符规则的可视化
def build_bad_char_table(pattern):
    """构建完整的坏字符表"""
    m = len(pattern)
    # 对于字符集中的每个字符
    table = {}
    for i, ch in enumerate(pattern):
        table[ch] = max(1, m - 1 - i)
    return table

print(boyer_moore_horspool("HERE IS A SIMPLE EXAMPLE", "EXAMPLE"))  # [17]
print(boyer_moore_sunday("HERE IS A SIMPLE EXAMPLE", "EXAMPLE"))    # [17]
```

## 关联页面

[[KMP算法]] [[Rabin-Karp算法]] [[字符串匹配概述]] [[坏字符规则]]
