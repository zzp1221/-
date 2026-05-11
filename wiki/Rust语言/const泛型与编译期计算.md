---
title: "Rust语言-const泛型与编译期计算"
course: Rust语言
chapter: 类型系统
difficulty: ADVANCED
tags: [Rust, const generics, const fn, 编译期计算]
aliases: [Rust Const Generics, Const fn, Compile-time Computation]
source: "Rust Reference: Const generics; RFC 2000 (const generics); Rust Blog: const generics MVP"
updated_at: 2026-05-02
---

## 核心定义

""Const泛型(const generics)允许将编译期已知的常量值作为类型参数：fn foo<const N: usize>() -> [i32; N]。这使得编译期确定大小的数组成为一等公民(如[T; N]实现所有需要的trait)。Rust 1.51+支持基础const泛型。const fn可以在编译期执行(如计算数组初始化值、const上下文中的函数调用)。const表达式中可用的操作有限(不能使用for/loop/while/if let)。

## 编译期计算能力

""const fn中可用：基本算术、分支(if/else)、match、const泛型参数、其他const fn调用。不能使用迭代器(部分可用在nightly)、可变引用、分配内存。const泛型可配合typenum crate进行类型级Nat数运算。数组[0; N]属于const泛型的基础用例。const_evaluatable_unchecked提供更多编译期计算。CTFE(Compile-Time Function Evaluation)在MIR层面进行。

## 关键结论

""1. const泛型实现数组大小泛型化——之前只能通过宏或impl_for_len! 2. const fn不能分配堆内存 3. 不稳定特性const_generic_defaults支持const参数的默认值 4. const block(在稳定化中)允许在非const函数中执行const求值 5. 编译期计算不会影响运行时性能(完全在编译期完成)

## 关联知识点

""[[Rust语言-泛型与Trait]] [[Rust语言-所有权与借用]] [[编译原理-静态分析与优化]]
