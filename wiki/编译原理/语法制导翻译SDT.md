---
title: 语法制导翻译SDT
course: 编译原理
chapter: 语义分析
difficulty: INTERMEDIATE
tags: [语法制导翻译, SDT, 翻译模式, 语义动作, 属性计算, 三地址码]
aliases: [Syntax-Directed Translation, SDT, 语法制导翻译模式]
source:
  - Alfred V. Aho《Compilers: Principles, Techniques, and Tools》(龙书)
updated_at: 2026-05-02

---

## 核心定义

语法制导翻译模式（Syntax-Directed Translation Scheme, SDT）是在 CFG 的产生式右部嵌入**语义动作**（Semantic Action）的程序片段，明确指定了属性计算的**求值顺序**。SDT 是 SDD 的具体实现形式——它不仅声明了属性的依赖关系，还规定了属性计算与语法分析步骤的交替顺序。语义动作可出现在产生式右部的任意位置（不像 SDD 仅声明语义规则的位置不限定），以 `{ action }` 表示。语义动作的执行时机结合具体的语法分析方法确定。

SDT 按适于不同的语法分析方法可分为：
- **适于自底向上（LR）分析的 SDT**：所有语义动作放在产生式**末尾**——当产生式被归约时执行，对应于 S-属性定义。在 YACC/Bison 中即为归约动作。
- **适于自顶向下（LL）分析的 SDT**：语义动作可放在产生式右部的**任何位置**——当分析器处理到产生式右部的该位置时执行。这允许在处理完某些符号后进行即时计算。

SDT 常被用来直接从源程序**生成中间代码**（如三地址码）。语义动作可以创建临时变量、生成三地址码指令、构建符号表条目等。SDT 将语法分析和语义处理合成一遍完成，避免了显式构建完整语法树的需要。

## 关键结论

- SDT 在推导或归约的特定时刻触发语义动作——可视为 "解析中的回调函数"
- 将动作放在产生式末尾 → 适于 LR 分析（S-属性 SDT）；动作分散在产生式中 → 适于 LL 分析
- 翻译模式中的动作不能引用尚未计算出的属性——这要求动作与属性依赖之间的一致性
- SDT 使得"一遍编译器"（One-Pass Compiler）成为可能，直接在语法分析过程中生成目标代码
- YACC/Bison 的语法部分本质上就是 SDT 的 LR 实现
- 三地址码生成是 SDT 的经典应用场景

## 易错点

1. 在 LR 分析中把动作放在产生式中间——这需要将产生式拆分引入标记非终结符（Marker Nonterminal），YACC 自动处理但需理解原理
2. 动作中引用尚未计算的属性值——例如在 SDT 中某动作位于产生式位置 i 却引用了位置 j > i 的符号的属性（尚未读入）
3. S-属性 SDT 与非 S-属性 SDT 的混淆——前者只需归约时计算；后者LL分析中在读到特定符号后才触发

## 例题

**例题1**：为表达式文法设计 SDT，直接生成三地址码。

**解答**：
```
E → E₁ + T  { E.place = newtemp(); 
              emit(E.place '=' E₁.place '+' T.place); }
E → T       { E.place = T.place; }
T → T₁ * F  { T.place = newtemp(); 
              emit(T.place '=' T₁.place '*' F.place); }
T → F       { T.place = F.place; }
F → ( E )   { F.place = E.place; }
F → id      { F.place = id.lexeme; }
```
此为 S-属性 SDT，动作放在产生式末尾，适合 LR 分析。属性 `place` 表示该符号对应的临时变量名或标识符名。

**例题2**：对比 SDD 和 SDT 的异同。

**解答**：SDD 是声明式规范——只规定属性之间的依赖关系；SDT 是过程式实现——明确规定了计算时机。SDD 的语义规则未限制执行位置；SDT 的语义动作在产生式中的位置即为执行位置。SDT 更接近实际编译器实现。

## 代码示例

```python
class SDTTranslator:
    """模拟SDT的三地址码生成"""
    def __init__(self):
        self.temp_count = 0
        self.code = []
    
    def new_temp(self):
        self.temp_count += 1
        return f't{self.temp_count}'
    
    def emit(self, instr):
        self.code.append(instr)
    
    def translate_expr(self, tokens):
        """简化SDT: 翻译后缀表达式为三地址码"""
        stack = []
        for tok in tokens:
            if tok.isdigit():
                stack.append(tok)
            elif tok in '+-*':
                b = stack.pop()
                a = stack.pop()
                t = self.new_temp()
                self.emit(f'{t} = {a} {tok} {b}')
                stack.append(t)
        return self.code

translator = SDTTranslator()
code = translator.translate_expr(['3', '5', '+', '2', '*'])
for instr in code:
    print(instr)
# t1 = 3 + 5
# t2 = t1 * 2
```

## 关联页面

[[语法制导定义SDD]] [[S属性与L属性]] [[三地址码]] [[YACC]] [[中间代码生成]]
