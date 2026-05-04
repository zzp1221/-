---
title: IEEE754浮点数标准
course: 计算机组成原理
chapter: 第二章 数据表示
difficulty: INTERMEDIATE
tags: [IEEE754, 浮点数, 单精度, 双精度, 阶码, 尾数, NaN, 非规格化数]
aliases: [IEEE 754, IEEE Floating Point, float, double]
source:
  - IEEE Std 754-2008
  - Patterson & Hennessy, Computer Organization and Design
updated_at: 2026-05-02

---

## 核心定义

IEEE754 是 IEEE 制定的浮点数算术标准（最新版 IEEE 754-2019），定义了浮点数的格式、运算规则和舍入模式。标准规定了多种精度格式：单精度（Single Precision, 32位）：1位符号位 S + 8位阶码 E（偏移量 Bias=127）+ 23位尾数 M；双精度（Double Precision, 64位）：1位符号 + 11位阶码（Bias=1023）+ 52位尾数。浮点数的值由公式 V = (-1)^S * (1 + M) * 2^{E - Bias} 给出（规格化数）。阶码的偏移表示（移码）使得无符号整数比较器可直接用于浮点数比较。IEEE754 定义了特殊值：阶码全1 + 尾数全0 = 正/负无穷（±∞）；阶码全1 + 尾数非0 = NaN（Not a Number，如 0/0、√(-1)）；阶码全0 + 尾数全0 = ±0；阶码全0 + 尾数非0 = 非规格化数（Denormalized Number），用于填补 0 附近的下溢区间（Gradual Underflow），值为 (-1)^S * M * 2^{-126}。

## 关键结论

- 规格化数的隐含位（Hidden Bit）：规格化尾数最高位恒为 1，因此 IEEE754 在存储时隐含"1."前缀，有效精度多 1 位
- 单精度范围：约 ±1.18 * 10^{-38} 到 ±3.40 * 10^{38}，有效数字约 7 个十进制位
- 双精度范围：约 ±2.23 * 10^{-308} 到 ±1.80 * 10^{308}，有效数字约 15-16 位
- 舍入模式：就近舍入（Round to Nearest, Ties to Even）、向零舍入、向正无穷舍入、向负无穷舍入（默认就近舍入偶数）
- 非规格化数（Denormal）解决了规格化数在下溢处的"空洞"，实现了渐进下溢

## 易错点

1. 隐含位的存在导致直接拼接尾数位计算时数值偏小 2 倍——忘记加回隐含的 1。
2. 单精度 23 位尾数实际表示 24 位精度（含隐含 1），故有效数字为 24*log10(2) ≈ 7.2。
3. NaN != NaN 在 IEEE754 中的特殊规定：任何 NaN 之间的比较返回 False（包括自身），这使得 isnan() 函数成为必要。NaN 的静默（Quiet）和信号（Signaling）之分类也常被忽视。

## 例题

**例题1：** 将十进制数 -12.625 表示为 IEEE754 单精度格式。

**解答：** S=1（负数）。12.625 = 1100.101_(2) = 1.100101 * 2^3（规格化）。尾数 M = 10010100000000000000000（23位）。阶码 E = 3 + 127 = 130 = 10000010_(2)。最终：1 | 10000010 | 10010100000000000000000 = 11000001010010100000000000000000 = 0xC14A0000。

**例题2：** 解释为何 0.1 + 0.2 != 0.3 在浮点运算中成立。

**解答：** 0.1_(10) = 0.0001100110011..._(2)（无限循环），单精度中只能保存约 7 位有效数字，0.1 和 0.2 均无法精确表示。0.1 + 0.2 的浮点计算结果 ≈ 0.30000001192092896 ≈ 0.3。由于舍入误差累积，结果不与 0.3 完全相等。

## 代码示例

```python
import struct

def float_to_ieee754_hex(f):
    """将 Python float 转为 IEEE754 单精度的十六进制"""
    packed = struct.pack('>f', f)
    return '0x' + packed.hex().upper()

def print_float_components(f):
    """打印浮点数的符号、阶码、尾数"""
    packed = struct.pack('>f', f)
    bits = int.from_bytes(packed, 'big')
    sign = (bits >> 31) & 1
    exponent = (bits >> 23) & 0xFF
    mantissa = bits & 0x7FFFFF
    print(f"值: {f}")
    print(f"  S = {sign}")
    print(f"  E = {exponent} (去偏: {exponent - 127})")
    print(f"  M = {mantissa:023b}")
    
    # 特殊值判断
    if exponent == 0xFF:
        if mantissa == 0:
            print(f"  => {'-' if sign else '+'}∞")
        else:
            print(f"  => NaN")
    elif exponent == 0:
        if mantissa == 0:
            print(f"  => {'-' if sign else '+'}0")
        else:
            print(f"  => Denormalized")

# 示例
print_float_components(-12.625)
print_float_components(0.1)
print(f"0.1 hex: {float_to_ieee754_hex(0.1)}")

# 比较浮点误差
print(f"0.1 + 0.2 = {0.1 + 0.2}")
print(f"0.1 + 0.2 == 0.3: {0.1 + 0.2 == 0.3}")  # False!
```

## 关联页面

[[定点数与浮点数]] [[原码反码补码移码]] [[浮点运算]] [[BCD码与ASCII]]
