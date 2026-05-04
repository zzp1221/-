---
title: S属性与L属性
course: 编译原理
chapter: 语义分析
difficulty: INTERMEDIATE
tags: [S属性, L属性, 属性文法, 综合属性, 继承属性, SDD分类]
aliases: [S-Attributed, L-Attributed, 属性分类]
source:
  - Alfred V. Aho《Compilers: Principles, Techniques, and Tools》(龙书)
updated_at: 2026-05-02

---

## 核心定义

S 属性和 L 属性是语法制导定义（SDD）中属性的两个核心分类，直接决定属性计算的**可行分析算法**和**遍数**。

**S-属性定义**（S-Attributed Definition）是一种仅使用**综合属性**的 SDD——所有属性都从子节点向父节点方向计算。S-属性定义完全适合自底向上（LR）分析：在产生式被归约时，其右部所有子节点已被归约（综合属性已知），可以立即计算左部的综合属性。S-属性定义的计算是单遍的、后序遍历的。

**L-属性定义**（L-Attributed Definition）是 S-属性的推广，允许有限形式的**继承属性**：(1) 一个产生式右部符号 X 的继承属性只能依赖于 X 左边符号（α中符号）的任意属性、或产生式左部 A 的继承属性；(2) 左部 A 的综合属性可依赖 A 的继承属性和右部任意符号的属性。关键约束是：继承属性的依赖不能"向右看"或"跨越右兄弟"。L-属性定义的命名来源于其属性可在一个 Left-to-right 深搜遍历（DFS）中完成计算。L-属性定义适合：(a) 自顶向下分析（LL分析）——可即时计算；(b) 自底向上分析（LR分析）配合继承属性的特殊处理。

两者关系：S-属性 ⊂ L-属性（所有 S-属性定义都是 L-属性定义，因为综合属性不涉及继承属性的限制）。实践中 S-属性对 LR 分析最自然；L-属性通过语义动作的适当放置也可在 YACC/Bison 中实现。

## 关键结论

- S-属性 SDD 的计算顺序为后序遍历语法树——最底层最先计算，逐层向上
- L-属性 SDD 可在 DFS（先左子树、再右子树、最后父节点）中完成计算
- 非 L-属性的 SDD 可能需要多遍扫描或先构建完整语法树后按依赖图排序计算
- 在 L-属性 SDD 中，继承属性模拟"上下文从父节点和左兄弟流入当前节点"
- S-属性的典型应用：表达式求值（综合属性 val）、三地址码生成（综合属性 code）
- L-属性的典型应用：类型分析（继承属性传递声明类型）、符号表构建（继承属性传递作用域信息）

## 易错点

1. 误认为自底向上分析只能处理 S-属性：通过引入标记非终结符和适当处理继承属性，YACC 等 LR 分析器也能处理 L-属性 SDD
2. L-属性的"L"不是指左递归：L 指的是 Left-to-right（从左到右遍历属性依赖）
3. 继承属性的不恰当使用：当继承属性需要来自右兄弟的信息时，该 SDD 就不是 L-属性的——需要重写文法或使用两遍扫描

## 例题

**例题1**：判断 SDD 类型。产生式 A → B C, 规则 B.inh = f(A.inh), C.inh = g(B.syn), A.syn = h(C.syn)。

**解答**：B.inh 依赖 A.inh（左部继承属性）√；C.inh 依赖 B.syn（左兄弟综合属性）√；A.syn 依赖 C.syn（子节点综合属性）√。所有依赖都遵循从左到右规则，该 SDD 为 L-属性定义。所有属性均为综合属性（A.syn），且继承属性的依赖方向合法。

**例题2**：为何 L-属性定义中继承属性不能依赖右兄弟？

**解答**：若允许，则单遍从左到右扫描无法计算属性——当处理某符号时需要右兄弟的信息，但右兄弟尚未被处理（属性未知）。这迫使要么预先计算右兄弟（需要前瞻或额外遍），要么改变计算顺序。因此 L-属性定义强制依赖方向与扫描方向一致。

## 代码示例

```python
class LAttributedEvaluator:
    """L-属性SDD的DFS求值"""
    def __init__(self):
        self.values = {}
    
    def evaluate(self, node, inherited=None):
        """对AST节点进行L-属性求值"""
        node.inherited = inherited or {}
        
        if node.type == 'decl':  # 声明语句
            type_val = node.children[0].syn.get('type')
            # 将类型作为继承属性传给变量列表
            self.evaluate(node.children[1], {'type': type_val})
        
        elif node.type == 'var_list':
            for child in node.children:
                child.inherited = node.inherited  # 传递继承属性
                self.evaluate(child, node.inherited)
        
        # 综合属性计算
        if node.type == 'type_int':
            node.syn = {'type': 'int'}
        elif node.type == 'var_id':
            node.syn = {'name': node.lexeme, 'type': node.inherited.get('type')}
        
        return node.syn

print("L-属性定义: 继承属性从左传递到右，综合属性从子传递到父")
```

## 关联页面

[[语法制导定义SDD]] [[语法制导翻译SDT]] [[符号表]] [[类型检查]]
