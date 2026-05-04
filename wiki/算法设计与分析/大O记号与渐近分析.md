---
title: 大O记号与渐近分析
course: 算法设计与分析
chapter: 第一章 算法基础
difficulty: INTERMEDIATE
tags: [大O记号, 渐近分析, 渐近上界, 渐近下界, 紧确界, 增长率]
aliases: [Big-O Notation, Asymptotic Analysis, Big-Theta, Big-Omega]
source:
  - Cormen, Introduction to Algorithms (CLRS)
updated_at: 2026-05-02
---

## 核心定义

渐近分析（Asymptotic Analysis）是研究当输入规模n趋向无穷大时算法性能变化趋势的数学方法。渐近分析的核心工具包括三种渐近记号：大O记号（Big-O）表示渐近上界（Upper Bound），即存在正常数c和n0，使得对所有n >= n0，有0 <= f(n) <= c*g(n)，表示算法在最坏情况下不超过某个增长率；大Ω记号（Big-Omega）表示渐近下界（Lower Bound），即存在正常数c和n0，使得对所有n >= n0，有0 <= c*g(n) <= f(n)，表示算法至少需要某个增长率；大Θ记号（Big-Theta）表示渐近紧确界（Tight Bound），当且仅当f(n)=O(g(n))且f(n)=Ω(g(n))时成立，表示算法性能严格地以g(n)的速率增长。此外还有小o记号（严格上界）和小ω记号（严格下界），它们在极限理论中与微积分中的极限概念紧密对应。

## 关键结论

- 渐近分析忽略常数因子和低阶项，仅关注增长率的主导项，这使分析大大简化
- 多项式函数的渐近界由其最高次项决定：例如 f(n) = 3n^3 + 2n^2 + n + 1 的渐近界为 Θ(n^3)
- 极限比较法：若 lim_{n->∞} f(n)/g(n) = c（c为常数且c>0），则 f(n) = Θ(g(n))
- 斯特林公式（Stirling's Formula）在分析阶乘相关复杂度时极为重要：n! ~ sqrt(2πn) * (n/e)^n，log(n!) = Θ(n log n)
- 对数换底公式在不改变渐近阶的前提下发挥作用：log_a(n) = log_b(n) / log_b(a)，故任何底数的对数都属于 Θ(log n)

## 易错点

1. 混淆大O和大Θ：大O只需证明上界，大Θ需要同时证明上下界。面试中提到的"大O"有时实际上是"大Θ"的含义，需要语境判断。
2. 以为O(f(n))和Ω(f(n))是传递关系：实际上不存在所有函数g(n)使得g(n)=Ω(f(n))成立的情况。
3. 忽略极限考察：有些函数不能直接判断大小关系，如 n^{1+sin n} 的振荡行为使得它在O(n^2)和Ω(1)之间反复波动，没有简单的渐近界。

## 例题

**例题1：** 证明 n log n = O(n^2)，但 n^2 != O(n log n)。

**解答：** 前半部分：取 n0 = 1, c = 1，则对 n >= 1，n log n <= n * n = n^2，故 n log n = O(n^2)。后半部分：反证法。假设存在 c, n0 使得 n^2 <= c * n log n 对足够大的n成立，即 n <= c log n。但 lim_{n->∞} n/log n = ∞，矛盾。

**例题2：** 使用极限法比较 f(n) = 2^n 和 g(n) = n^{100} 的渐近增长率。

**解答：** lim_{n->∞} 2^n / n^{100} = ∞（使用L'Hopital法则100次或直接利用指数函数增长率高于任何多项式的事实），故 n^{100} = O(2^n)，即2^n的增长速度远高于任何多项式。

## 代码示例

```python
# 比较不同复杂度在实际运行中的表现
import time
import math

def compare_complexities():
    """测试不同规模下各复杂度函数的运行趋势"""
    sizes = [10, 100, 1000, 10000]
    
    print("验证渐近分析:")
    for n in sizes:
        # 模拟 O(log n) 操作
        log_ops = int(math.log2(n))
        # 模拟 O(n) 操作
        linear_ops = n
        # 模拟 O(n^2) 操作
        quadratic_ops = n * n
        
        print(f"n={n}: log_n={log_ops}, n={linear_ops}, n^2={quadratic_ops}")
    
    # 渐近分析的核心：比较增长率
    print("\n增长率对比（高/低）：")
    n = 10000
    print(f"n^2 / n = {n}")        # 10000倍差距
    print(f"n / log(n) = {n / math.log2(n):.0f}")  # 约750倍差距

# 极限比较法实践
def limit_comparison(f_vals, g_vals):
    """给定两个数组（分别代表f(n)和g(n)在不同n下的值），观察比值趋势"""
    ratios = [f/g for f, g in zip(f_vals, g_vals)]
    return ratios

compare_complexities()
```

## 关联页面

[[算法概述]] [[时间复杂度分析]] [[空间复杂度分析]] [[递归式求解]] [[主定理]]
