---
title: "C语言-标准IO缓冲机制"
course: C语言深入
chapter: 标准库
difficulty: INTERMEDIATE
tags: [C语言, stdio, 缓冲, FILE, setvbuf]
aliases: [C stdio buffering, FILE*, setvbuf]
source: "C11 Standard §7.21; APUE §5.4; GNU C Library manual §12.20"
updated_at: 2026-05-02
---

## 核心定义

""C标准IO库(FILE*)在用户空间维护缓冲区以减少系统调用次数。三种缓冲模式：1.)_IOFBF(全缓冲)——缓冲区满才write(磁盘文件默认,通常4KB-8KB) 2.)_IOLBF(行缓冲)——遇到换行符时write(终端stdout默认) 3.)_IONBF(无缓冲)——每次写都是write系统调用(stderr默认)。setvbuf(fp, buf, mode, size)可设置缓冲模式和自定义缓冲区。未调用setvbuf前缓冲区大小未定义但通常为BUFSIZ(8192)。

## 缓冲陷阱

""常见错误：1.)fork前未fflush——子进程重复父进程的缓冲区数据(缓冲复制) 2.)同一文件使用FILE*和裸fd操作导致数据交错 3.)_exit()不刷新缓冲区(exit()会) 4.)输出重定向使stdout从行缓冲变为全缓冲(导致输出不显示) 5.)setvbuf的buf参数在关闭前不应被释放(fclose后不可再使用)。不同FILE*共享同一个打开的文件描述符(dup)可能导致缓冲问题。

## 关键结论

""1. stderr无缓冲——错误消息即时输出 2. fflush(NULL)刷新所有输出流 3. glibc中stdout的缓冲模式检测isatty()自动调整 4. 自定义缓冲可实现完全无锁写入(ring buffer) 5. FILE*的缓冲不可跨进程(与mmap不同) 6. fclose隐式fflush——防止数据丢失

## 关联知识点

""[[C语言深入-错误处理errno]] [[C语言深入-跨平台移植要点]] [[操作系统-文件系统与IO基础]]
