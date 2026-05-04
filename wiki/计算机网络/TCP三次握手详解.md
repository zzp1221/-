---
title: "TCP三次握手详解"
course: 计算机网络
chapter: 传输层
difficulty: BASIC
tags: [计算机网络, TCP, 三次握手, 连接建立]
aliases: [TCP Three-Way Handshake]
source: "RFC 793 (TCP); UNIX Network Programming (Stevens)"
updated_at: 2026-05-02
---

## 核心定义

TCP连接建立需三次握手：1.客户端→服务端：SYN=1, seq=x（客户端进入SYN-SENT）2.服务端→客户端：SYN=1, ACK=1, seq=y, ack=x+1（服务端进入SYN-RCVD）3.客户端→服务端：ACK=1, seq=x+1, ack=y+1（双方进入ESTABLISHED）。SYN Flood攻击：大量伪造IP的SYN包占满服务端SYN队列，用SYN Cookie防御。

## 关键结论

1. 为什么不是两次？防止旧连接请求建立会话 2. 为什么不是四次？服务端的SYN和ACK可以合并（捎带）3. 初始序号(ISN)随机生成防序列号攻击 4. TCP Fast Open(TFO)在SYN中携带数据实现0-RTT

## 关联页面

[[TCP四次挥手]] [[TCP头格式详解]] [[TCP流量控制]]
