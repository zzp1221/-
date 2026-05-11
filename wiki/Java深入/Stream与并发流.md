---
title: "Java深入-Stream与并发流"
course: Java深入
chapter: 函数式编程
difficulty: INTERMEDIATE
tags: [Java, Stream, parallelStream, 函数式编程, 并行]
aliases: [Java Stream API, Parallel Streams, Stream Pipeline]
source: "Java官方文档 java.util.stream; Urma et al.《Modern Java in Action》; Oracle Stream教程"
updated_at: 2026-05-02
---

## 核心定义

Stream API(Java 8)提供声明式集合处理。核心结构：源(source) → 0+中间操作(intermediate,惰性——filter/map/sorted/distinct) → 终端操作(terminal——collect/forEach/reduce/count)。Stream不存储数据(仅是计算视图),不可重用(一个Stream只能消费一次)。中间操作是惰性的——在终端操作触发后才执行。Stream并行度默认是ForkJoinPool.commonPool()线程数(availableProcessors - 1)。

## 并行流陷阱

parallelStream使用Fork/Join框架自动分解工作。但并行不一定更快——影响因素:数据大小(数据太少,分解开销>并行收益)、装箱(原始类型流IntStream/LongStream优于Stream<Integer>)、collect的可合并性(ArrayList合并需复制,ConcatCollectors更差)。状态中间操作(sorted/distinct)在并行流中开销显著。并行流不应在共享的ForkJoinPool中被阻塞(IO操作)——应使用自定义executor。

## 关键结论

1. 永远在并行流和非并行流版本间基准对比 2. 原始类型流(IntStream/DoubleStream)和collect更适合并行 3. 不要在并行流中使用非线程安全的累加器(改用collect) 4. forEachOrdered保证顺序但牺牲并行度 5. Spliterator特性(ORDERED/SIZED/SUBSIZED)影响并行拆分效率 6. reduce是有偏关联操作时并行结果非确定

## 关联知识点

[[Java深入-泛型擦除与类型安全]] [[Rust语言-迭代器与组合器]] [[算法设计与分析-分治与递归]]
