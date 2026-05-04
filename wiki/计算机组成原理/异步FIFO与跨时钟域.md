---
title: "异步FIFO与跨时钟域设计"
course: 计算机组成原理
chapter: 数字设计
difficulty: ADVANCED
tags: [计算机组成原理, 异步FIFO, 跨时钟域, CDC, 格雷码]
aliases: [Asynchronous FIFO]
source: "Simulation and Synthesis Techniques for Asynchronous FIFO Design (Cummings SNUG 2002); 数字集成电路设计"
updated_at: 2026-05-02
---

## 核心定义

异步FIFO在写时钟域和读时钟域之间安全传输数据。核心挑战：多比特跨时钟域传递指针可能产生亚稳态。解决方法：格雷码指针(相邻值仅1位不同)→双触发器同步器(打两拍消亚稳态)→比较格雷码指针判空满。空条件：写指针==读指针(同值)。满条件：写指针超前读指针一圈(写/读方向相反最高2位不同，其余位相同)。

## 关键结论

1. 格雷码指针天然编码了指针间的关系——比二进制更安全 2. 满条件的判断是异步FIFO最难的部分 3. 跨时钟域信号：单比特→双触发同步器，多比特→握手或异步FIFO 4. SoC/IP设计中CDC是芯片失败的头号原因

## 关联页面

[[时序与时钟]] [[握手协议与总线]]
