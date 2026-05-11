---
title: "Java-GC算法与调优"
course: Java深入
chapter: 内存管理
difficulty: ADVANCED
tags: [Java, GC, 垃圾回收, G1, ZGC, JVM调优]
aliases: [Garbage Collection, G1GC, ZGC]
source: "Oracle G1 GC Documentation; Plumbr GC Handbook"
updated_at: 2026-05-02
---

## 核心定义

JVM的自动内存管理通过GC(垃圾回收)实现。Serial GC: 单线程标记-清除-整理，适合客户端应用。Parallel GC(JDK5): 多线程并行Stop-The-World回收，吞吐量优先。CMS(JDK5-14): 并发标记清除，低延迟目标但可能碎片化。G1(JDK7+, JDK9默认): 区域化(Region)GC，可预测暂停时间，并发标记+STW整理。ZGC(JDK11+): 亚毫秒暂停时间(<1ms)，染色指针(colored pointers)无需读屏障停顿，JDK15转为production-ready。

## G1详解

G1将堆划分为大小相等的Region。Young GC(Eden/Survivor Region): STW复制到空Region。Mixed GC: 在Young GC基础上额外回收部分Old Region(Garbage-first: 优先回收垃圾最多的Region)。并发标记周期(Concurrent Mark): 初始标记(STW很短)→根区域扫描(并发)→并发标记→重新标记(STW快)→清除(并发)。

## 调优参数

-Xms/-Xmx: 初始/最大堆。G1: -XX:MaxGCPauseMillis=200ms, -XX:InitiatingHeapOccupancyPercent=45(IHOP阈值触发并发标记)。ZGC: -XX:ZCollectionInterval(两次GC最小间隔)。开启GC日志分析: -Xlog:gc*:file=gc.log+GCViewer/GCeasy可解析可视化。

## 关联知识点

[[Java-JVM架构与字节码]] [[Java-内存模型JMM]]
