---
title: QUIC协议详解
course: 计算机网络
chapter: 传输层
difficulty: ADVANCED
tags: [计算机网络, QUIC, HTTP3, UDP, 传输层]
aliases: [QUIC, HTTP/3, 基于UDP的传输]
source:
  - RFC 9000 (QUIC: A UDP-Based Multiplexed and Secure Transport)
  - RFC 9114 (HTTP/3)
  - Google QUIC设计文档
updated_at: 2026-05-03
---

## 核心定义

QUIC（Quick UDP Internet Connections）是Google设计的基于UDP的传输层协议，已标准化为IETF RFC 9000，是HTTP/3的底层协议。QUIC解决了TCP+TLS的三大问题：(1)队头阻塞（Head-of-Line Blocking）：TCP的字节流语义导致一个包丢失阻塞所有流。QUIC在UDP上实现多路复用流（Stream Multiplexing），每个流独立，一个流的丢失不影响其他流。(2)连接建立延迟：TCP+TLS 1.3需要2-3个RTT才能发送数据。QUIC将传输握手和TLS握手合并，首次连接1-RTT，后续0-RTT（类似TLS的session resumption）。(3)连接迁移：TCP连接由四元组（源IP/端口、目标IP/端口）标识，网络切换（如WiFi→4G）导致连接断开。QUIC使用Connection ID标识连接，支持无缝迁移。QUIC的核心特性：内置TLS 1.3加密（所有payload加密，头部也部分加密）、可拥塞控制（可插拔，如BBR/Cubic）、流量控制（连接级和流级）、连接迁移。

## 关键结论

- QUIC的0-RTT连接建立是其最大优势：缓存密钥后首次数据包就可以携带应用数据
- QUIC的流级多路复用彻底解决了TCP的队头阻塞：一个流丢包只阻塞该流
- QUIC基于UDP的原因是：UDP在中间设备（NAT/防火墙）上更容易穿透，且可以在用户空间实现
- QUIC的Connection ID机制支持连接迁移：客户端IP变化后连接不断
- HTTP/3是QUIC上的HTTP语义映射，HTTP/2帧格式适配为QUIC流

## 易错点

1. QUIC不是"UDP上跑HTTP"：QUIC是完整的传输协议，有拥塞控制、流控、可靠传输
2. 0-RTT有重放攻击风险：只适合幂等请求（如GET），非幂等请求应使用1-RTT
3. QUIC的拥塞控制是可插拔的：Google使用BBR，可以替换为Cubic或其他算法

## 例题

**例1：** 对比HTTP/2 over TCP+TLS 1.3和HTTP/3 over QUIC在首次连接和非首次连接的延迟。

**解答：** 首次连接：HTTP/2需要TCP握手(1 RTT) + TLS 1.3握手(1 RTT) = 2 RTT后才能发送HTTP请求。HTTP/3的QUIC握手(1 RTT，合并传输+TLS)后即可发送请求。假设RTT=50ms：HTTP/2首次请求延迟=100ms+请求时间，HTTP/3首次请求延迟=50ms+请求时间。非首次连接：HTTP/2需要TCP握手(1 RTT) + TLS 1.3 session resumption(1 RTT) = 2 RTT。HTTP/3使用0-RTT恢复，第一个数据包就携带HTTP请求。延迟：HTTP/2=100ms，HTTP/3=0ms（请求与握手并行）。在高延迟网络（如移动网络RTT=200ms）上，QUIC的优势更明显。

## 关联页面

[[TCP三次握手]] [[TLS握手与HTTPS]] [[HTTP2与HTTP3对比]]
