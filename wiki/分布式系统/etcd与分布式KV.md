---
title: etcd与分布式KV
course: 分布式系统
chapter: 消息系统与协调
difficulty: INTERMEDIATE
tags: [etcd, 分布式KV, Raft, Kubernetes, 配置管理, 服务发现]
aliases: [etcd, 分布式键值存储, 分布式KV]
source:
  - "etcd Official Documentation"
  - "CoreOS etcd: A Distributed, Reliable Key-Value Store, v0.4.6 Documentation"
  - "In Search of an Understandable Consensus Algorithm, Ongaro & Ousterhout (2014)"
updated_at: 2026-05-03
---

## 核心定义

etcd是CoreOS开发的分布式键值存储，使用**Raft共识算法**保证数据一致性。etcd是Kubernetes的默认数据存储，广泛用于**配置管理**、**服务发现**、**分布式锁**和**Leader选举**。

**核心特性**：
- **强一致性**：基于Raft协议，写入操作在多数派确认后返回，保证线性一致性
- **键值存储**：分层键空间（类似文件系统路径），支持前缀查询和范围查询
- **Watch机制**：监听键或前缀的变化，实时通知客户端
- **Lease（租约）**：为键设置TTL，到期自动删除。用于实现临时节点和心跳
- **事务（Transaction）**：支持If-Then-Else的原子事务（CAS操作）

**Raft实现**：
- etcd集群通常由3个或5个节点组成（奇数个，便于多数派投票）
- Leader处理所有写请求，Follower同步日志
- Leader选举超时默认为1000ms，心跳间隔为100ms

**与ZooKeeper的对比**：
- etcd使用**Raft**（更易理解），ZooKeeper使用**ZAB**
- etcd使用**HTTP/gRPC**接口，ZooKeeper使用**自定义协议**
- etcd支持**Watch前缀**（一次Watch多个键），ZooKeeper的Watch是一次性的
- etcd原生支持**TTL和Lease**，ZooKeeper通过临时节点实现

**Kubernetes中的应用**：
- 存储所有集群状态（Pod、Service、ConfigMap等）
- 服务发现：通过Endpoints对象
- Leader选举：Controller Manager和Scheduler的Leader选举
- 配置管理：ConfigMap和Secret存储在etcd中

## 关键结论

- etcd的**强一致性**使其适合存储关键的配置和状态数据，但写入性能低于AP系统
- **Lease机制**是实现分布式锁和服务发现的基础——结合Watch实现实时通知
- etcd的**事务**支持CAS（Compare-And-Swap），是实现分布式锁和乐观锁的关键
- etcd集群推荐**奇数个节点**（3或5），偶数个节点在故障时可能出现脑裂
- **碎片整理（Compaction）**和**碎片化（Defragmentation）**是etcd运维的重要任务

## 易错点

1. **高估etcd的写入吞吐量**：etcd是CP系统，写入需要Raft共识，吞吐量有限（约10K QPS）。不适合存储高频变更的数据
2. **忽视Watch的版本管理**：Watch需要指定revision，否则可能错过中间变更。etcd支持从特定revision开始Watch
3. **Lease过期导致锁失效**：如果业务处理时间超过Lease的TTL，锁会自动过期，可能导致并发问题。需要定期续租

## 例题

**题目**：使用etcd实现一个分布式锁，要求：
1. 互斥：同一时刻只有一个客户端持有锁
2. 防死锁：客户端崩溃后锁自动释放
3. 可重入：同一客户端可以多次获取锁

**解答**：

**实现方案：基于etcd Lease和Revision的分布式锁**

**获取锁**：
```python
def acquire_lock(client, lock_key, value, ttl=10):
    # 1. 创建Lease
    lease = client.lease(ttl)
    
    # 2. 创建键（带Lease），获取Revision
    #    使用事务保证原子性
    txn = client.transactions()
    txn.If(
        # 如果键不存在
        client.transactions.value(lock_key).does_not_exist()
    ).Then(
        # 创建键，绑定Lease
        client.transactions.put(lock_key, value, lease)
    ).commit()
    
    # 3. 记录Revision，用于排序（公平锁）
    return lease, revision
```

**释放锁**：
```python
def release_lock(client, lock_key, lease):
    # 撤销Lease，键自动删除
    lease.revoke()
```

**防死锁**：
- Lease绑定TTL（如10秒），客户端崩溃后Lease过期，键自动删除
- 客户端需要定期**续租（KeepAlive）**延长Lease有效期

**可重入实现**：
- 使用`lock_key = /locks/{resource}/{client_id}`
- 同一客户端的多次获取创建不同的键
- 通过Revision排序实现公平锁

**完整公平锁流程**：
1. 客户端创建临时键 `/locks/resource/0000000001`（带Lease）
2. 获取所有键，如果自己是最小的Revision，持有锁
3. 否则Watch前一个Revision的键
4. 前一个键删除时，重新检查自己是否最小

## 关联页面

[[ZooKeeper原理与应用]] [[Raft协议详解]] [[分布式锁实现]] [[服务发现与注册]] [[Leader选举]]
