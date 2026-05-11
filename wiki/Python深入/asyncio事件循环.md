---
title: "Python深入-异步编程asyncio事件循环"
course: Python深入
chapter: 异步编程
difficulty: INTERMEDIATE
tags: [Python, asyncio, 事件循环, async/await, 协程, Task]
aliases: [Python asyncio, Event Loop, AsyncIO]
source: "Python docs: asyncio module; PEP 3156 (Asynchronous IO Support); PEP 492 (async/await); uvloop project"
updated_at: 2026-05-02
---

## 核心定义

asyncio提供基于事件循环(Event Loop)的单线程协作式并发模型。事件循环是核心调度器——管理就绪的Task队列、注册I/O回调(基于epoll/kqueue/IOCP)、调度定时任务。async def创建协程对象(Coroutine)，await将控制权交还给事件循环(让其他Task运行)。可等待对象(Awaitable)有三种：协程、Task(包装协程的运行单元，由loop.create_task创建)、Future(低级结果容器)。事件循环每轮迭代：处理就绪I/O→执行已到期的定时回调→执行就绪的协程步骤。asyncio.run()是Python 3.7+的推荐入口——创建新的事件循环、运行协程、清理。uvloop(基于libuv)是Dropbox开源的更快事件循环实现。

## 关键结论

1.await释放控制权——不用await的阻塞调用(time.sleep/requests.get)阻塞整个线程和其他协程 2.asyncio.gather(*aws)并发执行多个协程，返回结果列表；任一抛出异常默认传播(return_exceptions=True可抑制) 3.asyncio.create_task()调度协程为后台任务(需保持强引用，否则任务可能被GC) 4.同步代码在线程中运行：await asyncio.to_thread(func)(Python 3.9+) 5.asyncio.Semaphore限制并发数量：async with semaphore控制同时运行的协程数 6.TaskGroup(Python 3.11+)提供结构化并发：异步上下文管理器中所有子任务完成才退出 7.调试：PYTHONASYNCIODEBUG=1启用慢回调检测(超过100ms的协程步骤)

## 关联知识点

[[Python深入-生成器与协程]] [[Python深入-GIL与并发编程]] [[Python深入-上下文管理器]] [[JavaScript-事件循环与Job Queue]]
