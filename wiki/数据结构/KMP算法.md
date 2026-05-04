---
title: KMP算法
course: 数据结构
chapter: 串
difficulty: ADVANCED
tags: [字符串匹配, KMP, next数组, 模式匹配, 前缀函数]
aliases: [Knuth-Morris-Pratt Algorithm, KMP String Matching]
source:
  - Knuth, Morris, Pratt 论文 (1977)
  - 《算法导论》
updated_at: 2026-05-02
---

## 核心定义

KMP（Knuth-Morris-Pratt）算法是一种高效的字符串模式匹配算法。它由 Donald Knuth、Vaughan Pratt 和 James Morris 于 1977 年共同发表。KMP 算法的核心思想是：当匹配过程中发生失配时，利用已经匹配成功的部分信息，将模式串向右滑动尽可能远的距离，而不是暴力算法那样每次只移动一位。这个"滑动信息"通过预处理模式串得到的 next 数组（也叫前缀函数或失败函数）来提供。next[j] 表示当模式串中第 j 个字符与主串失配时，模式串应该跳到的下一个比较位置。KMP 算法的时间复杂度为 O(n+m)，其中 n 为主串长度，m 为模式串长度，对比暴力算法的 O(n*m) 有显著提升。

## 关键结论

- KMP 的核心是 next 数组：next[j] = k 表示在 j 处失配时，模式串指针回退到 k（k 是满足最长公共前后缀的值）
- next 数组的计算也是通过 KMP 思想自身匹配自己来完成，时间复杂度 O(m)
- 整个匹配过程主串指针 i 从不回溯，只有模式串指针 j 根据 next 数组回溯
- KMP 的理论时间复杂度为 O(n+m)，空间复杂度为 O(m)
- 改进的 nextval 数组可以进一步优化（当 P[j] == P[next[j]] 时跳过无效回溯）

## 易错点

1. next 数组的首元素设置：通常 next[0] = -1（表示模式串第一个字符就不匹配，需要主串指针 i 前移）；也有教材定义 next[1] = 0，需要注意下标的起始约定
2. 求 next 数组时的双指针技巧：需要理解用 k 追踪当前最长前缀，j 为当前处理字符；当 P[k] != P[j] 时 k = next[k]
3. 匹配过程中 i 不动，j 回溯：暴力匹配是 i = i - j + 2（回溯很多），KMP 中 i 保持不变，只调整 j，这是理解 KMP 效率的关键

## 例题

**例1：** 对模式串 "abaabcac"，求其 next 数组（从 next[0] = -1 开始）。

**解答：** 计算过程：j=0,-1; j=1,next[1]=0; j=2,P[0]=P[1]? a!=b, next[2]=0; j=3,P[0]!=P[2], next[3]=0; j=4,P[3]==P[0]=a, next[4]=1; j=5,P[4]==P[1]=b, next[5]=2; j=6,P[5]==P[2]? c!=a, k=next[2]=0, P[5]!=P[0], next[6]=0; j=7,P[6]==P[0]=a, next[7]=1。结果：[-1, 0, 0, 0, 1, 2, 0, 1]。

## 代码示例

```cpp
#include <iostream>
#include <string>
#include <vector>
using namespace std;

// 求 next 数组
vector<int> getNext(const string& pattern) {
    int m = pattern.size();
    vector<int> next(m);
    next[0] = -1;
    int j = 0, k = -1;
    while (j < m - 1) {
        if (k == -1 || pattern[j] == pattern[k]) {
            j++; k++;
            // 普通 KMP
            // next[j] = k;
            // 改进版：如果 P[j] == P[next[j]]，则跳过无效比较
            if (pattern[j] != pattern[k])
                next[j] = k;
            else
                next[j] = next[k];
        } else {
            k = next[k];
        }
    }
    return next;
}

// KMP 匹配，返回所有匹配位置
vector<int> kmpSearch(const string& text, const string& pattern) {
    vector<int> result;
    vector<int> next = getNext(pattern);
    int i = 0, j = 0;
    int n = text.size(), m = pattern.size();
    while (i < n) {
        if (j == -1 || text[i] == pattern[j]) {
            i++; j++;
        } else {
            j = next[j];
        }
        if (j == m) {
            result.push_back(i - m);  // 匹配成功的位置
            j = next[j - 1];  // 继续找下一个匹配（可选的）
            i--;  // 因为循环会 i++
        }
    }
    return result;
}
```

```java
public class KMP {
    public static int[] getNext(String pattern) {
        int m = pattern.length();
        int[] next = new int[m];
        next[0] = -1;
        int j = 0, k = -1;
        while (j < m - 1) {
            if (k == -1 || pattern.charAt(j) == pattern.charAt(k)) {
                j++; k++;
                next[j] = (pattern.charAt(j) != pattern.charAt(k)) ? k : next[k];
            } else {
                k = next[k];
            }
        }
        return next;
    }
    
    public static List<Integer> kmpSearch(String text, String pattern) {
        List<Integer> res = new ArrayList<>();
        int[] next = getNext(pattern);
        int i = 0, j = 0, n = text.length(), m = pattern.length();
        while (i < n) {
            if (j == -1 || text.charAt(i) == pattern.charAt(j)) {
                i++; j++;
            } else {
                j = next[j];
            }
            if (j == m) {
                res.add(i - m);
                j = next[j - 1]; i--;
            }
        }
        return res;
    }
}
```

## 关联页面

[[字符串]] [[哈希表]] [[顺序表]] [[链表]]
