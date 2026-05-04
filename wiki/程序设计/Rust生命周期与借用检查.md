---
title: Rust生命周期与借用检查
course: 程序设计
chapter: 内存安全
difficulty: ADVANCED
tags: [程序设计, Rust, 生命周期, 借用检查, 所有权]
aliases: [Lifetime, Borrow Checker, Rust借用]
source:
  - Rust官方文档（The Rust Programming Language）
  - 《Rust程序设计语言》
  - Rustonomicon
updated_at: 2026-05-03
---

## 核心定义

Rust的所有权系统是编译期内存安全保证的核心，由三部分组成：(1)所有权规则：每个值有且只有一个所有者，所有者离开作用域时值被丢弃（drop）；(2)借用规则：任意时刻要么有一个可变引用（&mut T），要么有任意多个不可变引用（&T），引用必须始终有效（不能悬垂）；(3)生命周期（Lifetime）：编译器追踪引用的有效范围，确保引用不会比它指向的数据活得更长。生命周期标注语法`'a`不改变引用的实际寿命，只是帮助编译器理解多个引用之间的关系。生命周期省略规则（Lifetime Elision）：编译器在大多数情况下自动推断生命周期，无需手动标注。需要手动标注的场景：函数返回引用且参数有多个引用时。结构体包含引用时必须标注生命周期：`struct Foo<'a> { data: &'a str }`。'static生命周期表示整个程序运行期间有效（如字符串字面量）。NLL（Non-Lexical Lifetimes）：引用的生命周期在最后一次使用后结束（不是作用域结束），减少了不必要的借用冲突。

## 关键结论

- Rust的所有权系统在编译期消除了：悬垂指针、数据竞争、双重释放、内存泄漏（大部分）
- 借用检查器（Borrow Checker）是Rust编译器的核心组件，在编译期强制执行借用规则
- 生命周期不增加运行时开销：完全是编译期检查，零成本抽象
- 与C++的智能指针（shared_ptr/unique_ptr）相比，Rust的所有权在编译期检查，无运行时开销
- Pin<T>和Unpin trait用于处理自引用结构（如async/await生成的状态机）

## 易错点

1. 生命周期不是作用域：NLL使生命周期在最后一次使用后结束，不是花括号结束
2. `&mut T`的排他性：在可变引用存活期间，不能有其他任何引用（包括不可变引用）
3. 所有权转移（Move）后原变量不可用：这与C++的拷贝语义不同

## 例题

**例1：** 解释以下Rust代码为什么编译失败并修复：
```rust
fn longest(x: &str, y: &str) -> &str {
    if x.len() > y.len() { x } else { y }
}
```

**解答：** 编译失败原因：编译器不知道返回值的生命周期与x还是y相关。如果返回值的生命周期与x相同但实际返回了y，而y的生命周期比x短，就会产生悬垂引用。修复：添加生命周期标注`fn longest<'a>(x: &'a str, y: &'a str) -> &'a str`，告诉编译器返回值的生命周期与x和y中较短的那个相同。调用时：`let result; let s1 = String::from("long"); { let s2 = String::from("xyz"); result = longest(s1.as_str(), s2.as_str()); } // s2已drop，result不可用`。生命周期标注确保编译器能检查这种安全性。

## 关联页面

[[Rust所有权与借用]] [[RAII与资源管理]] [[内存模型-栈与堆]]
