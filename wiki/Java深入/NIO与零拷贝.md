---
title: "Java深入-NIO与零拷贝"
course: Java深入
chapter: IO与网络
difficulty: ADVANCED
tags: [Java, NIO, 零拷贝, ByteBuffer, FileChannel]
aliases: [Java NIO, Zero Copy, sendfile]
source: "Java NIO官方文档; Ron Hitchens《Java NIO》; Linux sendfile(2) man page"
updated_at: 2026-05-02
---

## 核心定义

Java NIO(java.nio)提供非阻塞IO基础。核心概念：Channel(双向通信通道——FileChannel/SocketChannel/ServerSocketChannel)、Buffer(数据容器——ByteBuffer/CharBuffer等)、Selector(多路复用——单线程管理多个Channel)。Direct Buffer分配在native堆外内存(allocateDirect())——避免JVM堆到native堆的拷贝，适合长生命周期的IO缓冲。ByteBuffer维护position/limit/capacity三指针和flip/clear/compact操作。

## 零拷贝与sendfile

Java的零拷贝通过FileChannel.transferTo/transferFrom实现——底层调用sendfile()系统调用(2.6.33后为splice)。数据从page cache直接传输到socket buffer而无需经过用户空间(真正的0次CPU拷贝在支持DMA scatter-gather的网卡下)。Netty使用CompositeByteBuf和FileRegion实现零拷贝。ByteBuffer.slice()创建共享底层数据的视图(零拷贝子Buffer)。MappedByteBuffer实现内存映射文件(map-reduce read——mmap syscall)。

## 关键结论

1. Direct Buffer分配/回收成本高——使用对象池复用 2. transferTo一次最多传输2GB(需循环) 3. MappedByteBuffer不受GC控制——通过Cleaner手动释放 4. NIO在连接数>1000时显著优于传统BIO(thread-per-connection) 5. Selector实现因操作系统而异(epoll在Linux,kqueue在macOS/BSD)

## 关联知识点

[[Java深入-JVM架构与字节码]] [[计算机网络-epoll与I/O多路复用]] [[Go语言-netpoll与网络模型]]
