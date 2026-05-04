---
title: "GCC与LLVM编译器架构对比"
course: 编译原理
chapter: 编译器综述
difficulty: INTERMEDIATE
tags: [编译原理, GCC, LLVM, 编译器架构]
aliases: [GCC vs LLVM]
source: "LLVM官方文档; GCC Internals文档"
updated_at: 2026-05-02
---

## 核心定义

GCC(1987)：传统三阶段设计——前端(语言特有)/中端(GIMPLE IR+优化passes)/后端(RTL→目标码)。单体架构，各pass紧耦合。LLVM(2000s)：模块化设计——前端(Clang)→LLVM IR(SSA形式，bitcode)→中端优化passes→后端(Legalization→ISel→寄存器分配→MC层)。IR分层设计(high/low level)，各pass独立运行。重要区别：LLVM是库(libLLVM/libClang)而非工具——可嵌入IDE/JIT中。

## 关键结论

1. LLVM的IR设计是其最大优势：可读、可序列化(LTO)、JIT可用 2. Clang提供更好的错误信息(准确的源码位置+修复建议) 3. LLVM JIT使Julia/Swift/Python(CPython正迁移到LLVM)等高性能动态语言成为可能 4. GCC仍广泛用于Linux内核构建

## 关联页面

[[三地址码与中间表示IR]] [[静态单赋值SSA]] [[JIT编译技术]]
