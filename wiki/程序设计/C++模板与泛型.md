---
title: "C++模板与泛型编程"
course: 程序设计
chapter: C++
difficulty: ADVANCED
tags: [C++, 模板, 泛型, 元编程, SFINAE]
aliases: [C++ Templates, Generic Programming]
source: "C++ Templates: The Complete Guide (Vandevoorde & Josuttis); Effective Modern C++ (Meyers)"
updated_at: 2026-05-02
---

## 核心定义

函数模板：编译器根据调用实参推导模板参数(隐式实例化)。类模板：编译时生成具体类型版本。特化：全特化(为特定类型提供完全不同的实现)和偏特化(部分参数特化，仅类模板支持)。SFINAE(Substitution Failure Is Not An Error)：模板替换失败不报错而只是从候选集中排除——enable_if/void_t/if constexpr利用此实现编译期条件。Variadic template：参数包+递归展开(折叠表达式C++17简化)。Concept(C++20)：约束模板参数提供更好的错误信息。

## 关键结论

1. 模板是图灵完备的(模板元编程) 2. 头文件包含模板定义(无法分离编译) 3. Concepts让模板的错误信息从数百行变为几行 4. CTAD(类模板实参推导)C++17起可用

## 关联页面

[[C++移动语义与右值]] [[RAII与智能指针]] [[编译期计算]]
