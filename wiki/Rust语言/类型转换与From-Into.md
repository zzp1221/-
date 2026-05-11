---
title: "Rust语言-类型转换与From/Into"
course: Rust语言
chapter: 类型系统
difficulty: BASIC
tags: [Rust, From, Into, TryFrom, 类型转换]
aliases: [Rust Type Conversion, From/Into traits, TryFrom]
source: "The Rust Book Ch 9; Rust标准库std::convert文档; Rust Reference: Type coercions"
updated_at: 2026-05-02
---

## 核心定义

""Rust的类型转换体系围绕标准trait：From<T>(不可出错的转换), Into<T>(From的反向,自动派生——impl<T,U:From<T>> Into<U> for T), TryFrom<T>/TryInto<T>(可出错的转换,返回Result)。实现From自动获得Into。使用场景：?操作符通过From转换错误类型, collect()通过FromIterator收集,函数参数通过Into接受多种类型(impl Into<String>接受&str/String)。

## 类型强制转换(Type Coercions)

""编译器在特定位置自动执行类型强制转换(coercion)：1. &T到&dyn Trait(unsized coercion) 2. &mut T到&mut dyn Trait 3. &T到*const T, &mut T到*mut T 4. 非捕获闭包到fn指针 5. Deref强制——&String到&str(通过Deref trait)。as关键字执行显式转换(数字类型转换、指针互转、enum到整数)。as不会像C那样静默截断有符号/无符号转换。

## 关键结论

""1. 库应实现From<T>而非Into(因泛型Into自动派生) 2. 从自己crate的类型到外部类型的From不能实现(孤儿规则) 3. 数值as转换可能产生意外(overflow cast在debug panic,release wrap) 4. transmute是unsafe的类型转换终极武器(仅重新解释内存) 5. 调用arg.into()可接受多种输入类型

## 关联知识点

""[[Rust语言-错误处理与Result]] [[Rust语言-切片与Deref强制]] [[Rust语言-泛型与Trait]]
