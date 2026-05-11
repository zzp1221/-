---
title: "Rust语言-错误处理与Result"
course: Rust语言
chapter: 语言设计
difficulty: BASIC
tags: [Rust, Result, ?, 错误传播, Option]
aliases: [Rust Error Handling, Result<T,E>, ? operator]
source: "The Rust Book Ch 9; Rust标准库std::result/std::error文档; RFC 1937 (? operator)"
updated_at: 2026-05-02
---

## 核心定义

""Rust没有异常机制，使用Result<T,E>枚举表达可恢复错误(Ok(T)或Err(E)),panic!表达不可恢复错误。?操作符(早期返回)自动解包Ok值或将Err向上传播：let x = f()?; 等价于 let x = match f() { Ok(v) => v, Err(e) => return Err(e.into()) };。?操作符调用From trait自动转换错误类型。main函数可返回Result<(), Box<dyn Error>>。

## 错误类型设计

""std::error::Error trait是基础错误接口：fn source(&self) -> Option<&(dyn Error + 'static)>支持错误链(链式包装)。thiserror派生宏提供自动Error实现(derive(Error) + Display)。anyhow提供类型擦除的错误容器(anyhow::Result<T> = Result<T, anyhow::Error>)适合应用层。thiserror适合库的精确错误类型，anyhow适合应用的通用错误处理。错误不应被吞掉——_.unwrap()/_.expect()在库代码中不推荐。

## 关键结论

""1. ?操作符仅可用于返回Result/Option的函数中 2. Result的ok()/err()方法转换为Option 3. map_err()修改错误类型但不影响Ok值 4. unwrap_or()/unwrap_or_else()提供默认值 5. 组合Result: and_then/flat_map式的链组合

## 关联知识点

""[[Rust语言-模式匹配与枚举]] [[Rust语言-Option与空值安全]] [[Go语言-错误处理哲学]]
