---
title: "Rust所有权与借用系统"
course: 程序设计
chapter: Rust
difficulty: ADVANCED
tags: [Rust, 所有权, 借用, 生命周期, 内存安全]
aliases: [Rust Ownership, Borrowing]
source: "The Rust Programming Language (Rust Book); Programming Rust (Blandy & Orendorff)"
updated_at: 2026-05-02
---

## 核心定义

Rust的所有权规则：1.每个值只有一个owner 2.值离开作用域时自动释放(drop) 3.同一时刻只能有一个可变引用(&mut T)或多个不可变引用(&T)，但不能同时。生命周期(lifetime)标注：'a等标注编译器不需显式标注大部分但有前提(同生命周期参数，编译器推断)。借用检查器(Borrow Checker)在编译时确保所有引用有效——无use-after-free、无double free、无数据竞争。

## 关键结论

1. move是默认(赋值=所有权转移)，Copy类型(如i32)例外(按位复制) 2. 生命周期标注不改变代码行为仅帮助编译器 3. 智能指针：Box(堆值)、Rc/Arc(共享所有权/引用计数)、RefCell(内部可变性-运行期检查) 4. Unsafe Rust允许绕过借用检查(需要手工保证安全性)

## 关联页面

[[RAII与智能指针]] [[C++移动语义与右值]]
