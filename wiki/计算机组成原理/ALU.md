---
title: 算术逻辑单元 ALU
course: 计算机组成原理
chapter: 第三章 运算器
difficulty: INTERMEDIATE
tags: [ALU, 算术逻辑单元, 运算器, 功能选择, 标志位, 多功能运算]
aliases: [Arithmetic Logic Unit, ALU结构]
source:
  - Patterson & Hennessy, Computer Organization and Design
updated_at: 2026-05-02

---

## 核心定义

算术逻辑单元（Arithmetic Logic Unit, ALU）是 CPU 中执行算术和逻辑运算的核心部件。ALU 接收两个 n 位的操作数 A 和 B，以及一个功能选择信号（Function Select / ALUOp），根据控制信号执行特定的运算（如加法、减法、与、或、异或、移位等），输出 n 位结果以及用于条件判断的标志位（Flags）。标志位通常包括：零标志位 ZF（Zero Flag，结果为零），进位/借位标志 CF（Carry Flag，加法进位或减法借位），溢出标志 OF（Overflow Flag，有符号数溢出），符号标志 SF（Sign Flag，结果最高位），奇偶标志 PF（Parity Flag）。ALU 的设计通常以加法器为核心，通过操作数的预处理（如对减法取补码）、多路选择器和逻辑门扩展，实现对多种运算的支持。现代 CPU 的 ALU 通常为 32 位或 64 位宽。

## 关键结论

- ALU 的核心是加法器：减法 = A + (-B)的补码 = A + ~B + 1；比较指令实质是减法但仅设置标志位不写回结果
- ALUOp 控制信号的编码决定了当前执行的运算类型，例如 2 位 ALUOp + Funct 字段扩展可编码十几条不同的运算
- 1 位 ALU 是基本构件：包含 AND 门、OR 门、1 位全加器和多路选择器（MUX）
- MIPS ALU 可执行：加法、减法、AND、OR、NOR、XOR、置小于（SLT）、移位等
- ALU 的标志位寄存器（Flag Register / Condition Code Register）是程序状态字 PSW 的核心部分

## 易错点

1. 溢出的判断：加法溢出 = 同号相加结果异号；减法溢出 = 异号相减结果与被减数异号。
2. SLT 指令的实现区别：MIPS 等 RISC 架构中 SLT 是独立的 ALU 功能，而非使用标志位。
3. 标志位更新策略：RISC-V 不使用条件码而是比较后分支（Compare-and-Branch），简化了流水线中标志位的维护。

## 例题

**例题1：** 设计一个支持 AND, OR, ADD 三种功能的简单 1 位 ALU。

**解答：** 输入：A, B, Cin, 2 位 Op。输出：Result, Cout。使用 4-1 MUX 选择输出：Op=00 选 A AND B；Op=01 选 A OR B；Op=10 选全加器 S 输出（A+B+Cin）。Cout = 仅当 Op=10 时有意义 = (A AND B) OR (Cin AND (A XOR B))。

**例题2：** 在 ALU 中如何实现 A - B？解释为何能用加法器实现减法。

**解答：** A - B = A + (-B) = A + (~B + 1)。ALU 中通过在加法器输入端 B 前放置反相器（NOT gate），并将最低位进位 Cin 设为 1（实现 +1），从而实现补码减法。因此减法无需独立硬件，仅需对 B 取反并将 Cin 设为 1。

## 代码示例

```python
class SimpleALU:
    def __init__(self, width=32):
        self.width = width
        self.mask = (1 << width) - 1
    
    def execute(self, op, a, b):
        """op: 0=ADD, 1=SUB, 2=AND, 3=OR, 4=XOR, 5=NOR"""
        if op == 0:  # ADD
            result = (a + b) & self.mask
            overflow = ((a ^ result) & (b ^ result) & (1 << (self.width - 1))) != 0
        elif op == 1:  # SUB
            result = (a - b) & self.mask
            overflow = ((a ^ b) & (a ^ result) & (1 << (self.width - 1))) != 0
        elif op == 2:  # AND
            result = a & b
            overflow = False
        elif op == 3:  # OR
            result = a | b
            overflow = False
        elif op == 4:  # XOR
            result = a ^ b
            overflow = False
        elif op == 5:  # NOR
            result = (~(a | b)) & self.mask
            overflow = False
        
        zero = (result == 0)
        sign = (result >> (self.width - 1)) & 1
        carry = ((a + b) >> self.width) & 1
        
        return result, {'ZF': zero, 'SF': sign, 'OF': overflow, 'CF': carry}

alu = SimpleALU(8)
r, flags = alu.execute(0, 100, 50)  # ADD
print(f"100+50={r}, flags={flags}")
r, flags = alu.execute(1, 50, -30)  # SUB (50-(-30)=80)
print(f"50-(-30)={r}, flags={flags}")
```

## 关联页面

[[加法器]] [[定点运算]] [[CPU结构]] [[数据通路]]
