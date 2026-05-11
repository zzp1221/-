---
title: "Python深入-GIL与并发编程"
course: Python深入
chapter: 并发与GIL
difficulty: ADVANCED
tags: [Python, GIL, 多线程, asyncio, subinterpreter]
aliases: [Python GIL, Global Interpreter Lock]
source: "Python docs: Global Interpreter Lock; PEP 703 (No-GIL); Grothe《Inside the Python GIL》(2013)"
updated_at: 2026-05-02
---

## 核心定义

GIL(Global Interpreter Lock)是CPython解释器中保护内部状态(引用计数、内存分配器、类型对象)的互斥锁。任何线程执行Python字节码前必须获取GIL——这意味着Python多线程在CPU密集型任务中实际上是串行的。GIL每隔sys.getswitchinterval()秒(默认5ms)或每执行约100条字节码后被强制释放，由等待线程争抢。等待I/O时线程主动释放GIL(Py_BEGIN_ALLOW_THREADS)，因此I/O密集型多线程仍然有效。PEP 703提出用偏向引用计数替代GIL，计划Python 3.13+实验性支持。Python 3.12引入的子解释器(PEP 684)每个拥有独立GIL，可并行执行。GIL是CPython的实现细节，并非Python语言规范——Jython和IronPython没有GIL。

## 关键结论

1.CPU密集型任务用multiprocessing(每个进程独立GIL)或C扩展中释放GIL 2.I/O密集型任务(网络请求、文件读写)多线程有效——等待I/O时GIL被释放 3.multiprocessing的进程间通信(Queue/Pipe)有序列化开销，适合粗粒度任务划分 4.concurrent.futures.ThreadPoolExecutor适合I/O密集型，ProcessPoolExecutor适合CPU密集型 5.GIL内部的切换机制：ceval.c中的_PyEval_EvalFrameDefault循环，每执行完一条字节码检查是否需要释放GIL 6.开发时可用cpu_count()来自动决定线程池vs进程池 7.GIL导致某个线程的无限循环阻塞所有线程——即使调用time.sleep(0)也会短暂释放GIL给其他线程

## 关联知识点

[[Python深入-CPython对象模型]] [[Python深入-asyncio事件循环]] [[Python深入-内存管理与GC]] [[Python深入-生成器与协程]]
