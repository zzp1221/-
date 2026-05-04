---
title: "TCP四次挥手与TIME_WAIT"
course: 计算机网络
chapter: 传输层
difficulty: INTERMEDIATE
tags: [计算机网络, TCP, 四次挥手, TIME_WAIT, 连接关闭]
aliases: [TCP Four-Way Handshake]
source: "RFC 793 (TCP); UNIX Network Programming (Stevens)"
updated_at: 2026-05-02
---

## 核心定义

TCP连接关闭需四次挥手：1.主动方→被动方：FIN=1, seq=u（FIN-WAIT-1）2.被动方→主动方：ACK=1, ack=u+1（CLOSE-WAIT，主动方进入FIN-WAIT-2）3.被动方→主动方：FIN=1, seq=v（LAST-ACK）4.主动方→被动方：ACK=1, ack=v+1（TIME-WAIT→等待2MSL后CLOSED）。TIME_WAIT持续2MSL(最大报文生存时间，通常60s)，确保最后的ACK能被对方收到且旧连接的报文全部消失。

## 关键结论

1. TIME_WAIT期间(IP, Port)对不可复用（服务器端常有大量TIME_WAIT）2. SO_REUSEADDR允许重用处于TIME_WAIT的端口 3. 被动关闭方不会有TIME_WAIT（直接CLOSED）4. 大量TIME_WAIT的解决方法：连接池、tcp_tw_reuse

## 关联页面

[[TCP三次握手详解]] [[TCP头格式详解]]
