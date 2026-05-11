---
title: "BBR拥塞控制"
course: 计算机网络
chapter: 传输层
difficulty: ADVANCED
tags: [计算机网络, BBR, 拥塞控制, TCP, 瓶颈带宽]
aliases: [BBR Congestion Control, Bottleneck Bandwidth and RTT]
source: "Cardwell et al. 2016 (BBR paper, ACM Queue); Google BBR GitHub; RFC 9438 (BBR v2)"
updated_at: 2026-05-02
---

## 核心定义

BBR(Bottleneck Bandwidth and Round-trip propagation time)是Google于2016年提出的拥塞控制算法。不同于传统基于丢包的算法(CUBIC/Reno)，BBR基于网络路径模型：持续测量交付速率(瓶颈带宽估计)和最小RTT(往返传播时间)。发送速率=BBR.BtlBw * pacing_gain，拥塞窗口=BBR.BDP* cwnd_gain。BBR不再将丢包作为拥塞信号——丢包可能是噪声或竞争引起。

## 状态机与v2改进

BBR状态机循环四个阶段：STARTUP(指数搜索带宽,2.5x pacing增益——快速填满管道)、DRAIN(排空STARTUP期间积累的队列)、PROBE_BW(周期8个RTT——大部分时间1x pacing+每8 RTT一个5/4增益探测更多带宽)、PROBE_RTT(每10s减少cwnd到4个包以探测更小的RTT基线)。BBR v2增加了对ECN(显式拥塞通知)和丢包的明确反应(轻度丢包减窗)，解决了v1在浅缓冲区或与损耗型算法公平性的问题。

## 关键结论

1. BBR在高丢包长RTT链路上表现优于CUBIC达2700倍 2. BBR v1在竞争fairness上有问题(可能会'撑死'其他流)——v2改进 3. YouTube采用BBR后中位吞吐量增加了4%(2016) 4. BBR仅需发送方支持(接收方无需改动) 5. TCP pacing是实现BBR的基础——即将数据包均匀分布在整个RTT而非突发

## 关联知识点

[[计算机网络-TCP拥塞控制]] [[计算机网络-QUIC与HTTP/3]] [[计算机网络-软件定义网络SDN]]
