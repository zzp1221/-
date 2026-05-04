---
title: "C++移动语义与右值引用"
course: 程序设计
chapter: C++
difficulty: ADVANCED
tags: [C++, 移动语义, 右值引用, std::move, 完美转发]
aliases: [Move Semantics]
source: "The C++ Programming Language (Stroustrup) 4th Ed; Effective Modern C++ (Meyers)"
updated_at: 2026-05-02
---

## 核心定义

右值引用(T&&)是C++11的核心语言特性，使移动语义成为可能。左值(lvalue)：有身份可寻址(如变量)；右值(rvalue)：临时对象/字面量(如x+y、42)。std::move将左值(无条件)转为右值引用(允诺'我不再使用')。std::forward<T>根据T的推导类型完美转发(左值/右值)。移动构造函数/移动赋值从源对象'窃取'资源（通常是指针赋值+源指针置null），避免深拷贝。

## 关键结论

1. 移动操作应为noexcept(在vector增长时异常安全保证) 2. std::move后源对象处于valid-but-unspecified状态(可调用不依赖具体值的函数) 3. 返回值优化(RVO/NRVO)在回临时本地变量时自动消除拷贝/移动

## 关联页面

[[RAII与智能指针]] [[Rust所有权与借用]] [[C++模板与泛型]]
