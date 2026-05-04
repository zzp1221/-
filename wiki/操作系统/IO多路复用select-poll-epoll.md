---
title: "IO多路复用（select/poll/epoll）"
course: 操作系统
chapter: IO系统
difficulty: ADVANCED
tags: [操作系统, IO, select, poll, epoll, 事件驱动]
aliases: [IO Multiplexing]
source: "UNIX Network Programming (Stevens) 第6章; Linux man pages epoll(7)"
updated_at: 2026-05-02
---

## 核心定义

IO多路复用允许单个线程同时监听多个文件描述符的IO事件。select：使用fd_set位图，FD_SETSIZE=1024限制，每次调用复制整个fd_set，O(n)扫描。poll：使用pollfd数组，无fd数量限制，但仍需O(n)扫描和复制。epoll(Linux)：epoll_create创建实例，epoll_ctl注册fd（红黑树存储），epoll_wait仅返回就绪fd（就绪链表），O(1)获取就绪事件。

## 关键结论

1. 大量连接中少数活跃用epoll，边缘触发ET更高效 2. select/poll对小规模连接(<100)性能尚可 3. epoll是Nginx/Redis高性能的关键 4. Windows上的IOCP是完成端口模型，不同于epoll

## 关联页面

[[IO控制方式]] [[文件描述符]] [[异步IO]] [[网络编程模型]]
