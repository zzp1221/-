---
title: "HTTP/2与HTTP/3全面对比"
course: 计算机网络
chapter: 应用层
difficulty: INTERMEDIATE
tags: [计算机网络, HTTP2, HTTP3, QUIC, 多路复用]
aliases: [HTTP/2 vs HTTP/3]
source: "RFC 7540 (HTTP/2); RFC 9114 (HTTP/3); web.dev HTTP性能指南"
updated_at: 2026-05-02
---

## 核心定义

HTTP/2(基于TCP+TLS)：二进制分帧、流多路复用(单连接多流)、头部压缩(HPACK)、服务器推送。但TCP层面的队头阻塞问题依然存在。HTTP/3(基于QUIC+UDP)：同样支持多路复用但消除了TCP层面的队头阻塞、0-RTT连接建立、连接迁移。HTTP语义(方法/状态码/头部)在两版本中保持一致。

## 关键结论

1. HTTP/2让请求并行但丢包仍阻塞所有流，HTTP/3丢包只影响相关流 2. 头部压缩：HPACK(HTTP/2)→QPACK(HTTP/3，减少队头阻塞) 3. 高丢包网络(移动端)HTTP/3提升显著 4. 主流浏览器/服务器(nginx/curl)已支持HTTP/3

## 关联页面

[[QUIC协议原理]] [[HTTP协议基础]] [[TCP拥塞控制]]
