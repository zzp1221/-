---
title: "Go语言-channel实现原理"
course: Go语言
chapter: Channel
difficulty: ADVANCED
tags: [Go, channel, CSP, hchan, select]
aliases: [Channel Implementation, hchan]
source: "Go Runtime source (src/runtime/chan.go); Go Blog: Share Memory By Communicating"
updated_at: 2026-05-02
---

## 核心定义

Go的channel基于CSP模型。底层数据结构hchan(runtime/chan.go)：buf=环形缓冲区，sendx/recvx=发送/接收指针，sendq/recvq=等待发送/接收的goroutine队列(FIFO)，lock=互斥锁保护。无缓冲channel(synchronous): buf为空，发送方阻塞直到接收方取走，接收方阻塞直到发送方提供值。有缓冲channel(asynchronous): buf有容量，仅当buf满时发送方阻塞，当buf空时接收方阻塞。

## Select实现

select语句编译为runtime.selectgo调用：随机化case顺序(公平性保证)→遍历所有case检查就绪(channel有数据/可写入/closed/无default)→若有就绪case，随机选择一个执行→若无就绪case且有default，执行default→若无就绪且无default，将当前goroutine入队所有case的等待队列，阻塞。

## 关闭与广播

close(c)将hchan.closed置为1，立即唤醒recvq中所有G。向已关闭channel发送会panic。从已关闭channel接收：buf中已缓冲的数据可正常接收，读完后返回零值+ok=false。利用关闭的广播特性可实现通知所有等待者。

## 关联知识点

[[Go语言-GMP调度器与goroutine]] [[Go语言-接口与类型系统]]
