---
title: "Rust语言-并发原语与Send/Sync"
course: Rust语言
chapter: 并发编程
difficulty: ADVANCED
tags: [Rust, Send, Sync, Arc, Mutex, Channel, 并发]
aliases: [Send/Sync Auto Traits, Arc<Mutex<T>>, Rust Channels]
source: "The Rustonomicon: Send and Sync; Rust Reference: Send/Sync; Mara Bos《Rust Atomics and Locks》"
updated_at: 2026-05-02
---

## 核心定义

""Send和Sync是Rust并发安全的两大auto trait。Send：类型值的所有权可以安全转移到另一个线程(几乎所有类型都Send,除了Rc/RefCell/裸指针)。Sync：类型的共享引用&T可以在多个线程间安全共享(当&T: Send时T: Sync)。Mutex<T>让T: Send成为Mutex<T>: Send+Sync(提供了内部同步)。Arc<T>: Send+Sync当T: Send+Sync。这实现了编译期数据竞争消除。

## Arc与Mutex实战

""Arc<Mutex<T>>是Rust并发中最常见的共享可变状态模式：Arc提供共享所有权+引用计数,Mutex提供内部可变性和互斥访问。Mutex::lock()返回LockResult<MutexGuard<T>>,MutexGuard实现了Deref/DerefMut和Drop(自动解锁)。std::sync::mpsc提供多生产者单消费者通道——Sender可克隆(多线程发送),Receiver只能由一个线程接收。crossbeam提供的MPMC通道性能更优。

## 关键结论

""1. Send/Sync是unsafe auto trait——标准库类型为它们提供安全抽象 2. 手动实现Send/Sync需要unsafe impl 3. 编译器自动为composite type推导Send/Sync 4. Poisoning：持有Mutex的线程panic时Mutex被毒化(poisoned) 5. Barrier/RwLock/Condvar使用频率更低但有特定场景

## 关联知识点

""[[Rust语言-所有权与借用]] [[Rust语言-async/await与Future]] [[操作系统-同步与死锁]]
