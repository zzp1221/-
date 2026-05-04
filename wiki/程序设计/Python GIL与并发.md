---
title: "Python GIL与并发模型"
course: 程序设计
chapter: Python
difficulty: ADVANCED
tags: [Python, GIL, 并发, 多线程, multiprocessing]
aliases: [Global Interpreter Lock]
source: "Python C API; Python GIL讨论 (PEP 703 Disabling GIL); David Beazley GIL讲解"
updated_at: 2026-05-02
---

## 核心定义

GIL(Global Interpreter Lock)是CPython解释器的互斥锁，确保同一时刻只有一个线程执行Python字节码。这是CPython内存管理(引用计数非线程安全)的实现简化。影响：CPU密集任务用多线程无效甚至更慢(线程切换开销+锁竞争)→用multiprocessing(多进程)或C扩展(释放GIL)。IO密集任务：IO操作会释放GIL(如网络/文件IO)，多线程有效。PEP 703(3.12实验→3.13可选)允许禁用GIL。

## 关键结论

1. GIL不是Python语言的问题而是CPython实现的问题(Jython/IronPython无GIL) 2. 科学计算用numpy——底层C代码释放GIL实现多核并行 3. 多进程的替代成本高(序列化开销+独立内存) 4. subinterpreters(PEP 554)是无GIL的轻量级替代

## 关联页面

[[协程原理与实现]] [[异步编程async-await]] [[线程池原理]]
