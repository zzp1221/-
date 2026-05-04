---
title: "实时调度算法（RMS与EDF）"
course: 操作系统
chapter: 进程调度
difficulty: ADVANCED
tags: [操作系统, 实时调度, RMS, EDF, 单调速率]
aliases: [Rate Monotonic Scheduling, Earliest Deadline First]
source: "Real-Time Systems (Liu & Layland 1973); Hard Real-Time Computing Systems (Buttazzo)"
updated_at: 2026-05-02
---

## 核心定义

实时系统调度要求任务在截止时间前完成。RMS（单调速率调度）：周期越短优先级越高，静态优先级可抢占，CPU利用率上界U≤n(2^(1/n)-1)，n→∞时U≤ln2≈69.3%。EDF（最早截止时间优先）：截止时间越近优先级越高，动态优先级可抢占，CPU利用率可达100%。

## 关键结论

1. RMS是最优的静态优先级调度算法 2. EDF是最优的动态优先级调度算法 3. 实际RTOS多使用混合方案 4. 优先级反转问题需要优先级继承协议(PIP)解决

## 关联页面

[[优先级调度]] [[优先级反转]] [[进程调度]]
