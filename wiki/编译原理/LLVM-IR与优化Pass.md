---
title: "LLVM IR与优化Pass"
course: 编译原理
chapter: 编译器框架
difficulty: ADVANCED
tags: [编译原理, LLVM, IR, Pass, 优化]
aliases: [LLVM IR, Optimization Pass, SIL]
source: "LLVM官方文档; Lattner & Adve 2004 (LLVM paper);《Getting Started with LLVM Core Libraries》"
updated_at: 2026-05-02
---

## 核心定义

LLVM IR(中间表示)是LLVM编译框架的核心——基于SSA(Static Single Assignment)形式的类型化低级表示。每个变量精确赋值一次(通过phi节点在控制流合并处选择不同来源的值)。LLVM IR三级：内存表示(in-memory——C++ API)、bitcode(.bc——磁盘存储)、汇编文本(.ll——可读格式)。Pass系统将优化组织为模块化的pass——每pass读取/修改IR然后传递到下一pass。Pass Manager(新PM)按依赖和阶段管理pass调度——Analysis passes提供分析结果(别名/支配树/loop info)。

## 经典Pass范例

最重要的LLVM优化pass：1.)mem2reg——将alloca/load/store提升为SSA寄存器(将栈变量转为虚寄存器) 2.)GVN(Global Value Numbering)——消除冗余计算(值等价) 3.)LICM(Loop Invariant Code Motion)——将循环不变量移到循环前 4.)Loop Unswitch——将循环内条件分支提升为循环外的两个循环 5.)InstCombine——指令级别的窥孔优化(千条规则)。LTO(Link-Time Optimization)通过IR在链接时重新应用全程序优化pass(ThinLTO平衡优化效果和可伸缩性)。

## 关键结论

1. LLVM IR不是可移植汇编——它是编译器优化的输入/输出语言 2. PGO(Profile-Guided Optimization)向优化pass提供运行时数据 3. 自定义pass可编写(如添加特定领域的优化) 4. LLVM的IR独立性将前端(Clang, Rust, Swift)和后端(x86/ARM/RISC-V)彻底解耦 5. Opaque pointer(LLVM 15+)简化IR——不再需要每个指针声明类型

## 关联知识点

[[编译原理-JIT编译原理]] [[编译原理-语法树与中间表示]] [[C语言深入-编译优化选项]]
