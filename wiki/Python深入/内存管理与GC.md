---
title: "Python深入-内存管理与GC机制"
course: Python深入
chapter: 内存管理
difficulty: INTERMEDIATE
tags: [Python, 内存管理, GC, 引用计数, 循环引用, 弱引用]
aliases: [Python GC, Python Memory Management, Reference Counting]
source: "Python docs: gc module; Python docs: Garbage Collector Interface; CPython Modules/gcmodule.c"
updated_at: 2026-05-02
---

## 核心定义

CPython采用引用计数(reference counting)与分代垃圾回收(Generational GC)的混合方案。每个PyObject包含ob_refcnt字段(通过Py_INCREF/Py_DECREF增减)，引用计数归零时立即通过tp_dealloc回收内存。引用计数无法处理循环引用(PyList包含自身)，分代GC专门解决此问题：仅追踪可包含其他对象的'容器'类型(list/dict/set/自定义类实例等)，按generation 0/1/2分层。新对象进入gen0；每次GC中存活的对象晋升到下一代；gen0收集最频繁(阈值默认700个obj分配)，gen2最不频繁。Python 3.11+引入快速GC避免在gen0为空时仍触发。

## 关键结论

1.gc.get_threshold()查看阈值(默认(700,10,10))；gc.collect(generation=0)手动触发 2.weakref.WeakValueDictionary/WeakKeyDictionary可用于缓存而不阻止对象回收 3.__del__和GC交互复杂：有__del__的不可达循环对象在Python 3.4以下放到gc.garbage；3.4+简化为直接调用__del__ 4.上下文管理器(with)优于__del__——__del__调用时机不确定，解释器退出时可能不调用 5.对象池优化：小整数(-5~256)预分配；短字符串(单字符/标识符)自动intern到全局dict 6.objgraph和tracemalloc可用于诊断内存泄漏——tracemalloc显示内存分配的Python回溯

## 关联知识点

[[Python深入-CPython对象模型]] [[Python深入-上下文管理器]] [[JavaScript-内存管理与内存泄漏]] [[Go语言-内存管理与GC]]
