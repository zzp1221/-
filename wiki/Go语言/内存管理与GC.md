---
title: "Go语言-内存管理与GC"
course: Go语言
chapter: 内存管理
difficulty: INTERMEDIATE
tags: [Go, GC, 内存分配, 三色标记, 逃逸分析]
aliases: [Go GC, Tricolor Mark-and-Sweep, Escape Analysis]
source: "Go Blog: A Guide to the Go Garbage Collector; Go Runtime src/runtime/mgc.go"
updated_at: 2026-05-02
---

## 核心定义

Go的GC采用并发三色标记清扫(Concurrent Tri-color Mark-Sweep)。三色抽象：白色(初始/未标记，可能回收)、灰色(已标记但其引用的对象未扫描)、黑色(已标记且引用的对象确定已找到)。GC过程：1.)STW写屏障启用+栈扫描 2.)并发标记(无STW) 3.)STW重扫描栈 4.)(可选STW终止) 5.)并发清扫。

## GC触发

GC触发条件：1.)GOGC=100(默认): 堆增长到上次存活量的200%时触发GC 2.)目标CPU时间: runtime.GC强制触发 3.)2分钟定时触发(如果一直未GC)。Go 1.19+支持软内存限制GOMEMLIMIT(通过SetMemoryLimit API)，防止OOM。

## 逃逸分析

逃逸分析(escape analysis)决定对象分配在栈上还是堆。若编译器证明对象在函数返回后未被引用(未逃逸)，栈上分配(函数返回时自动释放，无GC开销)。反之则堆上分配。常见逃逸场景：1.)返回局部变量的指针 2.)将变量存入interface{} 3.)闭包捕获变量 4.)发送到channel。

## 关联知识点

[[Go语言-GMP调度器与goroutine]] [[Go语言-接口与类型系统]]
