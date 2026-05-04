---
title: "QUIC协议原理"
course: 计算机网络
chapter: 传输层
difficulty: ADVANCED
tags: [计算机网络, QUIC, HTTP3, UDP, 传输层]
aliases: [Quick UDP Internet Connections]
source: "RFC 9000 (QUIC); RFC 9114 (HTTP/3); Google QUIC设计文档"
updated_at: 2026-05-02
---

## 核心定义

QUIC是基于UDP的下一代传输协议，HTTP/3的底层。核心改进：0-RTT握手（缓存server config后首次连接0-RTT）、多路复无用流ID替代TCP序列号消除队头阻塞(HOL blocking)、连接迁移用Connection ID而非四元组(切换WiFi/4G不断连)、内置TLS 1.3加密(无明文握手)。

## 关键结论

1. QUIC在用户态实现了TCP+TLS+HTTP/2多路复用融合 2. 队头阻塞消除是最大优势——TCP丢一个包阻塞整个连接，QUIC只阻塞该流 3. 已在Google/YouTube/CDN大量部署 4. 拥塞控制算法可插拔(NewReno/Cubic/BBR)

## 关联页面

[[TCP拥塞控制]] [[HTTP2与HTTP3对比]] [[TLS安全协议]]
