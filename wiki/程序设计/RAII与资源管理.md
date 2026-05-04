---
title: "RAII与智能指针"
course: 程序设计
chapter: C++/Rust
difficulty: INTERMEDIATE
tags: [C++, RAII, 智能指针, 所有权, Rust]
aliases: [Resource Acquisition Is Initialization]
source: "The C++ Programming Language (Stroustrup); Effective C++; Rust Book"
updated_at: 2026-05-02
---

## 核心定义

RAII(资源获取即初始化)是C++/Rust的资源管理核心思想：将资源的生命周期绑定到对象的生命周期。构造函数获取资源，析构函数释放资源——绝不手动释放。C++智能指针：unique_ptr(独占所有权，move-only)、shared_ptr(共享所有权，引用计数+控制块)、weak_ptr(观察不增加计数，lock升级为shared_ptr)。Rust：所有权规则(一个值一个owner)+借用(引用不过期于owner)+生命周期标注——编译期保证无use-after-free/双free/数据竞争。

## 关键结论

1. make_unique/make_shared比直接new更安全(异常安全+单次分配) 2. shared_ptr控制块独立于对象(weak_ptr可感知对象已销毁) 3. Rust的所有权系统是RAII+借用检查器的静态实现

## 关联页面

[[Rust所有权与借用]] [[C++移动语义]] [[垃圾回收算法]]
