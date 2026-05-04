---
title: 语法制导定义SDD
course: 编译原理
chapter: 语义分析
difficulty: INTERMEDIATE
tags: [语法制导定义, SDD, 属性文法, 综合属性, 继承属性, 依赖图]
aliases: [Syntax-Directed Definition, SDD, Attribute Grammar]
source:
  - Alfred V. Aho《Compilers: Principles, Techniques, and Tools》(龙书)
updated_at: 2026-05-02

---

## 核心定义

语法制导定义（Syntax-Directed Definition, SDD）是一种将语义信息附加到文法结构上的形式化方法。它由一个上下文无关文法和一组语义规则（Semantic Rule）组成：为每个文法符号关联一组**属性**（Attribute），并为每条产生式关联一组计算这些属性的语义规则。属性分为两类：(1) **综合属性**（Synthesized Attribute）：由产生式右部的属性和/或左部自身的其他属性计算而来——信息自底向上流动；(2) **继承属性**（Inherited Attribute）：由产生式左部的属性、右部中其他兄弟符号的属性、或自身已有的属性计算而来——信息自顶向下或横向流动。

SDD 不指定计算属性的具体顺序，只声明属性之间的**依赖关系**——这由**依赖图**（Dependency Graph）刻画。依赖图是有向图：节点为属性实例，有向边表示"属性 b 的计算依赖属性 a"。若依赖图中无环（即 SDD 是非循环的），则可以找到一个拓扑排序来计算所有属性。语法制导翻译（SDT）则是在 SDD 基础上添加了求值顺序的约束。

SDD 的重要子类包括：(1) **S-属性定义**（S-Attributed Definition）：仅使用综合属性——属性计算可自底向上单遍完成；(2) **L-属性定义**（L-Attributed Definition）：综合属性 + 受限的继承属性（继承属性只能依赖父节点的继承属性或左兄弟的综合属性）——属性计算可在自顶向下（LL）或自底向上（LR）的单遍分析中完成。

## 关键结论

- SDD 将语义计算"附着"在语法结构上，实现了语法驱动的语义分析
- 综合属性综合信息自底向上（如表达式类型由子表达式类型确定）
- 继承属性传递上下文信息自顶向下（如声明类型传递给变量）
- 依赖图的无环性是语义规则一致性的保证——若有环则无法计算
- S-属性 SDD 总是非循环的（因为综合属性只依赖子节点）
- SDD 使得语法树的装饰（Annotation）成为可能：遍历语法树按依赖图顺序计算所有属性

## 易错点

1. 综合属性与继承属性的方向混淆：综合属性从子节点向父节点传递，继承属性从父节点或左兄弟向当前节点传递
2. 依赖图中有向边的方向：A 依赖 B 时边从 B 指向 A——边的方向表示"被依赖→依赖者"
3. L-属性定义的继承属性限制：不能依赖右兄弟的综合属性——违反此限制的 SDD 可能需要多遍扫描

## 例题

**例题1**：为简单整数算术表达式文法设计 SDD，计算表达式的值。

**解答**：使用综合属性 val。
产生式及语义规则：
- L → E      { print(E.val) }
- E → E₁ + T { E.val = E₁.val + T.val }
- E → T      { E.val = T.val }
- T → T₁ * F { T.val = T₁.val * F.val }
- T → F      { T.val = F.val }
- F → (E)    { F.val = E.val }
- F → digit  { F.val = digit.lexval }

所有属性均为综合属性（S-属性定义），可在 LR 分析中自底向上计算。

**例题2**：设计 SDD 为变量声明语句计算类型信息。

**解答**：产生式 D → T id; D₁。需要继承属性来传递类型信息。
- T → int   { T.type = "int" }
- T → float { T.type = "float" }
- D → T id; D₁ { id.type = T.type (继承信息从 T 传给 id); D₁ 继承 T.type }
- D → ε    { }

这里 id.type 由 T.type 继承而来，属于继承属性作为类型从声明部分传递给所有变量。

## 代码示例

```python
class ASTNode:
    def __init__(self, name, children=None):
        self.name = name
        self.children = children or []
        self.attrs = {}  # 属性字典
    
    def set_synthesized(self, attr, value):
        self.attrs[attr] = value
    
    def get_attr(self, attr):
        return self.attrs.get(attr)

# S-属性SDD求值: 自底向上计算综合属性
def evaluate_sdd(node):
    """计算表达式AST的综合属性val"""
    # 先递归计算所有子节点的属性
    for child in node.children:
        evaluate_sdd(child)
    
    # 计算当前节点的val
    if node.name == 'E':
        if len(node.children) == 3:  # E -> E + T
            node.attrs['val'] = node.children[0].attrs['val'] + \
                                node.children[2].attrs['val']
        else:  # E -> T
            node.attrs['val'] = node.children[0].attrs['val']
    elif node.name == 'digit':
        node.attrs['val'] = node.attrs.get('lexval', 0)

# 构造 3+5 的AST并求值
ast = ASTNode('E', [
    ASTNode('digit', attrs={'lexval': 3}),
    ASTNode('+'),
    ASTNode('digit', attrs={'lexval': 5})
])
```

## 关联页面

[[语法制导翻译SDT]] [[S属性与L属性]] [[上下文无关文法]] [[符号表]] [[类型检查]]
