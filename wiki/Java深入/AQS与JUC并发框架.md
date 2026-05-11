---
title: "Java-AQS与JUC并发框架"
course: Java深入
chapter: 并发
difficulty: ADVANCED
tags: [Java, 并发, AQS, JUC, Lock, 线程池]
aliases: [AQS, AbstractQueuedSynchronizer, JUC]
source: "Java SE Documentation java.util.concurrent; Doug Lea《Java并发编程实战》"
updated_at: 2026-05-02
---

## 核心定义

AQS(AbstractQueuedSynchronizer)是JUC包的核心框架，基于FIFO双向队列+int state实现同步器。CLH变体节点：线程被封装为Node加入等待队列，自旋+信号的方式等待。state>0表示被占有，state=0表示可用。模板方法：tryAcquire/tryRelease/tryAcquireShared/tryReleaseShared由子类定义获取/释放语义。

## 基于AQS的实现

ReentrantLock: tryAcquire通过CAS设置state从0→1，重入时state++。CountDownLatch: state=count，await等待state=0，countDown()通过CAS减state。Semaphore: state=permits，tryAcquireShared当state>0时CAS减state。CyclicBarrier不使用AQS而是ReentrantLock+Condition。

## 线程池原理

ThreadPoolExecutor: corePoolSize核心线程常驻，最大线程数maximumPoolSize，超过corePoolSize的线程空闲keepAliveTime后被回收。workQueue: 无界队列/有界队列/SynchronousQueue直传模式。拒绝策略: CallerRuns/Abort/Discard/DiscardOldest。

## 关联知识点

[[Java-内存模型JMM]] [[Java-JVM架构与字节码]]
