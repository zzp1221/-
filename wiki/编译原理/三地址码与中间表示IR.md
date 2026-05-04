---
title: "三地址码与中间表示IR"
course: 编译原理
chapter: 中间代码生成
difficulty: ADVANCED
tags: [编译原理, 三地址码, 中间表示, IR, LLVM]
aliases: [Three-Address Code, IR]
source: "Compilers: Principles, Techniques, and Tools (Dragon Book) 第6章; LLVM Language Reference"
updated_at: 2026-05-02
---

## 核心定义

三地址码(TAC)是中间表示，每条指令最多3个地址(2源1目标)：x=y op z。常见TAC指令：赋值x=y、双目x=y op z、单目x=op y、无条件goto L、条件if x relop y goto L、过程param x;call p,n、索引x=y[i]和x[i]=y、地址/指针x=&y;x=*y;*x=y。LLVM IR是SSA形式的三地址码(每个变量只赋值一次)。

## 关键结论

1. TAC是AST和目标代码之间的桥梁 2. LLVM IR被Clang/Rust/Swift/Julia等广泛使用 3. SSA简化了数据流分析和优化 4. Java Bytecode也是变体TAC(栈式而非寄存器式)

## 关联页面

[[静态单赋值SSA]] [[语法树]] [[代码优化综合]]
