---
title: "TCP拥塞控制算法演化史"
course: 计算机网络
chapter: 传输层
difficulty: ADVANCED
tags: [计算机网络, TCP, 拥塞控制, BBR, CUBIC]
aliases: [TCP Congestion Control Evolution]
source: "RFC 2581 (NewReno); RFC 8312 (CUBIC); Van Jacobson 1988"
updated_at: 2026-05-02
---

## 核心定义

TCP拥塞控制演化：Tahoe(1988)→Reno(1990)→NewReno(1997)→CUBIC(Linux 2006)→BBR(Google 2016)。Tahoe：慢启动+拥塞避免+AIMD+RTO超时。Reno：增加快重传(3 dup ACK)+快恢复(不进入慢启动)。CUBIC：用三次函数代替AIMD的线性增长，适合高BDP网络。BBR：不再基于丢包而基于Bottleneck Bandwidth和RTT建模，主动探测带宽。

## 关键结论

1. 基于丢包的算法(CUBIC)在浅缓冲网络公平但在深缓冲有bufferbloat 2. BBR在有一定丢包率的链路上远超CUBIC但早期版本公平性存疑 3. 实际选择：互联网→CUBIC(公平)，数据中心→DCTCP，跨洋→BBR

## 关联页面

[[TCP拥塞控制]] [[QUIC协议原理]] [[TCP流量控制]]
