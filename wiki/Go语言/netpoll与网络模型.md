---
title: "Go语言-netpoll与网络模型"
course: Go语言
chapter: 运行时
difficulty: ADVANCED
tags: [Go语言, netpoll, epoll, 网络模型, 异步IO]
aliases: [Go Netpoll, Epoll Integration, Goroutine Network Model]
source: "Go runtime源码 netpoll.go/netpoll_epoll.go; Go Blog: Go's work-stealing scheduler; Draven《Go并发编程实战》"
updated_at: 2026-05-02
---

## 核心定义

""Go的网络IO模型基于netpoll——一个对操作系统多路复用机制(epoll/kqueue/IOCP)的封装。netpoll将非阻塞IO与goroutine调度集成：当goroutine在socket上读写阻塞时，runtime将其挂起，将文件描述符注册到netpoller，goroutine让出P(逻辑处理器)。IO就绪后netpoller将该goroutine标记为可运行并放回运行队列。

## netpoll与调度器集成

""netpoll的核心优势是goroutine级别的阻塞而非线程级别——一个OS线程可以运行数千个goroutine,当一个goroutine阻塞在网络IO上,线程可以立即切换到其他goroutine。关键函数：runtime.netpoll(轮询就绪fd), runtime.netpollblock(挂起当前g直到IO就绪)。Goroutine阻塞在IO时不消耗CPU。findrunnable()在寻找可运行goroutine时会调用netpoll检查就绪的IO。

## 关键结论

""1. Go的goroutine IO模型提供同步编程的简单性和异步IO的性能 2. netpoller是Go高并发网络服务的核心基础 3. 文件IO(O_DIRECT以外)不走netpoller——文件阻塞会占用OS线程 4. net.Dialer的Timeout/Deadline设置通过timer+netpoll实现 5. Go HTTP服务器的并发处理能力(百万连接级别)依赖netpoller

## 关联知识点

""[[Go语言-Go运行时调度器GPM]] [[Go语言-网络编程net/http]] [[计算机网络-epoll与I/O多路复用]]
