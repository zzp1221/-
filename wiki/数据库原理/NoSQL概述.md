---
title: NoSQL概述
course: 数据库原理
chapter: NoSQL数据库
difficulty: INTERMEDIATE
tags: [NoSQL, 非关系型数据库, BASE, 大数据, 水平扩展, 分布式数据库]
aliases: [NoSQL Overview, Not Only SQL, Non-Relational Database]
source:
  - 王珊《数据库系统概论》第5版
updated_at: 2026-05-02

---

## 核心定义

NoSQL（Not Only SQL / Non-Relational）是一类不同于传统关系型数据库（RDBMS）的数据库管理系统的统称。NoSQL数据库摒弃了关系模型中的固定表结构（Schema-less）、ACID强事务（使用BASE最终一致性替代）、连接操作和SQL作为统一查询语言。NoSQL数据库的设计初衷是解决互联网应用（社交网络、电商平台、物联网传感器海量数据）中单一RDBMS面临的三大瓶颈：（1）横向扩展困难——RDBMS的扩展主要靠"垂直缩放"（换更强大的CPU/内存/存储）成本呈指数增长，而NoSQL通过"水平扩展"（增加普通商用服务器节点组成集群）近乎线性地扩展容量和吞吐量；（2）Schema灵活性问题——半结构化和无结构数据（JSON文档、键值对、图关系、时序数据）不适合事先用严格的行/列定义描述，NoSQL提供动态Schema或完全无Schema的存储方式；（3）高并发低延迟——互联网交互对短请求（毫秒级）有严格要求，传统RDBMS的表连接和事务锁开销对互联网读/写而言过大。NoSQL并不是"没有SQL"，而是认为并非所有场景都需要SQL——NoSQL是对以关系数据库为唯一的传统方案的有益补充，在大型架构中常出现"SQL + NoSQL"的多数据库异构架构（Polyglot Persistence）——将不同形态数据归于其合适的数据库类型。

## 关键结论

- NoSQL四大类别：键值存储（Key-Value Store——Redis、DynamoDB、Riak），列族存储（Wide-Column Store——HBase、Cassandra、Bigtable），文档存储（Document Store——MongoDB、CouchDB、Elasticsearch），图数据库（Graph Database——Neo4j、OrientDB、JanusGraph），每种分别适用于不同的数据访问模式
- 关系模型的核心取舍——规范化需要表连接（JOIN开销昂贵），ACID全局一致性协调跨节点事务成本过高（2PC在分布式下的性能瓶颈）→ NoSQL拥抱去规范化（Denormalization）和BASE最终一致性（Basically Available基础可用, Soft state软状态, Eventually consistent最终一致）
- 数据分片（Sharding）机制：NoSQL将数据按分片键（Shard Key）哈希或范围划分自动分布到多个节点上——应用层无须感知分片逻辑（数据库自动路由请求到持有该分片的节点），这是水平扩展的核心手段。RDBMS在MySQL层面需要应用层或中间件做分片——失去关系查询能力
- CAP定理与NoSQL：一个大规模分布式数据系统在网络分区（P——Partition tolerance）发生时，只能在一致性(C)和可用性(A)之间选则只保留其中一项。大多数NoSQL数据库选择AP——分区发生时可继续提供服务但不保证各节点数据一致；少数选择CP——确保所有节点返回最新值但可能导致部分节点不可用。传统基于单一主库的RDBMS在CAP上位于CA附近——分区时无法保证完整系统
- NoSQL的一致性模型：从强一致→最终一致→因果一致→读自己写一致→单调读/单调写一致——是逐步变弱的，通过多版本、法定人数读写（Quorum-based Read/Write）及版本向量（Vector Clock）进行冲突检测与解决

## 易错点

1. **"NoSQL取代SQL"是夸大**：NoSQL只适合大数据和高扩展——不支持复杂查询（JOIN,聚合,子查询）在适用场景中受到严重限制。实际生产中使用的是多模型持久化的架构——关系数据库仍然处理结构化业务数据，NoSQL处理会话/缓存、日志、推荐图谱、时序数据等。

2. **"最终一致性等于数据不正确"不对**：最终一致性——在写入高峰期各复本存在临时延迟直到最终收敛。适用于不要求时刻看到最新数据的应用（社交媒体推文、商品评分、日志分析），不能用于支付/库存等强一致场景（仍需ACID）。

3. **NoSQL不应该没有Schema设计**：虽然NoSQL允许多变Schema，但若应用层不加任何结构的约束，数据污染和查询效率低下会快速积累——所以需要"应用层 Schema 管控"保证数据质量。

4. **MongoDB等文档数据库不是关系模型的实现**：尽管看起来像以JSON格式存储的"行"——但底层完全无表约束、无物理行的顺序、无强制Join——优化和查询策略截然不同于RDBMS，迁移时不能直接照搬关系模式。

## 例题

**例题1**：比较关系型数据库和NoSQL在存储海量用户行为日志场景（数十TB写入频率极高、查询基于时间范围聚合）上的适合程度。

**解答**：RDBMS劣势——(1)水平写扩展需手动分片+中间件破坏了关系查询能力；(2)固定表结构难以适应多种事件的动态属性；(3)ACID对日志实时写入引入事务开销。NoSQL优势——Cassandra或HBase的按时间范围有序存储+动态添加列+自然时间顺序分片支持无缝扩展和高写入率，聚合查询可以用流处理引擎补充。NoSQL在此更适合原始日志存储。

**例题2**：在选用键值数据库vs文档数据库时考虑哪些因素？

**解答思路**：键值在查询模式为"仅通过主键取得值"(不分析值内属性)时提供极快O(1)响应的缓存风格的使用。文档数据库适用需对文档内部属性进行索引/过滤/排序（查询包含字段条件）且有嵌套结构。想按值的内容筛选→必须用文档型（MongoDB能对文档中的字段建立辅助索引和查询，键值数据库无法做此级过滤）。

## 代码示例

简单对比——向两种存储系统写入相同的数据：

```sql
-- 关系型表结构
CREATE TABLE user_logs (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    event_type VARCHAR(50),
    log_time TIMESTAMP,
    details TEXT,
    INDEX (user_id, log_time)
);
INSERT INTO user_logs(user_id, event_type, log_time, details)
VALUES (1001, 'click', NOW(), '{"button":"buy"}');
```

```javascript
// MongoDB (文档型) - 直接插入JSON文档
db.user_logs.insertOne({
    user_id: 1001,
    event_type: "click",
    log_time: new Date(),
    details: { button: "buy", page: "/cart" }
});
// 无需事先定义Schema
```

```bash
# Redis (键值型) - Hash结构
HSET user:1001:log:{timestamp} event_type "click" button "buy"
# 通过key直接检索
```

## 关联页面

[[NoSQL-键值与文档]] [[NoSQL-列族与图]] [[CAP定理与BASE]] [[NewSQL]]
