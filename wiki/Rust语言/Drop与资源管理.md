---
title: "Rust语言-Drop与资源管理"
course: Rust语言
chapter: 内存管理
difficulty: INTERMEDIATE
tags: [Rust, Drop, RAII, 资源管理, ManuallyDrop]
aliases: [Rust Drop Trait, RAII, ManuallyDrop]
source: "The Rust Book Ch 15; Rust Reference: Destructors; The Rustonomicon: Drop check"
updated_at: 2026-05-02
---

## 核心定义

""Rust通过RAII(Resource Acquisition Is Initialization)管理资源：资源在获取时绑定到变量的生命周期，在变量离开作用域时自动释放。Drop trait定义释放逻辑：fn drop(&mut self)——编译器自动插入drop调用。释放顺序：结构体字段按声明顺序逆序释放。std::mem::drop(v)主动释放变量(将所有权移入drop函数使变量提前离开作用域,drop函数的空body触发实际Drop)。

## drop检查与Pin

""drop checker防止释放悬垂引用：检查结构体释放时其字段是否仍被其他作用域引用。否则编译报错。ManuallyDrop<T>包装器跳过Drop(用于FFI或复制语义的场景)。Pin<&mut T>与drop的交互——!Unpin的值在Pin后不能安全移动,包括提前drop(需要unsafe Pin::into_inner_unchecked)。mem::forget(v)泄漏内存(消费所有权但不drop),用于FFI所有权转移场景。

## 关键结论

""1. 不能显式调用drop(编译器调用)——使用std::mem::drop预防 2. 实现Copy trait的类型不应实现Drop(Copy语义与Drop冲突) 3. Vec::clear()调用所有元素的drop 4. std::mem::replace/swap可以安全清理资源 5. 递归drop可能导致栈溢出(链表——改用迭代式drop)

## 关联知识点

""[[Rust语言-所有权与借用]] [[Rust语言-FFI与unsafe Rust]] [[C语言深入-指针算术与内存模型]]
