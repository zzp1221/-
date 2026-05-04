---
title: "抽象语法树（AST）设计"
course: 编译原理
chapter: 语法分析
difficulty: INTERMEDIATE
tags: [编译原理, AST, 语法树, 语义分析]
aliases: [Abstract Syntax Tree]
source: "Compilers: Principles, Techniques, and Tools (Dragon Book) 第4-5章"
updated_at: 2026-05-02
---

## 核心定义

AST是源代码的树形表示，去掉语法细节(分号/括号/关键字)只保留语义信息。每个节点类型对应语言构造(If/While/Assign/Call/BinaryOp)。CST(具体语法树/解析树)包含所有语法细节。AST通过语法制导翻译在parse过程中构建：每个产生式关联语义动作(创建AST节点+连接子节点)。

## 关键结论

1. AST是后续所有分析和转换的基础 2. Clang/TypeScript Compiler API提供遍历AST的visitor模式 3. AST序列化为文本可以跨语言交换(如Babel解析JS→AST→转换→generate) 4. 符号表通常在AST遍历时填充

## 关联页面

[[语法分析]] [[语义分析]] [[三地址码与中间表示IR]]
