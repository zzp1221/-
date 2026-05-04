---
title: Actor模型与Akka
course: 分布式系统
chapter: 分布式计算
difficulty: INTERMEDIATE
tags: [Actor模型, Akka, 消息传递, 并发, Erlang, 消息驱动]
aliases: [Actor Model, Akka, 消息驱动, 消息传递并发]
source:
  - "A Universal Modular ACTOR Formalism for Artificial Intelligence, Hewitt et al. (1973)"
  - "Akka Documentation"
  - "Designing Data-Intensive Applications, Martin Kleppmann, Chapter 1"
updated_at: 2026-05-03
---

## 核心定义

Actor模型由Carl Hewitt于1973年提出，是一种基于**消息传递**的并发计算模型。在Actor模型中，**Actor**是计算的基本单元，每个Actor拥有私有状态和一个邮箱（mailbox），通过**异步消息传递**与其他Actor通信。

**Actor的三种行为**：
1. **发送消息**：向其他Actor发送有限数量的消息
2. **创建新Actor**：创建新的Actor来处理子任务
3. **改变行为**：修改对下一条消息的处理方式（状态变更）

**核心原则**：
- **无共享状态**：Actor之间不共享任何可变状态，所有通信通过消息传递
- **异步通信**：消息发送是异步的，发送者不阻塞
- **每条消息串行处理**：每个Actor一次只处理一条消息，避免了并发问题
- **位置透明**：消息发送不关心目标Actor在本地还是远程

**Akka框架**：Akka是JVM上最流行的Actor框架，由Lightbend开发。Akka支持：
- **本地和远程Actor**：同一编程模型支持本地和分布式Actor
- **集群（Cluster）**：Actor分布在集群中的多个节点上
- **持久化（Persistence）**：通过事件溯源（Event Sourcing）持久化Actor状态
- **监督策略（Supervision）**：父Actor监督子Actor的故障，支持"let it crash"哲学

**Erlang/OTP**：Erlang是Actor模型最成功的工业实现，OTP框架提供了强大的容错和热更新能力。WhatsApp、Discord等使用Erlang处理海量并发连接。

## 关键结论

- Actor模型通过**消息传递**避免了共享状态的并发问题（死锁、竞态条件）
- **"Let it crash"**哲学：Actor故障时由监督者决定重启策略，而不是尝试处理所有异常
- Actor模型适合**高并发**、**事件驱动**的场景，如实时通信、游戏服务器、IoT
- Akka Cluster使用**一致性哈希**分布Actor，使用**Gossip协议**传播集群状态
- Actor模型的局限：消息顺序保证取决于通信方式（本地有序、远程可能乱序）

## 易错点

1. **误认为Actor模型不需要考虑并发**：虽然单个Actor串行处理消息，但多个Actor并发执行时，消息的到达顺序可能不确定，仍需要考虑因果一致性
2. **忽视消息传递的语义**：Akka的消息传递默认是"at-most-once"（最多一次），不保证消息到达。需要"at-least-once"或"exactly-once"时，需要额外机制
3. **过度使用Actor**：不是所有并发问题都适合用Actor解决。简单的并发场景使用线程池或协程更高效

## 例题

**题目**：设计一个使用Actor模型的简单聊天系统，需要支持：用户发送消息、消息广播给所有在线用户、用户上下线通知。请设计Actor层次结构。

**解答**：

**Actor层次结构**：

```
ChatSystem（根Actor）
├── UserManager（管理用户Actor）
│   ├── UserActor-用户A
│   ├── UserActor-用户B
│   └── UserActor-用户C
├── ChatRoom（聊天室Actor）
│   ├── 消息广播逻辑
│   └── 在线用户列表
└── NotificationService（通知Actor）
    └── 上下线通知逻辑
```

**各Actor职责**：

**UserActor**（每个用户一个）：
- 维护用户状态（在线/离线、连接信息）
- 接收用户发送的消息，转发给ChatRoom
- 接收广播消息，推送给用户客户端

**ChatRoom**：
- 维护在线用户Actor列表
- 接收消息，广播给所有在线UserActor
- 处理用户加入/离开事件

**UserManager**：
- 管理UserActor的生命周期
- 用户上线时创建UserActor，下线时停止UserActor

**消息流**：
1. 用户A发送消息 → UserActor-A → ChatRoom → 广播给所有UserActor
2. 用户B上线 → UserManager创建UserActor-B → ChatRoom添加用户B → 通知所有UserActor

**容错**：
- UserActor崩溃 → UserManager监督，重启UserActor
- ChatRoom崩溃 → ChatSystem监督，使用持久化恢复状态

## 关联页面

[[消息队列原理]] [[Kafka架构详解]] [[分布式系统概述与挑战]] [[熔断与降级]] [[服务网格Service Mesh]]
