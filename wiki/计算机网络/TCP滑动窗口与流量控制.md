---
title: "TCP滑动窗口与零窗口"
course: 计算机网络
chapter: 传输层
difficulty: INTERMEDIATE
tags: [计算机网络, TCP, 滑动窗口, 流量控制, 零窗口]
aliases: [Sliding Window, Zero Window]
source: "RFC 793 (TCP); TCP/IP Illustrated (Stevens) 第20章"
updated_at: 2026-05-02
---

## 核心定义

滑动窗口机制实现TCP流量控制：接收方在ACK中通告Window Size(可接收字节数)，发送方确保已发送但未ACK的字节数≤窗口大小。发送窗口=min(拥塞窗口cwnd, 接收窗口rwnd)。零窗口：接收方缓冲区满通告win=0，发送方停止发送并启动持久计时器(persist timer)，周期性发送窗口探针(window probe)检测窗口是否恢复。糊涂窗口综合征(Silly Window Syndrome)：收发双方每次都处理极小数据量，用Nagle算法和Clark方案解决。

## 关键结论

1. rwnd是端到端流量控制，cwnd是网络拥塞控制——两者独立 2. 零窗口探测可被恶意利用（零窗口攻击）3. Nagle算法延迟小包发送直到收到ACK或凑满MSS

## 关联页面

[[TCP头格式详解]] [[TCP拥塞控制]] [[TCP三次握手详解]]
