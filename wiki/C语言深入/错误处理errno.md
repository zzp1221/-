---
title: "C语言-错误处理errno"
course: C语言深入
chapter: 错误处理
difficulty: BASIC
tags: [C语言, errno, 错误处理, perror, strerror]
aliases: [C errno, Error Handling, perror/strerror]
source: "C11 Standard §7.5; POSIX.1-2017 errno.h; APUE §1.7; CERT C ERR30-C"
updated_at: 2026-05-02
---

## 核心定义

""errno是C/POSIX标准错误报告机制——一个线程局部(thread-local)整数变量。库函数和系统调用在失败时设置errno为特定的错误码(EACCES权限拒绝、ENOENT文件不存在、EINTR被信号中断、EAGAIN资源暂时不可用等)。仅在函数返回-1或NULL时才检查errno——成功的函数也可能修改errno。perror(msg)输出msg+errno文本到stderr。strerror(errno)返回错误描述字符串。

## 线程安全与errno

""现代系统中errno通过宏实现，展开为获取线程局部errno的函数调用：(*__errno_location())。这意味着errno在多线程程序中每个线程独立——不需要互斥。不应在信号处理器中设置errno(使用SA_SIGINFO的si_errno字段)。检查errno前应保存其值(可能在下一个函数调用中被覆盖)。在write的EINTR处理中errno和restart语义需小心处理。

## 关键结论

""1. errno永远不应清零(由库函数设置) 2. 函数成功时errno的值不确定 3. 调用strerror之前应立即保存errno(非线程安全的某些实现) 4. 检查特定errno前应先确认函数返回错误 5. EINTR是'友好的'错误——提示重新调用而非失败 6. CERT C禁止依赖errno的值来区分错误

## 关联知识点

""[[C语言深入-信号处理与异步安全]] [[C语言深入-多线程pthread]] [[C语言深入-标准IO缓冲机制]]
