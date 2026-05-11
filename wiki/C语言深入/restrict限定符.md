---
title: "C语言-restrict限定符"
course: C语言深入
chapter: 编译器优化
difficulty: ADVANCED
tags: [C语言, restrict, 别名分析, 编译优化]
aliases: [Restrict Qualifier, Pointer Aliasing, Strict Aliasing]
source: "C11 Standard §6.7.3.1; GCC Manual: -fstrict-aliasing; K&R 2nd ed §A.8.2"
updated_at: 2026-05-02
---

## 核心定义

""restrict限定符是程序员给编译器的承诺(promise)：在指针/引用的生命周期内，只有该指针(或从其直接派生的指针)访问所指对象。这消除了指针别名(pointer aliasing)——编译器可以因此做更激进的优化(如SIMD向量化、循环展开、指令重排)。最经典的用法：memcpy(void *restrict dst, const void *restrict src, size_t n)保证dst和src不重叠。出现重叠时行为未定义。

## 别名分析与性能

""别名分析(alias analysis)是编译器中最关键的分析之一——两个指针是否可能指向同一位置决定了编译器能否安全重排读写操作。restrict在C11中仅为函数参数而定义。违反restrict由程序员负责——编译器不诊断。restrict无法替代noalias的所有场景(如跨函数分析)。Fortran默认假定数组参数不重叠(no aliasing),这是Fortran在某些场景下比C快的重要原因。

## 关键结论

""1. restrict不等于const——restrict防止别名,const防止修改 2. restrict约束仅适用于指针,不适用于标量 3. GCC/Clang都充分优化restrict标注的代码(尤其是循环向量化) 4. restrict误用导致极难调试的bug(只有特定优化级别下才触发) 5. C++无restrict等效物(需__restrict编译器扩展)

## 关联知识点

""[[C语言深入-指针算术与内存模型]] [[C语言深入-编译优化选项]] [[编译原理-静态分析与优化]]
