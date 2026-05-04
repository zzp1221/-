---
title: 计算机网络-TCP拥塞控制详解（视频）
course: 计算机网络
chapter: 传输层
difficulty: INTERMEDIATE
tags: [TCP, 拥塞控制, 慢启动, 拥塞避免, 快重传, 快恢复, Tahoe, Reno, BBR, 视频]
aliases: [TCP Congestion Control]
source:
  - 斯坦福 CS144 计算机网络课程
  - RFC 5681 TCP Congestion Control
updated_at: 2026-05-02
video_url: https://www.bilibili.com/video/BV1Hx411m7RH
video_platform: bilibili
video_author: 湖科大教书匠
video_duration: "38:15"
---

## 视频简介

B站经典网络课程，用动画和抓包实例详解 TCP 拥塞控制的四大算法（慢启动、拥塞避免、快重传、快恢复），从 Tahoe 到 Reno 再到现代的 BBR，完整呈现 TCP 拥塞控制的演进脉络。每个算法配合 Wireshark 抓包分析，直观展示 cwnd 和 ssthresh 的动态变化。

适合学习过 TCP 基本概念后，进一步深入理解 TCP 如何适应网络拥塞状态。

## 覆盖知识点
- 拥塞窗口 cwnd 与慢启动阈值 ssthresh
- 慢启动（Slow Start）指数增长
- 拥塞避免（Congestion Avoidance）线性增长 AIMD
- 快重传（Fast Retransmit）与快恢复（Fast Recovery）
- Tahoe vs Reno vs NewReno 区别
- BBR（Bottleneck Bandwidth and RTT）算法简介

## 关联页面
[[TCP首部格式]] [[TCP三次握手]] [[TCP四次挥手]] [[TCP流量控制]] [[网络层拥塞控制]]

## 推荐学习路径
先复习 [[TCP三次握手]] 理解连接建立，再观看本视频掌握拥塞控制，最后对比 [[TCP流量控制]] 区分两个控制机制的差异。
