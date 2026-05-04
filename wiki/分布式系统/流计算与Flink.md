---
title: 流计算与Flink
course: 分布式系统
chapter: 分布式计算
difficulty: INTERMEDIATE
tags: [流计算, Flink, 窗口, 事件时间, 水位线, 状态管理]
aliases: [Apache Flink, 流处理, Stream Processing, Flink]
source:
  - "Apache Flink Documentation"
  - "Millwheel: Fault-Tolerant Stream Processing at Google, Akidau et al. (2013)"
  - "The Dataflow Model, Akidau et al. (2015)"
  - "Designing Data-Intensive Applications, Martin Kleppmann, Chapter 11"
updated_at: 2026-05-03
---

## 核心定义

流计算（Stream Processing）是实时处理连续数据流的计算范式，与批处理（Batch Processing）相对。Apache Flink是目前最流行的流计算框架之一，以**真正的流处理**（非微批）和**精确一次（exactly-once）语义**著称。

**核心概念**：

**事件时间（Event Time）与处理时间（Processing Time）**：
- 事件时间：事件实际发生的时间（由数据携带）
- 处理时间：事件被系统处理的时间
- Flink推荐使用事件时间，因为它能正确处理乱序事件

**水位线（Watermark）**：水位线是一个时间戳，表示"所有事件时间小于该时间戳的事件已经到达"。水位线用于触发窗口计算和处理乱序事件。水位线越保守，延迟越高但数据越完整。

**窗口（Window）**：
- **滚动窗口（Tumbling Window）**：固定大小、不重叠
- **滑动窗口（Sliding Window）**：固定大小、可重叠
- **会话窗口（Session Window）**：按活动间隔动态划分
- **全局窗口（Global Window）**：需要自定义触发器

**状态管理**：Flink维护**算子状态（Operator State）**和**键控状态（Keyed State）**。状态存储在**State Backend**中（如RocksDB），支持增量Checkpoint。

**Checkpoint机制**：Flink使用**Chandy-Lamport算法**的变体实现分布式快照——在数据流中插入**屏障（Barrier）**，所有算子对齐Barrier后保存状态。Checkpoint保证了**精确一次语义**。

## 关键结论

- Flink是**真正的流处理**引擎（逐条处理），而非Spark Streaming的微批处理
- **Watermark**是处理乱序事件的核心机制——它在正确性和延迟之间做权衡
- Flink的**精确一次语义**通过Checkpoint + 两阶段提交Sink实现
- **状态管理**是流计算的核心挑战——状态可能很大，需要高效的存储和恢复机制
- Flink的**窗口**机制允许对无界数据流进行有限集上的聚合计算

## 易错点

1. **混淆事件时间和处理时间**：使用处理时间虽然简单，但无法正确处理迟到事件和数据回放。事件时间虽然复杂，但结果更正确
2. **Watermark设置不当**：Watermark太激进会丢失迟到数据，太保守会增加延迟。需要根据数据的乱序程度来调整
3. **忽视状态大小**：键控状态按key分片存储，如果key空间很大或状态更新频繁，可能导致State Backend成为性能瓶颈

## 例题

**题目**：一个实时监控系统使用Flink处理传感器数据流，需要计算每5分钟的平均温度。数据可能乱序到达，最大乱序时间为1分钟。请设计窗口和Watermark策略。

**解答**：

**窗口策略**：
- 使用**滚动事件时间窗口（Tumbling Event Time Window）**
- 窗口大小：5分钟
- 每个窗口覆盖一个5分钟的事件时间范围（如 [00:00, 00:05), [00:05, 00:10) ...）

**Watermark策略**：
- 最大乱序时间：1分钟
- 设置Watermark：`Watermark = 当前最大事件时间 - 1分钟`
- 这意味着：当Watermark到达00:06时，系统认为所有事件时间 < 00:05的事件都已到达
- 此时触发 [00:00, 00:05) 窗口的计算

**处理迟到数据**：
- 设置**允许迟到时间（Allowed Lateness）**：如2分钟
- 窗口触发后，在2分钟内收到的迟到数据仍会更新窗口结果
- 超过2分钟的迟到数据可以输出到**侧输出流（Side Output）**进行特殊处理

**代码示例**：
```java
dataStream
    .assignTimestampsAndWatermarks(
        WatermarkStrategy.<SensorData>forBoundedOutOfOrderness(Duration.ofMinutes(1))
            .withTimestampAssigner((event, timestamp) -> event.getTimestamp())
    )
    .keyBy(SensorData::getSensorId)
    .window(TumblingEventTimeWindows.of(Time.minutes(5)))
    .allowedLateness(Time.minutes(2))
    .sideOutputLateData(lateOutputTag)
    .reduce((a, b) -> new SensorData(a.getSensorId(), (a.getTemp() + b.getTemp()) / 2));
```

## 关联页面

[[Spark核心原理]] [[批流一体架构]] [[消息队列原理]] [[Kafka架构详解]] [[数据一致性实战]]
