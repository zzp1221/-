---
title: LEX工具
course: 编译原理
chapter: 词法分析
difficulty: INTERMEDIATE
tags: [LEX, Flex, 词法分析器生成器, 正则表达式, C语言, lex.yy.c]
aliases: [Lex, Flex, 词法分析生成器, Scanner Generator]
source:
  - Alfred V. Aho《Compilers: Principles, Techniques, and Tools》(龙书)
updated_at: 2026-05-02
---

## 核心定义

LEX（Lexical Analyzer Generator）是经典的词法分析器自动生成工具，由 M.E. Lesk 和 E. Schmidt 于 1975 年在贝尔实验室开发。其开源版本 Flex（Fast Lexical Analyzer Generator）是目前最广泛使用的 LEX 兼容工具。LEX 接受一个 `.l` 源文件（包含以正则表达式描述的词法规则），自动生成一个 C 语言源文件 `lex.yy.c`，其中包含了词法分析器的完整实现（即一个 DFA 驱动程序）。

LEX 源文件的结构分为三部分，以 `%%` 分隔：
```
{定义部分}
%%
{规则部分}
%%
{用户代码部分}
```

**定义部分**包括：C 代码块（`%{...%}`内含头文件、全局变量等）、正则表达式的宏定义（如 `DIGIT [0-9]`）、起始状态声明等。**规则部分**是 LEX 程序的核心：每一行格式为 `模式 {动作}`，模式是正则表达式，动作是 C 代码。LEX 按最长匹配原则（Longest Match）选择匹配的模式；若多个模式匹配相同长度，则选择在文件中出现最早的那个。**用户代码部分**包含辅助函数（如 `main()`、`yywrap()` 等）。

LEX 生成的词法分析器提供一个核心函数 `yylex()`，每次调用返回下一个 Token 的种别码，全局变量 `yytext` 保存当前 Token 的文本，`yyleng` 保存其长度。

## 关键结论

- LEX 将正则表达式翻译为 NFA（Thompson 构造法），再转化为 DFA（子集构造法），最后最小化并生成驱动表
- LEX 内部维持 DFA 的状态转移表，驱动程序是一个简单的 while 循环
- 最长匹配原则：若输入前缀同时匹配多个模式，LEX 取消耗字符最多的匹配
- 当需要将 Token 的种别码传递给语法分析器时，LEX 通常与 YACC/Bison 联合使用，种别码定义在共享头文件中
- 起始状态（Start Conditions）允许 LEX 在不同上下文下使用不同的规则集，如处理注释和字符串有不同的规则
- Flex 相比原始 LEX 有诸多改进：更快的扫描速度、更好的错误恢复、支持 C++

## 易错点

1. 正则表达式中的转义字符：在 LEX 中 `+` `*` `?` `|` `.` `()` `[]` 等都是元字符，匹配字面量时需要转义为 `\+` `\*` 等，或用双引号括起如 `"+"`
2. 规则顺序导致冲突：当两个模式匹配相同长度时，LEX 选择先出现的规则——因此关键字规则必须在标识符规则之前
3. `yytext` 是指针，其内容在下次调用 `yylex()` 时会被覆盖——如需保留 Token 文本，应立即复制

## 例题

**例题1**：编写 LEX 程序识别 C 语言的单行和多行注释。

**解答**：
```
%%
"//".*              { /* skip single-line comment */ }
"/*"([^*]|"*"[^/])*"*/"  { /* skip multi-line comment */ }
```

单行注释 `//` 后跟任意直到行尾的字符。多行注释中 `([^*]|"*"[^/])*` 匹配任意不含 `*/` 的字符串。

**例题2**：LEX 中如何实现字符串常量的识别（含转义字符）？

**解答**：
```
%%
\"(\\.|[^"\\])*\"  { 
    /* 处理字符串常量，yytext 包含双引号 */
    return STRING_LITERAL; 
}
```
其中 `\\.` 匹配任意转义字符（如 `\n`, `\"`, `\\`），`[^"\\]` 匹配非特殊普通字符。

## 代码示例

```c
/* 简单 LEX 文件示例: demo.l */
%{
#include <stdio.h>
int word_count = 0;
%}

%%
[a-zA-Z]+   { word_count++; printf("Word: %s\n", yytext); }
[0-9]+      { printf("Number: %s\n", yytext); }
[ \t\n]     { /* skip whitespace */ }
.           { printf("Other: %s\n", yytext); }
%%

int main(int argc, char **argv) {
    yylex();
    printf("Total words: %d\n", word_count);
    return 0;
}

int yywrap() { return 1; }
```

编译和执行：
```bash
flex demo.l          # 生成 lex.yy.c
gcc lex.yy.c -lfl    # 编译
./a.out < input.txt  # 运行
```

## 关联页面

[[词法分析]] [[正规式与正规文法]] [[DFA]] [[YACC]] [[编译概述]]
