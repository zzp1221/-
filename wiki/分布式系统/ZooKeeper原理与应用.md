---
title: ZooKeeper原理与应用
course: 分布式系统
chapter: 消息系统与协调
difficulty: INTERMEDIATE
tags: [ZooKeeper, 分布式协调, ZNode, Watch, Leader选举, 分布式锁]
aliases: [Apache ZooKeeper, ZooKeeper, 分布式协调服务]
source:
  - "ZooKeeper: Wait-free coordination for Internet-ready systems, Hunt et al. (2010)"
  - "Apache ZooKeeper Documentation"
  - "ZAB: High-performance broadcast for primary-backup systems, Junqueira et al. (2011)"
updated_at: 2026-05-03
---

## 核心定义

Apache ZooKeeper是Yahoo开发的分布式协调服务，提供**分布式配置管理**、**命名服务**、**分布式锁**、**Leader选举**、**组成员管理**等功能。ZooKeeper的核心是一个**分层命名空间**（类似文件系统），由**ZNode**组成。

**数据模型**：
- **ZNode**：ZooKeeper的数据节点，可以存储少量数据（默认最大1MB）
- **持久节点（Persistent）**：创建后一直存在，直到显式删除
- **临时节点（Ephemeral）**：与客户端会话绑定，会话结束后自动删除
- **顺序节点（Sequential）**：名称后附加单调递增的序号

**Watch机制**：客户端可以在ZNode上设置Watch，当ZNode发生变化时（创建、删除、数据变更），ZooKeeper通知客户端。Watch是一次性触发的，触发后需要重新设置。

**一致性保证**：ZooKeeper使用**ZAB协议**保证数据一致性：
- **写操作**：由Leader处理，通过ZAB广播到所有Follower
- **读操作**：可以从任意节点读取（可能读到旧数据）
- **顺序一致性**：所有更新按全局顺序执行
- **线性一致性读**：通过 `sync()` 操作 + 读取实现

**典型应用场景**：
- **Leader选举**：利用临时顺序节点实现
- **分布式锁**：利用临时顺序节点实现公平锁
- **配置管理**：将配置存储在ZNode中，通过Watch实时通知变更
- **服务发现**：服务实例注册为临时节点，Watch监听变更
- **分布式队列**：利用顺序节点实现

## 关键结论

- ZooKeeper的核心价值是提供**分布式协调原语**，而不是通用数据存储
- **临时节点**是实现Leader选举和服务发现的关键——进程崩溃后临时节点自动删除
- ZooKeeper的读操作可能返回**过时数据**（从Follower读取），需要线性一致性时使用 `sync()`
- ZooKeeper不适合存储大量数据或高频读写——它是协调服务，不是数据库
- **Session超时**的设置需要权衡：太短会导致网络抖动时频繁断开，太长会导致故障检测延迟

## 易错点

1. **误认为ZooKeeper的读操作是强一致的**：默认情况下，读操作从本地副本返回，可能是过时数据。需要线性一致性时必须先调用`sync()`
2. **忽视Watch的一次性**：Watch触发后必须重新注册，否则会错过后续变更
3. **ZNode数据量过大**：ZooKeeper设计用于存储少量元数据（配置、状态），不适合存储大量数据

## 例题

**题目**：使用ZooKeeper实现Leader选举，有3个客户端参与选举。请描述实现方案。

**解答**：

**实现方案：基于临时顺序节点的Leader选举**

**步骤**：

1. **每个客户端在 `/election` 路径下创建临时顺序节点**：
   ```
   /election/leader_0000000001  (客户端A)
   /election/leader_0000000002  (客户端B)
   /election/leader_0000000003  (客户端C)
   ```

2. **每个客户端获取 `/election` 下所有子节点**，找到**序号最小的节点**：
   - 如果自己是最小的节点，成为Leader
   - 否则，对**序号比自己小的上一个节点**设置Watch

3. **Leader处理逻辑**：
   - 客户端A发现自己是最小节点，成为Leader
   - 客户端A正常工作

4. **Follower处理逻辑**：
   - 客户端B发现最小节点是A，对A设置Watch
   - 客户端C发现最小节点是A，对B设置Watch（只Watch前一个节点，避免惊群效应）

5. **Leader崩溃**：
   - 客户端A崩溃，临时节点 `/election/leader_0000000001` 自动删除
   - ZooKeeper通知客户端B（B对A设置了Watch）
   - 客户端B获取子节点列表，发现自己是最小节点，成为新Leader

**关键设计点**：
- 使用**临时节点**：进程崩溃后自动删除，无需手动清理
- 使用**顺序节点**：保证全局有序，避免并发创建冲突
- 只Watch**前一个节点**：避免惊群效应（所有客户端同时收到通知）

## 关联页面

[[ZAB协议（ZooKeeper）]] [[分布式锁实现]] [[服务发现与注册]] [[etcd与分布式KV]] [[Raft协议详解]]
