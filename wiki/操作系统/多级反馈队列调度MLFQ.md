---
title: "多级反馈队列调度（MLFQ）"
course: 操作系统
chapter: 进程调度
difficulty: INTERMEDIATE
tags: [操作系统, MLFQ, 进程调度, 优先级, 时间片]
aliases: [Multilevel Feedback Queue]
source: "Operating Systems: Three Easy Pieces (Arpaci-Dusseau) 第8章"
updated_at: 2026-05-02
---

## 核心定义

MLFQ是最实用的通用调度算法，同时优化周转时间和响应时间。规则：1.优先级高的队列先调度 2.同优先级队列内时间片轮转 3.新进程进入最高优先级 4.用完时间片降优先级，主动让出CPU保持优先级 5.定期将所有进程提升到最高优先级（防止饥饿）。

## 关键结论

1. 无需预知进程行为，自适应CPU密集vs IO密集 2. 饥饿问题通过priority boost解决 3. Windows NT、macOS、Linux(CFS前)都使用MLFQ变体 4. 博弈问题：进程可能在时间片结束前主动IO来保持高优先级

## 关联页面

[[先来先服务FCFS]] [[短作业优先SJF]] [[时间片轮转调度]] [[优先级调度]]
