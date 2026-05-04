---
title: DFA
course: 编译原理
chapter: 词法分析
difficulty: INTERMEDIATE
tags: [DFA, 确定性有限自动机, 有限自动机, 状态转移, 确定化, 死状态]
aliases: [Deterministic Finite Automaton, 确定有限自动机]
source:
  - Alfred V. Aho《Compilers: Principles, Techniques, and Tools》(龙书)
updated_at: 2026-05-02
---

## 核心定义

确定性有限自动机（DFA, Deterministic Finite Automaton）是有限自动机的一种限制形式，要求转移函数是**确定的**——对于每个状态和每个输入符号，至多有一个下一状态。定义 M = (Q, Σ, δ, q₀, F)，其中 Q 是状态有限集、Σ 是字母表、δ: Q×Σ → Q 是**全函数**（确定性转移函数，每个状态对每个输入符号恰有一个转移）、q₀∈Q 是初始状态、F⊆Q 是接受状态集。与 NFA 相比，DFA 没有 ε-转移且转移是唯一确定的，因此对于任何输入串，DFA 的计算路径是唯一的。DFA 接受语言 L(M) = {w∈Σ* | δ*(q₀,w)∈F}，其中 δ* 是 δ 的自反传递闭包。DFA 是正则语言的**规范**识别器：每个正则语言都存在唯一的最小 DFA（在同构意义下），最小化 DFA 可以通过 Hopcroft 算法（O(n log n)）或 Moore 算法（O(n²)）完成。DFA 的实现通常使用二维转移表（状态数 × 字母表大小），查找效率 O(1)。

## 关键结论

- DFA 与 NFA 等价：任何 NFA 可通过子集构造法转化为等价的 DFA——这是正则语言的稳健性体现
- 正则语言的最小 DFA 在同构意义下唯一：最小 DFA 的状态数与 Myhill-Nerode 等价类一一对应
- DFA 的完备性：δ 必须是全函数，每个状态对每个符号都应有定义——若不完整可添加一个非接受"死状态"（sink state）
- DFA 的复杂性：最坏情况下，n 个状态的 NFA 可能需要 2ⁿ 个状态的等价的 DFA
- 最小化 DFA 可以极大减少状态数，状态数即等于该语言的正则等价类数
- DFA 的实现简洁高效：转移表是一个二维数组，驱动代码仅需一个 while 循环

## 易错点

1. DFA 的 δ 必须是全函数：若某个状态下某个输入符号没有定义转移，应引入"死状态"（非接受状态，对所有输入均回自身）使 δ 完备
2. 最小化 DFA 时的初始划分：将状态分为接受状态和非接受状态两类，从这两类出发逐步细化——初始划分错误会导致最终结果不对
3. DFA 的接受判定：串被接受当且仅当处理完整个字符串后的状态 ∈ F

## 例题

**例题1**：构造一个 DFA 识别语言 L = {w∈{0,1}* | w 以 "01" 结尾}。

**解答**：状态 q₀（尚未匹配到任何"01"的部分）、q₁（最新读到的字符是 0）、q₂（已匹配到 "01"，接受状态）。
转移：δ(q₀,0)=q₁, δ(q₀,1)=q₀; δ(q₁,0)=q₁, δ(q₁,1)=q₂; δ(q₂,0)=q₁, δ(q₂,1)=q₀。
初始状态 q₀，F={q₂}。

**例题2**：最小化以下 DFA：状态集 {A,B,C,D,E}，初始状态 A，接受状态 {D,E}。
转移表：δ(A,0)=B, δ(A,1)=C; δ(B,0)=D, δ(B,1)=E; δ(C,0)=B, δ(C,1)=C; δ(D,0)=D, δ(D,1)=E; δ(E,0)=D, δ(E,1)=E。

**解答**：初始划分 Π₀ = {D,E}, {A,B,C}。
考察 {A,B,C}：读 0 分别到 B,D,B。D 在接受类而 B 不在，故划分 A(→B∈Π₁) 和 C(→B∈Π₁)... 这里需要迭代直到收敛。

## 代码示例

```python
class DFA:
    def __init__(self, transitions, start, accepts):
        self.trans = transitions  # dict: (state, symbol) -> state
        self.start = start
        self.accepts = set(accepts)
    
    def run(self, s):
        state = self.start
        for ch in s:
            state = self.trans.get((state, ch))
            if state is None:
                return False
        return state in self.accepts

# DFA识别以"01"结尾的串
dfa = DFA(
    transitions={
        ('q0','0'):'q1', ('q0','1'):'q0',
        ('q1','0'):'q1', ('q1','1'):'q2',
        ('q2','0'):'q1', ('q2','1'):'q0'
    },
    start='q0', accepts={'q2'}
)

for w in ['', '0', '01', '001', '101', '010', '0101']:
    print(f"'{w}': {dfa.run(w)}")
```

## 关联页面

[[NFA]] [[NFA转DFA]] [[DFA最小化]] [[词法分析]] [[正规式与正规文法]]
