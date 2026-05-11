---
title: "Rust语言-模块与Crate组织"
course: Rust语言
chapter: 工程构建
difficulty: BASIC
tags: [Rust, module, crate, visibility, workspace]
aliases: [Rust Module System, Crate Organization, pub/use]
source: "The Rust Book Ch 7; Rust Reference: Crates and source files; Cargo Book"
updated_at: 2026-05-02
---

## 核心定义

""Rust的模块系统有三层：crate(编译单元, lib或bin)、module(命名空间,用mod声明/引入)、use(导入路径别名)。每个Rust文件隐式创建同名的module(lib.rs是库根,main.rs是二进制根)。mod关键字定义新模块(可内联或关联文件/目录)。可见性：pub使项公开，pub(crate)限制crate内可见，pub(super)父模块可见，pub(in path)特定路径可见，默认私有。

## Re-export与use惯用法

""use语句导入路径作为快捷方式(use std::collections::HashMap;)。惯用风格：函数导入到父模块级别(use my_mod::some_func;)，struct/enum导入到类型级别(use my_mod::MyStruct;)。pub use(重新导出)改变公开API的路径——可对外隐藏内部结构重新组织。use path::{self, A, B}同时导入模块和子项。prelude模式在lib.rs中集中导出常用类型。

## 关键结论

""1. 模块不通过文件系统反射——Rust文件路径需匹配mod声明而非目录 2. use as提供别名 3. glob导入(use xxx::*)不推荐在公开API中使用 4. extern crate语法已过时(2018 edition) 5. Cargo workspace管理多crate项目共享受依赖

## 关联知识点

""[[Rust语言-cargo与依赖管理]] [[Rust语言-泛型与Trait]] [[软件工程-软件架构设计]]
