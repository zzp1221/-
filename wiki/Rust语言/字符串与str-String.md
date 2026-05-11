---
title: "Rust语言-字符串与str/String"
course: Rust语言
chapter: 数据结构
difficulty: INTERMEDIATE
tags: [Rust, String, &str, UTF-8, OsString]
aliases: [Rust Strings, &str vs String, UTF-8 Encoding]
source: "The Rust Book Ch 8; Rust标准库std::string/std::str文档; Rustomicon: String representation"
updated_at: 2026-05-02
---

## 核心定义

""Rust有两种字符串类型：&str(字符串切片)——不可变的UTF-8字节序列引用，(ptr, len)组成。String——可变、可增长的UTF-8字符串，(ptr, len, cap)组成。String可解引用强制转换(Deref)为&str(String: Deref<Target=str>)。Rust字符串保证内容永远是合法UTF-8(NonZero结尾优化zero-sized类型除外)。OsString/OsStr处理平台原生的可能非UTF-8的文件路径。

## UTF-8与索引

""Rust不支持直接索引字符串s[i](因为UTF-8中一个char可能占1-4字节)。必须通过边界明确的迭代器：.chars()(Unicode标量值)、.bytes()(原始字节)、.char_indices()。切片s[a..b]必须落在char边界上否则panic(使用s.get(a..b)安全返回Option)。String内部是Vec<u8>的包装，所有ASCII操作在Rust字符串上O(1)完成(但需要边界检查)。

## 关键结论

""1. 函数参数优先使用&str(更通用——可接受&String和字面量) 2. String -> &str 通过Deref隐式完成(零成本) 3. &str -> String 需要.to_owned()或.to_string()(分配内存) 4. format!宏构建String 5. Cow<str>提供写时复制的智能字符串(Copy-on-Write)

## 关联知识点

""[[Rust语言-切片与Deref强制]] [[Rust语言-所有权与借用]] [[Go语言-String与[]byte转换]]
