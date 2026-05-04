---
title: "内存映射（mmap）"
course: 操作系统
chapter: 内存管理
difficulty: INTERMEDIATE
tags: [操作系统, mmap, 内存映射, 文件IO, 零拷贝]
aliases: [Memory-Mapped File]
source: "Advanced Programming in the UNIX Environment (Stevens) 第14章; Linux man mmap(2)"
updated_at: 2026-05-02
---

## 核心定义

mmap将文件或设备映射到进程的虚拟地址空间，使文件访问像访问内存一样简单。类型：文件映射（映射普通文件，修改可选回写磁盘）、匿名映射（不关联文件，用于malloc大块内存）。标志：MAP_SHARED（修改对其他进程可见并写回文件）、MAP_PRIVATE（COW私有映射）。

## 关键结论

1. 相比read/write减少一次内核到用户空间的拷贝 2. 适合随机访问大文件 3. mmap+write实现零拷贝文件传输 4. 缺点是缺页中断开销大且难以处理文件截断(SIGBUS)

## 关联页面

[[文件系统]] [[虚拟内存]] [[零拷贝技术]]
