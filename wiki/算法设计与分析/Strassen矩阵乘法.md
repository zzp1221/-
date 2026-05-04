---
title: Strassen矩阵乘法
course: 算法设计与分析
chapter: 第二章 递归与分治
difficulty: ADVANCED
tags: [Strassen, 矩阵乘法, 分治法, 数值计算, 线性代数]
aliases: [Strassen Matrix Multiplication, Strassen算法]
source:
  - Strassen, Gaussian Elimination is not Optimal (1969)
  - Cormen, Introduction to Algorithms (CLRS)
updated_at: 2026-05-02
---

## 核心定义

Strassen矩阵乘法是由 Volker Strassen 于1969年提出的分治矩阵乘法算法。经典矩阵乘法的复杂度为 O(n^3)（n 为方阵维度），而 Strassen 算法通过巧妙的代数变换，将两个 n x n 方阵的乘法分解为 7 次 n/2 x n/2 子矩阵乘法和 18 次矩阵加减法，而非传统的 8 次子矩阵乘法。其递归式为 T(n) = 7T(n/2) + O(n^2)，使用主定理解得 T(n) = Θ(n^{log_2 7}) ≈ Θ(n^{2.807})。这是人类首次证明矩阵乘法可以在亚立方时间内完成，开启了快速矩阵乘法的研究领域。理论上存在更快的 Coppersmith-Winograd 算法（约 O(n^{2.376})），但由于常数因子过大，实际中仍以 Strassen 算法和优化后的传统算法为主。

## 关键结论

- Strassen算法的核心在于用 7 次乘法替代 8 次乘法，这看似微小的减少通过分治法使指数降低
- 递归基条件：当矩阵缩小到一定阈值时，切换回传统 O(n^3) 乘法效率更高
- 加减法开销：Strassen 比传统分治法多做 14 次 n/2 x n/2 矩阵加减法，但对数因子足以抵消这一开销
- 数值稳定性：Strassen 算法比传统方法稍差，在科学计算中需谨慎使用
- 实际应用：现代 BLAS 库（如 OpenBLAS、MKL）对 Strassen 进行了工程优化，配合多线程、SIMD 和缓存分块（Blocking）使其实用化

## 易错点

1. 矩阵必须为方阵且维度为 2 的幂次：如果不是，需要填充零行零列，这会增加额外开销。
2. 将 7 个 P 矩阵的计算公式写错：Strassen 的 7 个中间乘积有严格定义——P1=A11*(B12-B22), P2=(A11+A12)*B22, P3=(A21+A22)*B11, P4=A22*(B21-B11), P5=(A11+A22)*(B11+B22), P6=(A12-A22)*(B21+B22), P7=(A11-A21)*(B11+B12)。组合成 C 时也须按公式：C11=P5+P4-P2+P6, C12=P1+P2, C21=P3+P4, C22=P5+P1-P3-P7。
4. 忽略切换阈值导致性能倒退：传统 O(n^3) 的常数因子远小于 Strassen（约为 7/8 的乘法对应大量加法），对中小矩阵需要切换到传统算法。

## 例题

**例题1：** 证明 Strassen 递归式 T(n) = 7T(n/2) + O(n^2) 的解为 Θ(n^{log_2 7})。

**解答：** 使用主定理：a=7, b=2, f(n)=O(n^2)。log_2 7 ≈ 2.807。比较 f(n)=n^2 与 n^{log_2 7}。取 ε=0.5，则 n^2 = O(n^{2.807-0.5}) = O(n^{2.307})，满足 Case 1。所以 T(n) = Θ(n^{log_2 7})。

**例题2：** 比较 Strassen 与经典算法在 n=1024 时的理论加速比。

**解答：** 经典算法：1024^3 ≈ 1.07e9 次标量乘法。Strassen：1024^{log_2 7} ≈ 1024^{2.807} ≈ 2.74e8 次标量乘法。加速比约 3.9x。实际因加减法和递归开销会打折扣，但仍有约 2-3x 的实际加速。

## 代码示例

```python
import numpy as np

def strassen(A, B, threshold=64):
    """Strassen矩阵乘法，带阈值优化"""
    n = A.shape[0]
    
    # 基准情况：小矩阵使用传统乘法
    if n <= threshold:
        return A @ B
    
    # 若 n 为奇数，填充一行一列
    if n % 2 == 1:
        A_pad = np.pad(A, ((0,1),(0,1)))
        B_pad = np.pad(B, ((0,1),(0,1)))
        C_pad = strassen(A_pad, B_pad, threshold)
        return C_pad[:n, :n]
    
    # 分块
    mid = n // 2
    A11, A12 = A[:mid, :mid], A[:mid, mid:]
    A21, A22 = A[mid:, :mid], A[mid:, mid:]
    B11, B12 = B[:mid, :mid], B[:mid, mid:]
    B21, B22 = B[mid:, :mid], B[mid:, mid:]
    
    # Strassen 的 7 个乘法
    P1 = strassen(A11, B12 - B22, threshold)
    P2 = strassen(A11 + A12, B22, threshold)
    P3 = strassen(A21 + A22, B11, threshold)
    P4 = strassen(A22, B21 - B11, threshold)
    P5 = strassen(A11 + A22, B11 + B22, threshold)
    P6 = strassen(A12 - A22, B21 + B22, threshold)
    P7 = strassen(A11 - A21, B11 + B12, threshold)
    
    # 组合结果
    C11 = P5 + P4 - P2 + P6
    C12 = P1 + P2
    C21 = P3 + P4
    C22 = P5 + P1 - P3 - P7
    
    # 拼接
    C = np.zeros((n, n))
    C[:mid, :mid], C[:mid, mid:] = C11, C12
    C[mid:, :mid], C[mid:, mid:] = C21, C22
    return C
```

## 关联页面

[[分治法]] [[主定理]] [[递归式求解]] [[数值算法]]
