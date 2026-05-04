---
title: "异步编程（async/await）原理"
course: 程序设计
chapter: 并发编程
difficulty: INTERMEDIATE
tags: [异步编程, async, await, 协程, 事件循环]
aliases: [async/await, Asynchronous Programming]
source: "Python asyncio文档; JavaScript Promises/A+; Rust async/await RFC"
updated_at: 2026-05-02
---

## 核心定义

async/await是协程的语法糖，让异步代码看起来像同步。事件循环(Event Loop)：单线程轮询任务，IO操作注册回调后挂起当前协程切换到另一个。工作流程：async函数返回Future/Promise(尚未完成的计算)，await挂起当前协程直到Future完成，释放执行线程去处理其他任务。Python的asyncio用selectors(epoll)做IO多路复用；JS的Promise用microtask队列。

## 关键结论

1. async/await ≠ 多线程(仍是单线程协作式) 2. 关键：await让渡控制权(GIL的替代路径) 3. CPU密集任务阻塞事件循环→用线程池执行器run_in_executor 4. 协程的开销远小于线程(数KB的栈vs数MB)

## 关联页面

[[协程原理]] [[事件循环]] [[IO多路复用select-poll-epoll]]
