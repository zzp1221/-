---
title: "Python GC与内存管理"
course: 程序设计
chapter: Python
difficulty: INTERMEDIATE
tags: [Python, GC, 内存管理, 引用计数]
aliases: [Python Garbage Collection]
source: "CPython源码 (Objects/, Python/gcmodule.c); Fluent Python (Ramalho)"
updated_at: 2026-05-02
---

## 核心定义

CPython GC是引用计数+分代回收的组合。引用计数：每个PyObject有ob_refcnt，增/减引用时更新，归0立即释放。分代GC：处理循环引用(引用计数无法处理)——3代(gen0/1/2)，新对象在gen0，存活越多次代越高。gc.collect()触发回收，gc.get_threshold()查看阈值。__del__的调用时机不确定(应避免依赖，用context manager或weakref)。

## 关键结论

1. 循环引用是引用计数的阿喀琉斯之踵(用gc模块处理) 2. Python的引用计数使C API中的Py_INCREF/Py_DECREF尤为重要 3. 相比Java Go的tracing GC，Python引用计数延迟更低但原子操作开销大

## 关联页面

[[垃圾回收算法]] [[Python GIL与并发]] [[RAII与智能指针]]
