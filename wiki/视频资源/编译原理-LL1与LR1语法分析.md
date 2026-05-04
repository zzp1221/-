---
title: 计算机组成原理-CPU流水线设计（视频）
course: 计算机组成原理
chapter: 中央处理器CPU
difficulty: ADVANCED
tags: [流水线, Pipeline, 数据冒险, 控制冒险, 结构冒险, 转发, 分支预测, 视频]
aliases: [CPU Pipeline, Instruction Pipeline]
source:
  - 计算机组成与设计 Patterson & Hennessy 第4章
  - 哈工大-计算机组成原理 MOOC
updated_at: 2026-05-02
video_url: https://www.bilibili.com/video/BV1t4411e7LH
video_platform: bilibili
video_author: 哈工大-刘宏伟
video_duration: "48:20"
---

## 视频简介

哈工大经典课程，用时序图清晰展示 MIPS 五段流水线（IF-ID-EX-MEM-WB）的数据通路和控制信号，配合大量的流水线时空图分析三种冒险（结构/数据/控制）的成因，再逐一讲解转发（Forwarding）、流水线暂停（Stall）、分支预测（Branch Prediction）等解决方案。

适合学完单周期 CPU 后，理解现代处理器如何通过流水线并行提高指令吞吐率。

## 覆盖知识点
- MIPS 五段流水线：IF、ID、EX、MEM、WB
- 流水线寄存器与时空图
- 结构冒险：资源冲突与解决（分离指令/数据 Cache）
- 数据冒险：RAW/WAR/WAW 与转发（Forwarding）
- 控制冒险：分支延迟槽、静态/动态分支预测
- 流水线性能：吞吐率、加速比、CPI 计算

## 关联页面
[[指令系统]] [[CPU结构与数据通路]] [[Cache缓存]] [[指令流水线]] [[分支预测]] [[旁路转发]]

## 推荐学习路径
先阅读 [[CPU结构与数据通路]] 理解单周期 CPU，再观看本视频掌握流水线，最后复习 [[Cache缓存]] 理解存储层次如何配合流水线工作。
