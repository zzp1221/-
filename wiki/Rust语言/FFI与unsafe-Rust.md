---
title: "Rust语言-FFI与unsafe Rust"
course: Rust语言
chapter: 系统编程
difficulty: ADVANCED
tags: [Rust, FFI, unsafe, extern C, C ABI]
aliases: [Rust FFI, Unsafe Rust, Foreign Function Interface]
source: "The Rustonomicon; Rust Reference: Unsafe operations; RFC 2045 (target_feature 1.1)"
updated_at: 2026-05-02
---

## 核心定义

""Rust的unsafe块是超级用户模式(superpowers)：可执行5种额外操作——1.解引用裸指针 2.调用unsafe函数/方法 3.访问/修改可变全局变量 4.实现unsafe trait 5.访问union字段。unsafe并不意味着不安全——它表示由程序员而非编译器保证安全。unsafe块应封装在安全抽象后并用// SAFETY注释解释安全理由。extern块声明FFI接口：extern "C" fn。

## FFI实践与ABI

""Rust通过extern声明与C ABI互操作。#[no_mangle]禁止名称修饰(mangling)。extern 'C'使用C调用约定。#[repr(C)]确保结构体布局与C兼容。将Rust回调传递给C时需注意生命周期——Box::into_raw+Box::from_raw管理堆分配。libc crate提供C类型别名。cbindgen工具自动生成C头文件。Deref强化将*mut T/&mut T自动转换。Rust的无效值优化(null pointer optimization)使Option<&T>与&T同大小。

## 关键结论

""1. unsafe缩小范围——越小的unsafe块越容易审查 2. 确保FFI中所有权不跨语言边界泄漏 3. catch_unwind在FFI边界防止panic穿越(panic unwind over FFI is UB) 4. std::ffi::CStr/CString管理C字符串 5. null_mut()/NonNull提供非空裸指针保证

## 关联知识点

""[[Rust语言-所有权与借用]] [[Rust语言-并发原语与Send/Sync]] [[C语言深入-链接器与ABI详解]]
