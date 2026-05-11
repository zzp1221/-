---
title: "Church-Turing论题"
course: 离散数学
chapter: 可计算性理论
difficulty: ADVANCED
tags: [离散数学, Church-Turing, 可计算性, 图灵机]
aliases: [Church-Turing Thesis, Computability, Turing Machine]
source: "Turing 1936 (On Computable Numbers); Church 1936; Sipser Ch 3-5; Copeland《The Essential Turing》"
updated_at: 2026-05-02
---

## 核心定义

Church-Turing论题断言：所有直观上可计算的函数正好是λ演算可定义的函数(Church)和图灵机可计算的函数(Turing)。这些形式定义等价地刻画了'可计算'——即图灵完备性。物理Church-Turing论题：任何物理上可实现的计算过程都可以被标准图灵机模拟。量子计算不违反Church-Turing论题——量子图灵机等价于普通图灵机(在可计算性上——计算能力完全相同，仅在效率上有潜在优势(量子加速))。

## 图灵机详解

图灵机(TM)由无穷长的纸带(tape)、读写头(head)、有限状态控制器组成。一条指令:(当前状态,读取符号)→(新状态,写入符号,左移/右移)。通用图灵机(UTM)可以通过编码任何TM的描述在带子上模拟该TM——是'存储程序'概念的数学根基。可变体:多带图灵机、非确定图灵机(NTM)、oracle machine(带玄机的TM——超越可计算函数)。停止问题(Halting Problem)是图灵机不可判定的——证明：假设推导出矛盾(对角线法)。

## 关键结论

1. Church-Turing论题不是数学定理——它是关于物理实在的假设 2. λ演算、递归函数、寄存器机、Post系统都与图灵机等价 3. 图灵完备性(Turing-completeness)成为衡量计算系统能力的标准 4. 不可计算问题天然存在于计算机科学中(如死锁检测、最小程序长度) 5. 超计算(hypercomputation)模型试图定义超越图灵的机器——目前仅存在于理论中

## 关联知识点

[[离散数学-有限状态机与正则语言]] [[离散数学-自动机与形式语言]] [[算法设计与分析-NP完全性理论与归约]]
