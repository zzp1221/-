---
title: "零拷贝技术与sendfile"
course: 计算机网络
chapter: 应用层
difficulty: ADVANCED
tags: [计算机网络, 零拷贝, sendfile, DMA, 高性能]
aliases: [Zero Copy, sendfile]
source: "Linux man pages sendfile(2); Efficient File Serving (Nginx文档)"
updated_at: 2026-05-02
---

## 核心定义

零拷贝(zero-copy)技术消除CPU在用户态和内核态之间的数据拷贝，让DMA引擎直接在设备间搬运数据。传统文件发送需4次拷贝（磁盘→内核缓冲区→用户缓冲区→socket缓冲区→网卡）。sendfile系统调用将拷贝降至2次（磁盘→内核缓冲区→网卡DMA）。Linux splice/vmsplice实现管道零拷贝。mmap+write将拷贝减为3次但减少一次用户态拷贝。

## 关键结论

1. sendfile在Nginx/Kafka/静态文件服务器中广泛使用 2. 真正零拷贝需要网卡支持Scatter-Gather DMA 3. Kafka零拷贝：生产者文件→Socket无需中间buffer 4. 零拷贝不适合需修改数据的场景（如SSL加密）

## 关联页面

[[内存映射mmap]] [[IO多路复用select-poll-epoll]] [[DMA直接存储器访问]]
