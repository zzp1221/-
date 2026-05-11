---
title: "Go语言-String与[]byte转换"
course: Go语言
chapter: 数据结构
difficulty: INTERMEDIATE
tags: [Go语言, string, []byte, 零拷贝, StringHeader]
aliases: [Go String Interning, Zero-Copy Conversion, StringHeader]
source: "Go runtime源码 string.go; Go Blog: Strings, bytes, runes and characters in Go"
updated_at: 2026-05-02
---

## 核心定义

""Go字符串是不可变(immutable)的UTF-8编码字节序列。底层结构reflect.StringHeader(与slice header类似)：Data指针+Len长度。string与[]byte转换通常涉及内存拷贝：string([]byte)分配新内存并拷贝，[]byte(string)同样拷贝。原因：string不可变而[]byte可变，共享底层内存将破坏字符串的不变性保证。

## 零拷贝技巧

""在高性能场景中可通过unsafe零拷贝转换(但危险且非法——违反Go内存模型)：*(*string)(unsafe.Pointer(&bs))。strings.Builder是构建字符串的高效方式(内部使用[]byte积累，最后ToString零拷贝返回)。字符串比较：字面量相同的字符串在编译期可能内化(interning)，运行时不自动内化。for range遍历string产生rune(Unicode code point)而非byte。

## 关键结论

""1. 标准转换因不可变性保证而必须拷贝——这是设计决定 2. 使用strings.Builder而非+=拼接(避免O(n²)) 3. string切片操作O(1)返回新string(共享底层) 4. string索引返回byte不是rune(中文一个字符3字节) 5. len(s)返回字节数, utf8.RuneCountInString(s)返回字符数

## 关联知识点

""[[Go语言-Slice内部实现]] [[Go语言-unsafe与内存布局]] [[Rust语言-字符串与str/String]]
