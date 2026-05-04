---
title: Kotlin协程
course: 程序设计
chapter: 异步编程
difficulty: INTERMEDIATE
tags: [程序设计, Kotlin, 协程, Coroutine, 结构化并发]
aliases: [Kotlin Coroutine, 挂起函数, 协程作用域]
source:
  - Kotlin官方文档（kotlinlang.org/docs/coroutines.html）
  - 《Kotlin协程编程实战》
  - JetBrains协程设计文档
updated_at: 2026-05-03
---

## 核心定义

Kotlin协程是语言级别的轻量级并发方案，通过编译器变换（CPS变换）将异步代码写成同步风格。核心概念：(1)挂起函数（suspend function）：用suspend关键字标记的函数，可以在不阻塞线程的情况下暂停和恢复执行。(2)协程构建器：launch（启动不返回结果的协程）、async（启动返回结果的协程）、runBlocking（阻塞当前线程直到协程完成）。(3)协程作用域（CoroutineScope）：定义协程的生命周期，所有协程必须在作用域内启动。(4)调度器（Dispatcher）：决定协程在哪个线程上执行——Dispatchers.Default（CPU密集型）、Dispatchers.IO（IO密集型）、Dispatchers.Main（UI线程）。Kotlin协程的实现原理：编译器将suspend函数转换为状态机（CPS变换），每个挂起点对应一个状态，函数的局部变量保存在Continuation对象中。挂起时不阻塞线程，而是将Continuation注册到调度器，线程去执行其他任务，调度器在适当时候恢复Continuation。

## 关键结论

- Kotlin协程是编译器实现的，不是运行时库实现的：suspend函数被编译为状态机
- 结构化并发（Structured Concurrency）：子协程在父协程作用域内启动，父协程等待所有子协程完成
- 协程比线程轻量得多：一个应用可以轻松运行数十万个协程
- withContext可以切换协程的调度器（线程），不需要回调：`withContext(Dispatchers.IO) { /* IO操作 */ }`
- Flow是Kotlin的响应式流API，类似RxJava但基于协程和挂起函数

## 易错点

1. suspend函数不能在普通函数中调用：必须在另一个suspend函数或协程构建器中调用
2. GlobalScope.launch不推荐使用：不受结构化并发管理，可能导致协程泄漏
3. Dispatchers.IO的线程数远大于Default：IO操作会阻塞线程，需要更多线程

## 例题

**例1：** 使用Kotlin协程并发请求3个API，汇总结果后返回。

**解答：**
```kotlin
suspend fun fetchAll(): Result {
    return coroutineScope {
        val user = async { api.getUser() }
        val orders = async { api.getOrders() }
        val products = async { api.getProducts() }
        Result(user.await(), orders.await(), products.await())
    }
}
```
`coroutineScope`确保3个async协程都在同一作用域内，如果任一协程失败会自动取消其他协程（结构化并发）。`async`返回Deferred，`await()`挂起等待结果。3个请求并发执行，总耗时等于最慢的那个请求。

## 关联页面

[[协程原理与实现]] [[异步编程async-await]] [[并发编程]]
