---
title: "Go语言-Context与取消传播"
course: Go语言
chapter: 并发编程
difficulty: INTERMEDIATE
tags: [Go语言, context, 取消传播, 超时控制, 并发]
aliases: [Go Context, Cancellation Propagation]
source: "Go官方博客: Go Concurrency Patterns: Context; Go标准库context包文档"
updated_at: 2026-05-02
---

## 核心定义

""context.Context是Go中跨goroutine传递请求范围值的机制。核心类型：context.Background()(根context), context.TODO()(占位), context.WithCancel(可取消), context.WithDeadline/WithTimeout(超时), context.WithValue(值传递)。Context形成树结构：父context取消时自动取消所有子context。

## 取消传播机制

""context.Done()返回只读channel，当context被取消时该channel关闭，所有监听它的goroutine收到广播信号。内部实现使用propagateCancel父子链：父取消时遍历所有child canceler并依次调用cancel。WithDeadline内部使用timer实现自动取消。Context的Err()方法返回取消原因(context.Canceled或context.DeadlineExceeded)。

## 关键结论

""1. Context应作为函数的第一个参数(context.Context, error模式) 2. 不要将Context存储在struct字段中(除了少数基础设施代码) 3. WithValue仅用于传递请求范围的元数据(trace ID、user id)，不用于传递业务参数 4. 永远不要用nil传递context，应使用context.TODO()

## 关联知识点

""[[Go语言-Goroutine与通道]] [[Go语言-sync包深入]] [[分布式系统-分布式追踪]]
