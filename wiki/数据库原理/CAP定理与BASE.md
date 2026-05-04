---
title: CAP定理与BASE模型
course: 数据库原理
chapter: 分布式数据库
difficulty: ADVANCED
tags: [CAP定理, BASE, 最终一致性, 分布式系统, PACELC, 一致性模型]
aliases: [CAP Theorem, BASE Model, Eventual Consistency, Brewer's Theorem, PACELC]
source:
  - 王珊《数据库系统概论》第5版
updated_at: 2026-05-02

---

## 核心定义

CAP定理（CAP Theorem / Brewer's Theorem）是分布式系统领域的基本定理，由Eric Brewer于2000年提出。CAP定理指出：一个分布式共享数据系统在网络分区（Network Partition——P）发生时，只能同时满足以下三个属性中的两个，无法三者同时满足——一致性（Consistency——所有节点在同一时刻看到相同数据的最新副本）、可用性（Availability——每一个非失败节点对接收到的请求必须返回非错误的响应（即总能响应））和分区容忍性（Partition Tolerance——当网络故障导致节点之间消息丢失或延迟的情况下，系统仍然能够继续运行）。由于网络分区故障是分布式系统不可避免的（网络不可靠——交换机故障、丢包、硬件错误、跨区域通信延迟）——所以P是实际上的必须保障，这导致在发生分区时系统设计只能在C（一致性）和A（可用性）之间做选择。放弃C意味着选择最终一致性（AP系统——像Cassandra/DynamoDB/CouchDB在网络分区时继续进行读写但可能返回暂时不一致的数据），放弃A意味着选择强一致性（CP系统——如HBase/ZooKeeper在分区时为了维护一致可拒绝部分节点的写入）。传统单节点的RDBMS天然满足CA但在需要跨节点扩展时陷入CAP约束。

BASE模型（Basically Available, Soft state, Eventually consistent）是对CAP中AP系统行为的概括——它是对ACID严格一致性的"妥协"性后续解决方案。BASE指出分布式数据系统应该达到：基本可用（Basically Available——即使部分节点故障系统整体依然响应，返回的可能不是最新数据但至少提供响应），软状态（Soft State——系统的状态可能随时间即使无输入也会变化，因为数据同步尚未完成），最终一致性（Eventual Consistency——在系统中没有更新足够长时间后，所有副本将对最新的数据达成一致状态）。BASE不是反对ACID——而是指出系统可牺牲尽速一致性以换取高可用性和水平伸缩。

## 关键结论

- CAP中"一致性"不是ACID中的C：在CAP的C是分布式系统中线性一致性（Linearizability——所有节点操作的顺序看起来像单一副本串行执行的效果，即每个读都反映前一个写的结果）。ACID的C指事务将数据库从一个一致状态带入另一个一致状态——两者是不同的概念，不能直接互换
- PACELC定理是CAP的延伸扩展：当系统正常运行未出现网络分区时（没有P——Else部分），系统需要在延迟（Latency——L）与一致性（Consistency——C）之间再做一层权衡。即CAP是"有P时的选择为C或A"，PACELC并指出"没有P时系统选择L(低延迟弱一致)或C(高延迟强一致)"——完善了CAP原来只描述分区情况下的局限
- 分布式一致性协议类型：(a)强一致协议——Paxos/Raft——主节点通过法定数确保每次写都在多数节点得到确认返回给客户端——保证线性一致性但延迟高；(b)最终一致协议——Gossip协议——每个节点与随机的其他节点交换信息逐步将新数据传播——在无故障后最终达到一致
- 现实系统中一致性级别多样化：除线性一致性和最终一致性外还有因果一致性（有因果依赖关系的操作在所有节点上以相同顺序呈现）、会话一致性（在一个客户端会话中所有操作保持一致性可见）、单调读一致性（客户端的一次读取只会在该客户端后续读取中一直看到该值或更新的值不会倒退）、单调写一致性（客户端的写按顺序得到系统的顺序化处理）
- CAP定理对架构的指导意义：在实践中互联网应用的层级剪裁——核心交易系统（支付结算）偏向CP的一致性以保证资金一致；社交媒体的动态墙/状态更新偏向AP（短不一致不是致命缺陷且需要极高可用）；中间层通过组合不同的数据库采取"基于资源、按需求选择C或A"的混合模式

## 易错点

1. **CAP并不是"三选二"的在正常情况下的约束**：CAP中的选择仅在网络分区发生时出现——在正常运行、网络无故障的情况下分布式系统可以同时满足C和A（当然也要容忍P）。很多人误会所有时间点只能满足两个指标——这是对定理的过度简单化。

2. **"最终一致性等于无一致性保证"是误解**：最终一致依赖系统在故障恢复后能收敛——符合规范的最终一致系统必须指出"在不发生新更新的条件下收敛"的最大时限。但由于不能指定时限——最终一致数据库不适合需要等待最新数据的返回判断场景（产生读己写错误）。

3. **可用性在CAP定义中受限**：可用性要求"每一个非失败节点"都能响应请求——在CP系统中当网络分区时，非主分区节点被系统要求拒绝写请求→不可用。所以CP的可用性下降往往体现为关闭部分分区的写操作。

4. **BASE与ACID不是完全对立的关系**：很多系统在不同的层次使用不同的模型——底层存储最终一致+上层应用层通过补偿事务和幂等保证最终正确的业务状态（即基于工作流的补偿式Saga长事务取代ACID跨服务两阶段提交）。两者的组合正是微服务架构的普遍实践。

## 例题

**例题1**：设计一个跨区域的分布式键值存储的使用场景——需要决定CAP选取：两地三中心的数据复制方案，分析CAP取舍及其一致性级别。

**解答**：如果两个数据中心之间网络中断（P发生）——(a) CP方案：使从中心停止接受写入（返回错误），保持主中心的数据仍然完全一致——客户端不能发写到从中心等待恢复后同步；(b) AP方案：两个中心继续各自接受写入→用向量时钟解决后续冲突——当网络恢复后多版本解决冲突再由应用程序进行冲突处理（如latest wins或用户合并）。权衡——面向金融数据ACP更高（CP方案确保数据正确），但面向社交内容读/写的时效则多AZ下AP方案保障可用性高。

**例题2**：解释DynamoDB的法定读写数公式R+W>N←RFC不适用于哪些场景，并示例。

**解答思路**：(R+W>N)保证在必定存在一个节点保存最新写和读的交集，因此读可拿到最新。但若选择W=1和R=1（缺少交集)无法保证读到最新数据（最终一致），适合于高吞吐低延迟低一致需求——会话缓存/cdn内容配置这类可以容忍稍旧的数据。

