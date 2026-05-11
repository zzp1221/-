---
title: "Rust语言-Trait系统与泛型"
course: Rust语言
chapter: 类型系统
difficulty: ADVANCED
tags: [Rust, trait, 泛型, 静态分发, 动态分发, 关联类型]
aliases: [Traits, Generics, Static Dispatch, Dynamic Dispatch]
source: "The Rust Reference §10-11; Rust RFC 0195 (Associated Items)"
updated_at: 2026-05-02
---

## 核心定义

Rust的Trait定义了类型间共享的行为契约。类似Haskell的typeclass但更接近OOP接口的思想。trait约束：fn f<T: Trait1 + Trait2>(x: T)限制T必须实现这些trait。Blanket implementations：为满足条件的类型自动实现trait (impl<T: Display> ToString for T)。Orphan rule：实现trait时至少trait或类型之一必须在当前crate中定义，防止上游库冲突。

## 静态分发 vs 动态分发

静态分发(monomorphization): 编译器为每种具体类型生成特化代码，完全消除trait调用开销(类C++模板)。动态分发: trait object (dyn Trait)使用胖指针(数据指针+vtable指针)，调用通过vtable间接跳转。Sized默认约束：大多数泛型参数默认要求Sized。?Sized放宽约束允许DST(Dynamically Sized Types)。

## 关联类型与GAT

关联类型(type Item/type Output): 将trait的类型参数提升为类型成员，减少类型推导复杂度。GAT(Generic Associated Types, Rust 1.65+): 关联类型可以有自己的生命周期和类型参数，如trait LendingIterator { type Item<'a> where Self: 'a; ... }。

## 关联知识点

[[Rust语言-所有权与生命周期]] [[Rust语言-智能指针与内部可变性]]
