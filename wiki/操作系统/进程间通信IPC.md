---
title: "进程间通信（IPC）机制全景"
course: 操作系统
chapter: 进程管理
difficulty: INTERMEDIATE
tags: [操作系统, IPC, 管道, 消息队列, 共享内存, 信号]
aliases: [Inter-Process Communication]
source: "Advanced Programming in the UNIX Environment (Stevens) 第15章; Linux man pages"
updated_at: 2026-05-02
---

## 核心定义

IPC是进程间交换数据的机制。管道(Pipe)：半双工，用于父子进程通信。命名管道(FIFO)：有文件名，可用于无亲缘进程。消息队列：消息的有序链表，支持按类型选择接收。共享内存：最快IPC，多个进程映射同一物理内存区域。信号量(Semaphore)：进程间同步原语，P/V操作。信号(Signal)：异步通知机制。Socket：网络IPC，也可用于本地Unix Domain Socket。

## 关键结论

1. 共享内存最快但需要额外同步机制 2. 管道适合流式数据，消息队列适合结构化数据 3. POSIX IPC vs System V IPC：POSIX更简洁但兼容性差 4. Unix Domain Socket性能优于TCP loopback

## 关联页面

[[进程同步与互斥]] [[生产者消费者问题]] [[共享内存]]
