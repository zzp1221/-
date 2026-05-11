---
title: "Go语言-sync包深入"
course: Go语言
chapter: 并发编程
difficulty: ADVANCED
tags: [Go语言, sync, Mutex, WaitGroup, atomic]
aliases: [Go sync package, sync.Mutex, sync/atomic]
source: "Go标准库sync包文档; Go Blog: Go 1.18 sync additions; Go Memory Model"
updated_at: 2026-05-02
---

## 核心定义

""sync包提供基本同步原语。sync.Mutex(互斥锁)：Lock()阻塞直到获取锁,Unlock()释放。sync.RWMutex(读写锁)：RLock/RUnlock允许并发读,Lock()写锁排斥所有读锁和写锁。sync.WaitGroup：Add(1)增计数,Done()减计数,Wait()阻塞直到计数归零。sync.Once：确保函数只执行一次,基于原子操作实现。sync.Cond：条件变量,Wait()释放锁并等待Signal/Broadcast。

## sync/atomic详解

""sync/atomic提供硬件级别的原子操作：AddInt64/AddUint64(原子加),LoadInt64(原子读),StoreInt64(原子写),CompareAndSwapInt64(CAS),SwapInt64(原子交换)。Go 1.19新增atomic.Int64等类型安全包装。原子操作不用锁，性能极高(~1ns级别)，但不能替代互斥锁用于保护多个变量的不变式。atomic.Value提供任意类型的原子存储与加载。

## 关键结论

""1. Mutex零值即可用 2. 不可复制Mutex(go vet检测) 3. WaitGroup的Add必须在goroutine外调用 4. atomic不能替代channel进行goroutine同步 5. Go 1.18的sync.Map优化了高并发读多写少场景

## 关联知识点

""[[Go语言-Goroutine与通道]] [[Go语言-Context与取消传播]] [[操作系统-同步与死锁]]
