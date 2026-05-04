---
title: n皇后问题
course: 算法设计与分析
chapter: 第五章 回溯法与分支限界
difficulty: INTERMEDIATE
tags: [n皇后, 回溯法, 约束满足, 排列树, 剪枝]
aliases: [N-Queens, 八皇后问题, Eight Queens]
source:
  - Golomb & Baumert, Backtrack Programming (1965)
  - Cormen, Introduction to Algorithms (CLRS)
updated_at: 2026-05-02
---

## 核心定义

n皇后问题是回溯法的经典例题：在 n x n 的国际象棋棋盘上放置 n 个皇后，要求任意两个皇后不能在同行、同列或同一对角线（主对角线和副对角线）上，求所有合法的放置方案。该问题是约束满足问题（Constraint Satisfaction Problem, CSP）的典型代表。使用回溯法，按行依次放置皇后，对每一行枚举所有可能的列位置，通过约束检查剪枝不可行的分支。问题的解空间为排列树，最坏情况理论上有 n! 种可能，但通过高效的约束检查（使用辅助布尔数组记录列和对角线的占用状态，O(1) 时间检查冲突），回溯法在实践中可以高效求解。n皇后问题也是并行回溯算法的经典测试案例。

## 关键结论

- 解空间为排列树：第 i 行有 n 种选择，第 2 行约 n-1 种，总排列数 O(n!)
- 冲突检查优化：使用三个布尔数组（列、主对角线、副对角线）可在 O(1) 时间内完成冲突检查
- 主对角线索引：row - col + n - 1（范围 0 ~ 2n-2）；副对角线索引：row + col（范围 0 ~ 2n-2）
- 只有 n=1 和 n>=4 时有解：n=2 和 n=3 无解
- n皇后问题的解数随 n 增长极快：n=8 有 92 解，n=15 约有 227 万解

## 易错点

1. 对角线冲突的判断公式易写错：主对角线是 row-col 常数（任意行col差相同则同对角线），副对角线是 row+col 常数。
2. 三维皇后/超级皇后扩展混淆：n皇后变体包括禁止在同一条 8 个方向的线上（如超级皇后）、三维棋盘版本等，每种对冲突检查的要求不同。
3. 索引范围忽略：两个对角线数组的大小应为 2n-1，非 n。使用 2n 是安全的做法。

## 例题

**例题1：** 4皇后问题的所有解。

**解答：** 解1：(0,1), (1,3), (2,0), (3,2)。解2：(0,2), (1,0), (2,3), (3,1)。验证解1：列：1≠3≠0≠2，主对角线：0-1+3≠1-3+3=1, 0-1+3=-1+3=2, 1-3+3=1...验证各项不冲突。

**例题2：** 分析 n 皇后问题回溯法的时间复杂度。

**解答：** 最坏需探索 n! 个排列，但剪枝后可大幅减少。实际运行节点数远少于 n!。使用位运算加速（N-Queens Bitwise 解法）可进一步减小常数因子，但对最坏复杂度无渐近改进。n皇后问题被论证为 #P 完全问题（计数解个数）。

## 代码示例

```python
def solve_n_queens(n):
    results = []
    cols = [False] * n
    diag1 = [False] * (2 * n)  # 主对角线
    diag2 = [False] * (2 * n)  # 副对角线
    board = [-1] * n
    
    def backtrack(row):
        if row == n:
            results.append(board[:])
            return
        for col in range(n):
            d1 = row - col + n
            d2 = row + col
            if cols[col] or diag1[d1] or diag2[d2]:
                continue  # 约束剪枝
            # 放置皇后
            board[row] = col
            cols[col] = diag1[d1] = diag2[d2] = True
            backtrack(row + 1)
            # 回溯
            cols[col] = diag1[d1] = diag2[d2] = False
    
    backtrack(0)
    return results

# 位运算加速版本（最高效）
def solve_n_queens_bit(n):
    results = []
    all_cols = (1 << n) - 1
    
    def backtrack(row, cols, diag1, diag2, current):
        if cols == all_cols:
            results.append(current[:])
            return
        # 可放置的位置：未被列、两条对角线占用的位
        available = all_cols & (~(cols | diag1 | diag2))
        while available:
            bit = available & -available  # 取最低位的1
            col = (bit.bit_length() - 1)
            available ^= bit
            current.append(col)
            backtrack(row + 1, cols | bit, 
                      (diag1 | bit) << 1, (diag2 | bit) >> 1, current)
            current.pop()
    
    backtrack(0, 0, 0, 0, [])
    return results

print("4皇后解数:", len(solve_n_queens(4)))      # 2
print("8皇后解数:", len(solve_n_queens_bit(8)))  # 92
```

## 关联页面

[[回溯法]] [[图的着色]] [[哈密顿回路]] [[约束满足问题]]
