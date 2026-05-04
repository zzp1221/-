---
title: NFA
course: 编译原理
chapter: 词法分析
difficulty: INTERMEDIATE
tags: [NFA, 非确定性有限自动机, 有限自动机, 状态转移, Thompson构造法]
aliases: [Nondeterministic Finite Automaton, 非确定有限自动机]
source:
  - Alfred V. Aho《Compilers: Principles, Techniques, and Tools》(龙书)
updated_at: 2026-05-02

---

## 核心定义

非确定性有限自动机（NFA, Nondeterministic Finite Automaton）是有限自动机的一种形式，允许从同一状态读取同一输入符号转移到多个不同状态，也允许不消耗输入符号的 ε-转移。形式化定义为 M = (Q, Σ, δ, q₀, F)，其中 Q 是有限状态集合、Σ 是字母表、δ: Q × (Σ∪{ε}) → P(Q) 是转移函数（将状态和输入映射到状态的子集，体现非确定性）、q₀ 是初始状态、F ⊆ Q 是接受状态集。NFA 接受字符串 w 的条件是：存在一个状态序列 r₀,r₁,...,rₙ 满足 r₀=q₀, rₙ∈F，且对于每个 i，rᵢ₊₁ ∈ δ(rᵢ, aᵢ₊₁)（或 rᵢ₊₁ ∈ δ(rᵢ, ε)）。关键定理：NFA 与 DFA 等价——任何 NFA 都可转化为等价的 DFA（通过子集构造法），因此 NFA 也恰好识别正则语言。

Thompson 构造法是系统性地从正规式构造等价的 NFA 的算法。其核心思想是：将正规式分解为基本构件，每个构件对应一个小型 NFA，然后通过 ε-转移将这些小型 NFA 按照正规式的运算（连接、选择、闭包）组合起来。

## 关键结论

- NFA 的非确定性体现在两方面：(1) 同一状态下读同一符号可转移至不同状态；(2) 存在 ε-转移（不消耗输入即自动发生的转移）
- NFA 接受字符串的判断依据是：存在至少一条从初始状态到某个接受状态的路径
- NFA 可能比等价的 DFA 指数级地更紧凑（状态数少）——例如 (a|b)*a(a|b)ⁿ 的 NFA 仅需 n+2 个状态，而 DFA 需要 2ⁿ 个状态
- ε-闭包 ε-closure(S) 是 S 中的状态通过零次或多次 ε-转移可达的所有状态的集合
- ε-转移虽然增加了模型的复杂度，但也是 NFA 构造（Thompson 法）和转换的基础
- NFA 的推广应用包括带输出的自动机（Moore机、Mealy机）以及与正则表达式匹配相关的各种引擎

## 易错点

1. 混淆 NFA 与 DFA 的接受条件：DFA 有唯一计算路径，而 NFA 只要存在某条路径到达接受状态即接受；若所有可能路径都拒绝才拒绝
2. NFA 中计算 δ 时需要求 ε-闭包：从当前状态出发，先通过所有可能的 ε-转移扩展状态集，再对输入符号做转移，之后再求 ε-闭包
3. 子集构造时误以为每个 NFA 状态子集都需要计算转移：实际上只需计算从初始状态可达的状态子集

## 例题

**例题1**：构造正规式 a(b|c)* 的 NFA（Thompson 法）。

**解答**：
步骤：(1) 构造 'a' 的 NFA：0 --a--> [1]；(2) 构造 'b' 的 NFA：2 --b--> [3]，构造 'c' 的 NFA：4 --c--> [5]；(3) b|c：合并起点和终点，ε 转移连接 → NFA_bc；(4) (b|c)*：增加从终点回起点的 ε 转移和直接跨越的 ε 转移；(5) 将 a 的 NFA 与 (b|c)* 的 NFA 通过 ε 连接。最终状态数为 6（起点 0 到终点共 6 个状态）。

**例题2**：NFA M = ({q₀,q₁,q₂}, {a,b}, δ, q₀, {q₂})，其中 δ(q₀,a)={q₀,q₁}, δ(q₀,b)={q₀}, δ(q₁,b)={q₂}, δ(q₂,*)=∅。判断字符串 "aab" 是否被接受。

**解答**：枚举路径。读 'a': q₀→q₀ 或 q₀→q₁。路径1: q₀→add 'a'→q₀→add 'a'→q₀→add 'b'→q₀（拒绝）。路径2: q₀→add 'a'→q₁→读 'a'❌（q₁ 读 a 无转移，此路径死亡）。路径3: q₀→add 'a'→q₀→add 'a'→q₁→add 'b'→q₂（接受）。存在接受路径，故接受。

## 代码示例

```python
class NFA:
    def __init__(self, states, alphabet, transitions, start, accepts):
        self.states = states              # set of states
        self.alphabet = alphabet          # set of symbols
        self.transitions = transitions    # dict: (state, symbol) -> set of states
        self.start = start
        self.accepts = accepts
    
    def epsilon_closure(self, states_set):
        """计算ε-闭包"""
        stack = list(states_set)
        closure = set(states_set)
        while stack:
            s = stack.pop()
            eps_targets = self.transitions.get((s, None), set())
            for t in eps_targets:
                if t not in closure:
                    closure.add(t)
                    stack.append(t)
        return closure
    
    def accepts_string(self, s):
        """判断NFA是否接受字符串s"""
        current_states = self.epsilon_closure({self.start})
        for char in s:
            next_states = set()
            for state in current_states:
                targets = self.transitions.get((state, char), set())
                next_states |= targets
            current_states = self.epsilon_closure(next_states)
        return bool(current_states & self.accepts)

# 构造 a(b|c)* 的 NFA
nfa = NFA(
    states={0,1,2,3,4,5},
    alphabet={'a','b','c'},
    transitions={
        (0, 'a'): {1},
        (1, None): {2}, (2, 'b'): {3}, (2, 'c'): {4},
        (3, 'b'): {3}, (3, 'c'): {4}, (4, 'b'): {3}, (4, 'c'): {4},
        (3, None): {5}, (4, None): {5}, (2, None): {5},
        (5, None): {2}
    },
    start=0, accepts={5}
)
print(nfa.accepts_string("abc"))  # True
```

## 关联页面

[[词法分析]] [[DFA]] [[NFA转DFA]] [[正规式与正规文法]]
