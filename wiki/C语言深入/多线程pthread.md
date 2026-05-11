---
title: "C语言-多线程pthread"
course: C语言深入
chapter: 并发编程
difficulty: INTERMEDIATE
tags: [C语言, pthread, POSIX, 多线程]
aliases: [POSIX Threads, pthread API]
source: "POSIX.1-2017; Butenhof《Programming with POSIX Threads》; pthreads(7) manual"
updated_at: 2026-05-02
---

## 核心定义

""POSIX线程(pthread)是UNIX系统的标准多线程API。核心函数：pthread_create(&tid, attr, func, arg)创建线程，pthread_join(tid, &ret)等待线程结束回收资源，pthread_exit(ret)线程退出。pthread_self()返回自身ID。线程属性pthread_attr_init/attr_setstacksize控制线程栈大小等。线程数过多可能超出系统资源(pthread默认栈8MB Linux,每个线程消耗虚拟地址空间)。

## 同步原语

""pthread提供三种同步机制：互斥锁——pthread_mutex_init/lock/trylock/unlock/destroy。读写锁——pthread_rwlock_rdlock/wrlock(读者优先或写者优先策略)。条件变量——pthread_cond_wait/signal/broadcast(配合mutex解决特定条件的等待)。pthread_once确保函数在进程中仅执行一次。pthread_key_create建立线程局部存储(TLS)。屏障(pthread_barrier)确保多线程同步于某点。

## 关键结论

""1. 线程安全函数列表由POSIX定义——printf不加锁但线程安全 2. 每个线程有独立的errno(通过TLS实现) 3. pthread_cancel异步取消线程可能导致资源泄漏(使用cleanup handler) 4. 不能fork正在运行的线程(子进程仅复制调用线程) 5. 线程ID复用——使用pthread_equal比较而非== 6. 信号与线程：信号发送给整个进程但由任意线程处理

## 关联知识点

""[[C语言深入-C11原子操作]] [[C语言深入-信号处理与异步安全]] [[操作系统-进程与线程]]
