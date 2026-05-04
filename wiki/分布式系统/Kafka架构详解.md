---
title: Kafka架构详解
course: 分布式系统
chapter: 消息系统与协调
difficulty: INTERMEDIATE
tags: [Kafka, 消息队列, 分区, 消费者组, 副本, 日志]
aliases: [Apache Kafka, Kafka, Kafka架构, 分布式消息系统]
source:
  - "Kafka: a Distributed Messaging System for Log Processing, Kreps et al. (2011)"
  - "Apache Kafka Documentation"
  - "Designing Data-Intensive Applications, Martin Kleppmann, Chapter 11"
updated_at: 2026-05-03
---

## 核心定义

Apache Kafka是LinkedIn于2011年开源的分布式消息系统，现已成为大数据和实时流处理的核心基础设施。Kafka的设计目标是**高吞吐量**、**低延迟**、**持久化**和**水平扩展**。

**核心概念**：
- **Topic**：消息的逻辑分类，一个Topic可以有多个Partition
- **Partition**：Topic的物理分片，是并行处理和有序性的基本单位。每个Partition是一个**有序的、不可变的消息序列**
- **Broker**：Kafka集群中的服务器节点，存储Partition数据
- **Producer**：将消息发送到Topic的指定Partition
- **Consumer**：从Partition消费消息
- **Consumer Group**：一组消费者协作消费Topic。每个Partition只能被同一Consumer Group中的一个消费者消费

**存储机制**：
- 每个Partition是一个**追加日志（append-only log）**，消息按偏移量（offset）顺序编号
- 消息存储在**Segment文件**中，支持按时间或大小滚动
- 使用**页缓存（page cache）**和**零拷贝（zero-copy）**优化读写性能
- **保留策略**：消息按时间（如7天）或大小保留，过期后删除

**副本机制**：
- 每个Partition有多个副本（Leader + Follower）
- **Leader**处理所有读写请求，**Follower**从Leader同步数据
- Leader故障时，ISR（In-Sync Replicas）中的Follower被选为新Leader
- **acks配置**：acks=0（不等待确认）、acks=1（Leader确认）、acks=all（所有ISR确认）

## 关键结论

- Kafka的**高吞吐量**来源于：顺序IO、页缓存、零拷贝、批量发送、消息压缩
- Kafka保证**分区内有序**，不保证跨分区有序。需要全局有序时使用单分区
- **Consumer Group**实现了**队列模式**（同组内竞争消费）和**发布/订阅模式**（不同组独立消费）的统一
- **ISR机制**是Kafka高可用的核心——只有同步副本才有资格成为Leader
- Kafka的**精确一次语义**（Exactly-Once）通过幂等生产者 + 事务 + 消费者位移提交实现

## 易错点

1. **误解Kafka的消息顺序**：Kafka只保证**单个Partition内**的消息有序。多Partition的消息顺序无法保证。如果业务需要全局有序，只能使用单Partition（牺牲并行性）
2. **忽视Consumer Group的Rebalance**：消费者加入或离开Consumer Group时，会触发Rebalance（重新分配Partition）。Rebalance期间消费会暂停
3. **acks配置不当**：acks=1时，Leader确认后崩溃可能导致数据丢失。acks=all最安全但延迟最高

## 例题

**题目**：一个Kafka集群有6个Broker，Topic "orders" 有12个Partition，副本因子为3。请分析：
（1）每个Broker存储多少个Partition副本？
（2）如果一个Broker宕机，最多有多少个Partition需要Leader切换？
（3）设置min.insync.replicas=2, acks=all时，能否保证数据不丢失？

**解答**：

**（1）每个Broker的Partition副本数**：
- 总副本数 = 12 × 3 = 36
- 平均每个Broker：36 / 6 = **6个副本**

**（2）宕机影响分析**：
- 每个Broker上有6个副本（可能是Leader或Follower）
- 如果Kafka均匀分配，宕机的Broker上有约2个Leader（12/6=2）
- 最多有**6个Partition副本受影响**，其中最多**2个Partition需要Leader切换**
- 其他4个是Follower副本，不影响服务

**（3）数据持久性分析**：
- `min.insync.replicas=2`：至少2个副本同步才算写入成功
- `acks=all`：所有ISR副本确认才算写入成功
- 场景：Leader + 2个Follower都在ISR中（共3个副本）
- 写入成功意味着至少2个副本（包括Leader）已持久化

**结论**：配置 `min.insync.replicas=2, acks=all` 可以保证：
- 最多1个副本丢失时（如1个Follower崩溃），数据不丢失
- 如果2个副本同时丢失（Leader + 1个Follower），可能丢失数据
- 要容忍f个副本丢失，需要 `副本因子 >= min.insync.replicas + f`

## 关联页面

[[消息队列原理]] [[RabbitMQ与AMQP]] [[流计算与Flink]] [[ZooKeeper原理与应用]] [[数据复制策略]]
