---
title: NFA转DFA
course: 编译原理
chapter: 词法分析
difficulty: INTERMEDIATE
tags: [NFA转DFA, 子集构造法, 确定化, ε-闭包, 状态子集, 词法分析]
aliases: [Subset Construction, NFA to DFA, 子集构造法, 确定化算法]
source:
  - Alfred V. Aho《Compilers: Principles, Techniques, and Tools》(龙书)
updated_at: 2026-05-02
---

## 核心定义

NFA 转 DFA 算法，又称**子集构造法**（Subset Construction），是将任意 NFA 转化为等价的 DFA 的系统性算法——这是证明 NFA 与 DFA 等价的核心构造。算法核心思想：将 NFA 的**一组状态**视为 DFA 的**一个状态**。具体步骤为：

(1) 计算 NFA 初始状态 q₀ 的 ε-闭包 ε-closure({q₀})，作为 DFA 的初始状态。

(2) 对当前未处理的 DFA 状态（NFA 状态子集）S 和每个输入符号 a：(a) 计算 move(S, a) = {t | ∃s∈S 使得 t∈δ(s,a)}，即从 S 中所有状态经 a 转移可达的 NFA 状态集合；(b) 计算 ε-closure(move(S, a)) 得到新的 NFA 状态子集 T；(c) 在 DFA 转移表中添加从 S 经 a 到 T 的转移。

(3) 重复步骤 (2) 直到没有新的状态子集产生。

(4) DFA 的接受状态：包含至少一个 NFA 接受状态的状态子集。

该算法在最坏情况下的复杂度为 O(2ⁿ)（n 为 NFA 状态数），因为 NFA 的状态子集共有 2ⁿ 个。但在实践中，大多数 NFA 只有少量可达的状态子集——这是子集构造法的实用价值所在。

## 关键结论

- 子集构造法正确处理了 NFA 的两种不确定性：ε-转移（通过 ε-闭包消除）和多路转移（通过状态子集"跟踪所有可能性"消除）
- 算法本质：构造 NFA 状态集的幂集子格中最小的含初始状态且对转移封闭的结构
- 懒惰求值（Lazy Evaluation）优化：只计算可达的子集，不枚举全部 2ⁿ 个子集，大幅减少实际复杂度
- 等价的 DFA 状态数 ≤ 2ⁿ，最坏情况下可达上界（例如语言 (a|b)*a(a|b)ⁿ⁻¹）
- 实现技巧：用位向量（Bit Vector）或集合哈希表示状态子集，用 BFS/队列驱动构造过程

## 易错点

1. 遗漏 ε-闭包计算：从 NFA 状态子集经符号转移后，必须再求 ε-闭包得到新的 DFA 状态；忘记此步将导致 DFA 状态不完整
2. 接受状态判定错误：DFA 状态 S 是接受状态当且仅当 S ∩ F ≠ ∅（S 中包含至少一个 NFA 接受状态，而非 S 中所有状态都是接受状态）
3. 死状态的遗漏：某些状态子集可能对某些符号没有转移，应添加指向"死状态"的转移来完备 DFA

## 例题

**例题1**：将 NFA M = ({q₀,q₁,q₂}, {a,b}, δ, q₀, {q₂}) 转化为 DFA，其中 δ(q₀,a)={q₀,q₁}, δ(q₀,b)={q₁}, δ(q₁,a)={q₂}, δ(q₂,*)=∅（其余未定义）。

**解答**：先计算各状态的 ε-闭包（无 ε-转移，故闭包即本身）。

DFA 初始状态 A = {q₀}。对 A 和符号 a：move({q₀},a) = {q₀,q₁}, 记 B={q₀,q₁}。move({q₀},b)={q₁}, 记 C={q₁}。

对 B 和 a：move(B,a)={q₀,q₁,q₂}, D={q₀,q₁,q₂}。move(B,b)={q₁}, C。

对 C 和 a：move(C,a)={q₂}, E={q₂}。move(C,b)→∅, 死状态 X。

对 D 和 a：move(D,a)={q₀,q₁,q₂}=D。move(D,b)={q₁}=C。

对 E 和 a,b：均→∅→X。X 对 a,b→X。接受状态：含 q₂ 的 DFA 状态→D, E。

## 代码示例

```python
def nfa_to_dfa(nfa_states, alphabet, nfa_transitions, nfa_start, nfa_accepts):
    """NFA转DFA的子集构造法"""
    def epsilon_closure(states):
        """简化的ε-闭包（假设没有ε-转移）"""
        return frozenset(states)
    
    start_set = epsilon_closure({nfa_start})
    dfa_states = [start_set]
    dfa_transitions = {}
    queue = [start_set]
    visited = {start_set}
    
    while queue:
        current = queue.pop(0)
        for symbol in alphabet:
            # move(current, symbol)
            next_states = set()
            for s in current:
                if (s, symbol) in nfa_transitions:
                    next_states |= nfa_transitions[(s, symbol)]
            if not next_states:
                continue
            next_closure = epsilon_closure(next_states)
            dfa_transitions[(current, symbol)] = next_closure
            if next_closure not in visited:
                visited.add(next_closure)
                dfa_states.append(next_closure)
                queue.append(next_closure)
    
    dfa_accepts = {s for s in dfa_states if s & nfa_accepts}
    return dfa_states, dfa_transitions, start_set, dfa_accepts

# 示例NFA: (a|b)*a
nfa_trans = {
    ('q0','a'):{'q0','q1'}, ('q0','b'):{'q1'},
    ('q1','a'):{'q2'}
}
result = nfa_to_dfa({'q0','q1','q2'}, {'a','b'}, nfa_trans, 'q0', {'q2'})
print(f"DFA状态数: {len(result[0])}")
```

## 关联页面

[[NFA]] [[DFA最小化]] [[词法分析]] [[DFA]]
