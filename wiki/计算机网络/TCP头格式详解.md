---
title: "TCP头格式详解"
course: 计算机网络
chapter: 传输层
difficulty: INTERMEDIATE
tags: [计算机网络, TCP, 传输层, 报文格式]
aliases: [TCP Header]
source: "RFC 793 (TCP); RFC 7323 (TCP Extensions)"
updated_at: 2026-05-02
---

## 核心定义

TCP头部固定20字节(不含选项)：Source/Dest Port各16位、Sequence Number(32位，本报文段首字节序号)、ACK Number(32位，期望收到对方的下一个字节序号)、Data Offset(4位，头部长度/4)、控制标志URG/ACK/PSH/RST/SYN/FIN(各1位)、Window Size(16位，接收窗口)、Checksum(16位，含伪首部)、Urgent Pointer(16位)。选项最长40字节：MSS、窗口缩放、时间戳、SACK等。

## 关键结论

1. Seq和ACK Number都是字节序号不是报文序号 2. SYN和FIN各占一个序号 3. Window Size最大65535，窗口缩放选项可扩展到1GB 4. TCP伪首部包括源/目的IP+协议号+TCP长度防止路由错误

## 关联页面

[[TCP三次握手]] [[TCP四次挥手]] [[TCP流量控制]] [[TCP拥塞控制]]
