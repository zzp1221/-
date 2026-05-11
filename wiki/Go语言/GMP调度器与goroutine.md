---
title: "Go语言-GMP调度器与goroutine"
course: Go语言
chapter: 并发模型
difficulty: ADVANCED
tags: [Go, goroutine, GMP, 调度器, 并发]
aliases: [GMP Scheduler, Goroutine Scheduling]
source: "Go Runtime Source Code (src/runtime/proc.go); Go Blog: The Go Scheduler"
updated_at: 2026-05-02
---

## 核心定义

Go的并发模型基于GMP调度器：G(Goroutine)=轻量级协程，M(Machine)=操作系统线程，P(Processor)=逻辑处理器(默认=GOMAXPROCS=CPU核数)。每个P持有本地runq(环形队列，容量256)，M绑定P后从P的runq取G执行。全局runq+Network Poller作为补充调度源。当一个G阻塞（系统调用/网络IO/channel操作），P与当前M解绑，寻找新的M或新建M。

## 抢占调度

Go 1.14+基于信号的抢占：sysmon监控线程定期给长时间运行的G发送SIGURG信号，触发异步抢占点。抢占点(checkpoint): 函数调用前检查stackguard0标记，若需要抢占则进入调度循环。1.13以前只能协作式抢占（函数调用处），导致紧密循环不调度。

## Work Stealing

当P的本地runq为空，随机选择其他P的runq窃取一半G。Net Poller充当'全局网络G循环队列'的角色：当netpoller检测到fd就绪，将等待的G插入就绪队列。

## 关联知识点

[[Go语言-channel实现原理]] [[Go语言-内存管理与GC]]
