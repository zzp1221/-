---
title: "Rust语言-闭包与Fn特征"
course: Rust语言
chapter: 函数式编程
difficulty: INTERMEDIATE
tags: [Rust, 闭包, Fn, FnMut, FnOnce]
aliases: [Rust Closures, Fn traits, Move Closures]
source: "The Rust Book Ch 13; Rust Reference: Closure expressions; Rust标准库std::ops"
updated_at: 2026-05-02
---

## 核心定义

""Rust闭包是捕获环境的匿名函数：|params| { body }。编译器为每个闭包生成唯一的匿名类型(不能直接命名)，该类型实现Fn/FnMut/FnOnce trait中的至少一个。Fn调用通过&self(不可变引用)访问捕获变量。FnMut通过&mut self(可变引用)。FnOnce通过self(所有权转移)。闭包自动(且保守地)推导实现哪些trait——如果闭包消耗了捕获变量只能FnOnce,修改了捕获变量可以FnMut。

## move闭包与捕获

""move关键字强制闭包获取所有引用变量的所有权(而非借用)。使用场景：线程spawn、异步任务、所有权逃离当前作用域的闭包。闭包捕获的方式：1.捕获不可变引用(最宽松) 2.捕获可变引用 3.按值移动(所有权转移)。编译器遵循最小权限原则选择捕获方式。函数指针fn(i32) -> i32和闭包是不同的——但非捕获闭包可自动强制转换为fn指针。

## 关键结论

""1. FnOnce是三个trait的父trait——所有闭包至少FnOnce 2. 接受闭包的函数用泛型+where约束最灵活 3. Box<dyn Fn()>存储不同类型闭包的堆分配 4. 迭代器适配器接受FnMut闭包(map/filter) 5. 闭包默认不要求Send/Sync除非推导要求(如tokio::spawn)

## 关联知识点

""[[Rust语言-迭代器与组合器]] [[Rust语言-async/await与Future]] [[Rust语言-所有权与借用]]
