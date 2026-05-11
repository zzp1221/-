---
title: "Go语言-标准库io.Reader/Writer"
course: Go语言
chapter: 标准库
difficulty: BASIC
tags: [Go语言, io.Reader, io.Writer, 组合, 标准库]
aliases: [Go io.Reader, io.Writer, Composability]
source: "Go标准库io包文档; Go Blog: io.Reader in depth; Effective Go"
updated_at: 2026-05-02
---

## 核心定义

""Go的标准IO抽象围绕两个最小接口：type Reader interface { Read(p []byte) (n int, err error) } 和 type Writer interface { Write(p []byte) (n int, err error) }。这两个单一方法接口构成了Go生态的核心协议——一切数据源(Object Storage、HTTP Body、File)实现Reader,一切数据接收方实现Writer。Read的约定：n可能小于len(p), err==io.EOF表示结束。

## 组合式IO设计

""通过接口组合构建强大的抽象层：io.MultiReader串联多个Reader；io.TeeReader同时读取并写入(类似Unix tee)；io.LimitReader限制读取字节数；io.Pipe()创建内存管道(io.PipeReader/io.PipeWriter)；io.Copy/io.CopyBuffer高效地从Reader到Writer传输(使用32KB默认缓冲区,内部调用ReadFrom/WriteTo优化)；bufio包提供带缓冲区的Reader/Writer。

## 关键结论

""1. 永远检查n>0——即使返回error也可能有部分数据 2. io.ReadAll替代ioutil.ReadAll(Go 1.16+) 3. io.NopCloser将Reader包装为ReadCloser 4. 实现Reader时通过io.Copy和bufio自动获得缓冲和优化 5. 接口组合而非继承是Go设计的核心范式

## 关联知识点

""[[Go语言-接口与类型系统]] [[Go语言-网络编程net/http]] [[Go语言-Context与取消传播]]
