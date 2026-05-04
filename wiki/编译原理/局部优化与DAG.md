---
title: 局部优化与DAG
course: 编译原理
chapter: 代码优化
difficulty: INTERMEDIATE
tags: [局部优化, DAG, 公共子表达式消除, 复写传播, 死代码消除, 代数简化]
aliases: [Local Optimization, DAG-Based Optimization, 基本块优化]
source:
  - Alfred V. Aho《Compilers: Principles, Techniques, and Tools》(龙书)
updated_at: 2026-05-02

---

## 核心定义

局部优化（Local Optimization）是在单个基本块范围内进行的优化，不涉及跨块的控制流分析。DAG（Directed Acyclic Graph，有向无环图）是其最有力的工具——用 DAG 表示基本块内的计算，可以自然地发现公共子表达式并消除冗余计算。

**DAG 构造**：为基本块中的每条指令构建 DAG 节点。对于三地址码 `x = y op z`：(1) 为 y 和 z 查找或创建叶子节点（表示初始值）；(2) 查找是否已有以 y 和 z 为子节点、op 为运算符的内部节点——若有，则此为公共子表达式，不需要新建节点；若无，则创建新节点并标记为 op；(3) 将 x 添加到该节点的附加标识符列表中（表示变量 x 持有该节点的值）。

局部优化的主要技术包括：
- **公共子表达式消除**（Common Subexpression Elimination, CSE）：若同一基本块内多次计算相同表达式且变量值未改变，则重用第一次计算结果
- **复写传播**（Copy Propagation）：`x = y` 后，后续使用 x 的地方可以用 y 替代（只要 y 在这期间未改变）
- **死代码消除**（Dead Code Elimination）：删除其值不再被使用的变量的赋值指令。若一个变量被赋值后直到基本块结束都未被引用（或仅在死代码中被引用），则该赋值是死代码
- **代数简化**（Algebraic Simplification）：利用代数恒等式简化表达式，如 `x+0` → `x`、`x*1` → `x`、`x*2` → `x+x`（可能更高效）或 `x<<1`（移位替代乘法）
- **常量折叠**（Constant Folding）：编译期计算常量表达式的值，如 `3+5` → `8`

## 关键结论

- DAG 使得基本块内的公共子表达式"一目了然"——同一内部节点的多个附加标识符说明计算被多次使用
- 基于 DAG 的局部优化可以同时完成 CSE、死代码消除和简单的常量折叠
- 局部优化是"安全"的——在基本块内进行等价变换不会改变程序的控制流行为
- 代数简化利用了运算符的代数性质（交换律、结合律、分配律、恒等律），需要小心浮点数的精度问题
- 强度削弱（Strength Reduction）用低代价操作替代高代价操作：如乘法改为移位（仅对 2 的幂次成立）、除法改为乘法逆

## 易错点

1. DAG 构造中错误的公共子表达式识别：两节点虽然运算符和操作数相同，但若操作数的值可能在块内被修改（不同版本），不能视为公共子表达式
2. 死代码消除的过度激进：看似"死"的代码可能有隐含的副作用（如函数调用、volatile 变量访问），不能被消除
3. 浮点数代数简化的陷阱：由于浮点精度问题，某些代数恒等式在浮点数下不精确成立（如 (a+b)+c ≠ a+(b+c) 在极端情况下）

## 例题

**例题1**：用 DAG 优化基本块：
```
t1 = a + b
t2 = a + b    // 公共子表达式
t3 = t1 * c
t4 = t1 * c    // 公共子表达式
a = t3
```

**解答**：构造 DAG。a、b 为叶节点。`a+b` 产生内部节点 N1（标记为+），附加列表 {t1, t2}。c 为叶节点。`N1 * c` 产生内部节点 N2（标记为*），附加列表 {t3, t4}。优化后代码：
```
t1 = a + b
t3 = t1 * c
a = t3
```
消除了 t2 和 t4 的冗余计算。

**例题2**：分析以下代码中的常量折叠和复写传播机会：
```
x = 5
y = x + 3
z = y
w = z * 2
```

**解答**：常量折叠：x=5, y=5+3=8, w=8*2=16。复写传播：z=y → 后续使用 z 替换为 y。完全优化后：
```
x = 5
y = 8
z = 8
w = 16
```
甚至可以消除 x, y, z 的死代码（若后续未使用）。

## 代码示例

```python
class DAGNode:
    def __init__(self, op, left=None, right=None, value=None):
        self.op = op
        self.left = left
        self.right = right
        self.value = value  # 常量值
        self.labels = []    # 附加标识符列表

def build_dag_block(instructions):
    """为基本块构造DAG"""
    nodes = {}  # (op, left, right) -> DAGNode
    var_to_node = {}  # 变量 -> 当前值的节点
    
    for instr in instructions:
        parts = instr.replace(' ', '').split('=')
        if len(parts) != 2: continue
        target, expr = parts
        
        if '+' in expr:
            left, right = expr.split('+')
            left_node = var_to_node.get(left, DAGNode('leaf', value=left))
            right_node = var_to_node.get(right, DAGNode('leaf', value=right))
            
            key = ('+', id(left_node), id(right_node))
            if key not in nodes:
                nodes[key] = DAGNode('+', left_node, right_node)
            
            nodes[key].labels.append(target)
            var_to_node[target] = nodes[key]
    
    return nodes

print("DAG构造: 公共子表达式自动共享节点")
```

## 关联页面

[[基本块与流图]] [[循环优化]] [[数据流分析]] [[中间代码生成]]
