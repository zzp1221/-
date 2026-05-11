---
title: "Rust语言-async/await与Future"
course: Rust语言
chapter: 异步编程
difficulty: ADVANCED
tags: [Rust, async, await, Future, Pin, Executor]
aliases: [Rust Async, Future Trait, Pin/Unpin]
source: "Rust Async Book; Rust Reference: async/await; Tokio官方文档; RFC 2394"
updated_at: 2026-05-02
---

## 核心定义

""Rust的async/await提供零成本异步编程：async关键字将函数/代码块转换为实现Future trait的匿名状态机。Future trait核心：fn poll(self: Pin<&mut Self>, cx: &mut Context<'_>) -> Poll<Self::Output>。async fn在被.await调用前不执行任何代码。编译器将async块转换为枚举(每个await点对应一个variant)，状态在poll调用间保持。

## Pin与自引用结构

""Pin<&mut T>保证被固定的值不会在内存中移动。async生成的状态机是自引用(self-referential)结构——一个字段是另一个字段的引用(等待的future被当前状态机持有引用)。Pin阻止move破坏这些引用。Unpin auto trait标记类型在Pin后仍可安全移动。!Unpin类型的Pin<&mut T>无法获取&mut T(除非通过unsafe)。Pin::new_unchecked和Pin::as_mut提供安全封装。

## 关键结论

""1. async fn返回impl Future——名称是不能直接被引用的不透明类型 2. 没有executor时Future什么也不做(需要tokio/async-std轮询) 3. .await让出当前任务给executor 4. Send trait决定Future是否能跨线程移动 5. async move block获得所有权的变量而非引用

## 关联知识点

""[[Rust语言-所有权与借用]] [[Rust语言-并发原语与Send/Sync]] [[Rust语言-闭包与Fn特征]]
