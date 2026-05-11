---
title: "Rust语言-切片与Deref强制"
course: Rust语言
chapter: 类型系统
difficulty: INTERMEDIATE
tags: [Rust, 切片, Deref, unsized coercion, &[T]]
aliases: [Rust Slices, Deref Coercions, Unsized Coercion]
source: "The Rust Book Ch 15; Rust Reference: Type coercions; The Rustonomicon: Exotic Sizes"
updated_at: 2026-05-02
---

## 核心定义

""切片(slice)是对连续序列[T]的引用视图：&[T](不可变切片)和&mut [T](可变切片)。切片不拥有数据——它仅是(ptr, len)的fat pointer(胖指针,16字节在64位系统——相比普通指针8字节)。Vec<T>可Deref到&[T],因此所有接受&[T]的函数同时接受&Vec<T>。str类型是[u8]切片的不同UTF-8保证的'视图'——&str是切片引用(Deref: String→&str)。

## Deref强制详解

""Deref trait(fn deref(&self) -> &Self::Target)允许类型在被解引用时返回另一个类型的引用。编译器在函数调用、方法调用、字段访问时自动插入*和解引用操作(最多应用一次Deref)。DerefMut对应可变解引用。Deref强制允许：&T到&U(当T: Deref<Target=U>)、&mut T到&mut U、&mut T到&U。Box<T>通过Deref获得T的所有方法(Rust中'智能指针'的运作方式)。

## 关键结论

""1. Deref不是继承——不会改变类型本质(fn签名仍要求具体类型) 2. 切片可被索引(s[i])但通过Index trait而非切片本身 3. 数组[T; N]自动强制为&[T] 4. 胖指针(&[T]/&dyn Trait)占用两个usize 5. 实现Deref仅在语义上是某种智能指针时——滥用破坏可读性

## 关联知识点

""[[Rust语言-字符串与str/String]] [[Rust语言-所有权与借用]] [[Rust语言-类型转换与From/Into]]
