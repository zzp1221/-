---
title: YACC
course: 编译原理
chapter: 语法分析
difficulty: ADVANCED
tags: [YACC, Bison, 语法分析器生成器, LALR1, 移进-归约冲突, %left, %prec]
aliases: [Yet Another Compiler Compiler, Bison, Parser Generator]
source:
  - Alfred V. Aho《Compilers: Principles, Techniques, and Tools》(龙书)
updated_at: 2026-05-02

---

## 核心定义

YACC（Yet Another Compiler Compiler）是经典的语法分析器自动生成工具，由 Stephen C. Johnson 于 1975 年在贝尔实验室开发。Bison 是其 GNU 兼容替代品。YACC 接受一个 `.y` 源文件（包含以类 BNF 记号的 CFG 描述），自动生成一个 LALR(1) 语法分析器的 C 源代码文件 `y.tab.c`。YACC 通常与词法分析器生成器 LEX/Flex 配套使用（YACC 通过调用 `yylex()` 获取 Token）。

YACC 源文件结构与 LEX 类似，以 `%%` 分隔为三部分：
```
{定义部分}
%%
{规则部分}
%%
{用户代码部分}
```

定义部分包含：C 代码块（`%{...%}`）、Token 声明（`%token`）、结合性和优先级声明（`%left`, `%right`, `%nonassoc`）、开始符号声明（`%start`）和联合体类型声明（`%union`）。规则部分包含以 BNF 记号书写的产生式，每条产生式可附带语义动作（以 `{...}` 括起的 C 代码，在归约时执行）。YACC 使用 `$$` 表示产生式左部的属性值，`$1, $2, ...` 表示产生式右部各符号的属性值。

YACC 的关键特性是冲突解决机制：(1) 优先级和结合性声明（`%left`, `%right`, `%prec`）解决移进-归约冲突——比较产生式和输入符号的优先级；(2) 默认解决策略：移进-归约冲突默认选择**移进**，归约-归约冲突默认选择**先出现的产生式**。

## 关键结论

- YACC 生成的是 LALR(1) 分析器——兼顾了分析能力和状态数量
- YACC 允许二义文法通过优先级/结合性声明消歧——这大大简化了表达式文法的书写
- `%left` 声明左结合，`%right` 声明右结合，声明顺序从低到高优先级递增
- 语义动作在产生式被归约时执行——这正是 S-属性语法制导翻译的实现
- 冲突报告信息（`y.output` 文件或 `--verbose` 选项）是调试文法的重要工具
- YACC 的错误处理：特殊 Token `error` 可嵌入产生式中，用于 panic-mode 错误恢复
- YACC 中的动作代码可访问 `yylval`（Token 的属性值）和位置信息

## 易错点

1. 结合性声明顺序颠倒：YACC 中越**后面**声明的结合性优先级**越高**——如先 `%left '+'` 后 `%left '*'` 表示 * 优先级高于 +
2. `%prec` 的使用场景：为特定产生式赋予不同于默认的优先级——如一元减号产生式可能需要比二元减更高的优先级
3. `$$` 的默认类型：若未使用 `%union` 或 `%type`，`$$` 默认为 int 类型——在处理复杂属性时需检查类型

## 例题

**例题1**：编写一个简单计算器的 YACC 文件。

**解答**：
```yacc
%{
#include <stdio.h>
%}
%token NUM
%left '+' '-'
%left '*' '/'
%%
expr: expr '+' expr { $$ = $1 + $3; }
    | expr '-' expr { $$ = $1 - $3; }
    | expr '*' expr { $$ = $1 * $3; }
    | expr '/' expr { $$ = $1 / $3; }
    | '(' expr ')'  { $$ = $2; }
    | NUM           { $$ = $1; }
    ;
%%
```
注意该文法有二义性，但通过 `%left` 声明自动解决。

**例题2**：YACC 报告中 `shift/reduce conflict` 的含义是什么？如何解决？

**解答**：移进-归约冲突指某个状态下分析器既可以选择移进当前 Token 也可以选择归约某个产生式。YACC 默认选择移进。解决：(1) 用 `%left`/`%right` 声明优先级（若冲突涉及运算符）；(2) 用 `%prec` 覆盖特定产生式的优先级；(3) 重写文法消除歧义。

## 关联页面

[[LEX工具]] [[自底向上LR0与SLR1]] [[LR1与LALR1]] [[语法制导翻译SDT]] [[编译概述]]