## 代码示例

分布式键值系统模拟——展示网络分区时的行为：

```python
class DistributedNode:
    def __init__(self, node_id: int, is_primary: bool = False):
        self.id = node_id
        self.data = {}
        self.partitioned = False
        self.is_primary = is_primary

    def write(self, key, value):
        if self.partitioned and not self.is_primary:
            # CP模式：非主分区拒绝写入
            raise Exception(f"Node {self.id}: partition detected, write rejected (CP)")
        self.data[key] = value
        return True

    def read(self, key):
        if self.partitioned and not self.is_primary:
            return self.data.get(key, "STALE_DATA")  # AP模式：返回可能过时的数据
        return self.data.get(key, None)
    
    def simulate_partition(self):
        self.partitioned = True

# 使用
node1 = DistributedNode(1, is_primary=True)
node2 = DistributedNode(2, is_primary=False)
node1.write("x", 100)
node2.simulate_partition()
# node2 当前返回过时数据（AP行为）或拒绝写（CP行为）
```

分布式一致性级别的配置示例（Cassandra CQL）：

```sql
-- 写入一致性级别 QUORUM (保证法定数副本写入)
CONSISTENCY QUORUM;

-- 读取一致性级别 QUORUM (同样法定数保证读最新)
-- 由于R+W=QUORUM+QUORUM > 副本数 → 保证强一致
SELECT * FROM users WHERE user_id = '1001';

-- 使用LOCAL_QUORUM 保障本地DC内的一致
CONSISTENCY LOCAL_QUORUM;
```

## 关联页面

[[NoSQL概述]] [[事务-ACID]] [[NewSQL]] [[数据库恢复]]
