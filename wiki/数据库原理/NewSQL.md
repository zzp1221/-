---
title: NewSQL数据库
course: 数据库原理
chapter: NewSQL
difficulty: ADVANCED
tags: [NewSQL, 分布式SQL, TiDB, CockroachDB, Spanner, 分布式事务, HTAP]
aliases: [NewSQL, Distributed SQL, Google Spanner, TiDB, CockroachDB]
source:
  - 王珊《数据库系统概论》第5版
updated_at: 2026-05-02

---

## 核心定义

NewSQL是一类新型分布式关系数据库系统，目标是在保持传统关系型数据库ACID事务支持和SQL查询能力的同时，实现类似NoSQL系统的高水平扩展性和高并发吞吐。NewSQL的核心思路是"重新设计架构而非对既有RDBMS加分布式补丁"——从零开始构建分布式无共享（Shared-Nothing）架构，将数据自动分区到多节点、通过分布式一致性协议（MVCC快照隔离+多节点共识）保证跨节点事务的一致性，并兼容MySQL/PostgreSQL协议和驱动使得应用迁移成本最低。Google Spanner是NewSQL的鼻祖——F1分布式关系数据库首次在全球范围多个数据中心部署——通过TrueTime API（由原子钟+GPS时钟同步提供全球有界时钟误差）实现外部一致性的分布式事务。开源的TiDB（PingCAP开发和维护）和CockroachDB是两大领先的开源NewSQL实现——两者均实现了基于Raft协议的副本同步和分布式事务的SI（快照隔离）/SSI（串行化快照隔离）。此外HTAP（Hybrid Transactional/Analytical Processing）融合是NewSQL新的发展方向——将事务型（OLTP）和分析型（OLAP）负载融合在同一系统中处理，TiDB的TiDB Server + TiKV + TiFlash分层解决OLTP和OLAP的混合。

## 关键结论

- NewSQL与传统RDBMS+分库分表中间件的本质区别：分库分表方案（如MyCAT/ShardingSphere）将表手动拆分到不同物理实例，应用需要处理分片路由、跨分片JOIN缺失、分布式事务靠XA等性能不理想。NewSQL对用户则呈现为一个单一完整的数据库实例——分片/副本/事务由数据库内核自动完成，可做跨节点JOIN和全SQL查询不需应用介入，是实现真正的"云原生分布式SQL数据库"
- Google Spanner的架构核心——TrueTime与外部一致性：传统的分布式事务通过锁+2PC保证可串行化但存在通信延迟高——Spanner利用全局原子时钟（TrueTime API保证时钟误差窗口始终在数个ms内），当读写执行过程中通过等待一个时钟误差窗口后读最新——利用Timestamps而非大量网络锁协商获得全球级别的线性一致读。这是业界最领先的一致性方案
- TiDB架构分层：(a) TiDB Server——无状态SQL解析+计划优化层，支持MySQL协议，负责接收客户端连接和查询路由；(b) TiKV——基于RocksDB的分布式键值存储引擎，将数据整理成Raft Group进行多副本一致同步；(c) PD（Placement Driver）—集群元数据管理、时间戳(Timestamp Oracle)分配和调度器自动分配/均衡Region在各TiKV节点的分布。这一计算存储分离的架构各层独立弹性伸缩
- CockroachDB的地理分区：支持把不同表或行范围绑定到具体的地区节点上——使某地域常用的数据就在本地副本，降低跨大陆延迟，而全局仍全维系的一致性。这使得全球化部署变得简单——数据"离家近"却仍然整体一致
- HTAP混合负载引擎的挑战：传统的OLTP行存友好写入/点查，OLAP列存适合聚合扫描——行存+列存之间有数据同步延迟，TiFlash同步TiKV的行存到列存储备——通过Raft learner无损同步使得延迟极小（毫秒级）——这可以让实时类面板和交易在不同引擎上同时读取到一致数据快照

## 易错点

1. **NewSQL不是NoSQL的竞争对手——而是重新连接SQL和分布式扩展**：NewSQL提供RDBMS级完整的事务(ACID)+全SQL兼容——NoSQL放弃这些换取水平扩展。NewSQL是为那些需要水平扩展但必须保留事务和SQL的业务设计的。

2. **"只需迁移连接串即可从MySQL切换到TiDB"不完全适用于生产**：虽然有MySQL协议的兼容性——但一些存储引擎差异（事务隔离级实现细节（TiDB使用SI需处理写冲突）、某些系统级函数缺失、外键支持不完整、执行计划差异、大事务的写冲突概率、热点的优化设计）——可能引入原生MySQL下不会出现的表现——迁移前必须测试。

3. **分布式事务比单机事务延迟高**：尽管NewSQL的跨节点事务比2PC快——但数据如果跨多个Region存——每个Raft共识通信至少涉及数个网络往返。与就地单库事务相比，跨节点写延迟数毫秒甚至更多——所以NewSQL并非对所有小项目更优——轻量应用单机数据库足矣。

4. **Raft Leader选址与延迟关系密切**：写入必须去Raft Leader——若应用的Topology未感知出每个Region的Leader所在地——写请求可能跨地域到Leader节点发生高延迟——学习Follower Reads机制和关闭跨region写可以尽量限制延迟。

## 例题

**例题1**：给出TiDB在处理跨行转账事务（A转100到B，不论A和B是否在同一Region）时分布式事务的实现方式，基于Percolator（TiDB的TXN模型基础）的2阶段提交步骤进行分析。

**解答**：Percolator采用两阶段——(a) Prewrite阶段：对于每一修改的行（A余额写; B余额写），在锁定该行写入一个预备写入锁和更新该键对应的最新版本；(b) 提交阶段：从PD获得T_commit时间戳——移锁并将各行标记为已提交。若任一节点Prewrite失败（锁冲突）——发起者事务回滚，清除所有已锁并返回失败。通过主键（第一个被更新的行）作为事务的Primary来协调其余Secondaries——避免全局2PC性能问题——这是Percolator的核心优化。

**例题2**：对比CockroachDB和MySQL主从复制架构下的灾备容错与全球部署的优缺。

**解答思路**：MySQL主从（异步或半同步）——主节点单一写入点且跨区域RTT高；若主库故障需人工切换或自动切换可能有数据丢失。CockroachDB多节点各自有Raft同步的本地数据副本——不存在单写入点——Raft共识自动故障切换且无数据丢失；支持Table-level地理分区——连接最近数据降低延迟。最后在数据恢复和一致保证上NewSQL架构在该场景具备天然优势。

## 代码示例

TiDB — SQL完全兼容MySQL协议—应用层不改代码：

```sql
-- 在TiDB中建表并插入数据（SQL同MySQL）
CREATE TABLE accounts (
    id BIGINT PRIMARY KEY AUTO_RANDOM,  -- TiDB特殊主键避免写热点
    user_name VARCHAR(100),
    balance DECIMAL(10,2)
);

-- 插入
INSERT INTO accounts (user_name, balance) VALUES ('Alice', 1000.00);
INSERT INTO accounts (user_name, balance) VALUES ('Bob', 500.00);

-- 转账事务（跨分片也能够执行ACID）
BEGIN;
UPDATE accounts SET balance = balance - 100 WHERE user_name = 'Alice';
UPDATE accounts SET balance = balance + 100 WHERE user_name = 'Bob';
COMMIT;

-- 分析查询（可能同时结合TiFlash列存加速）
SELECT user_name, SUM(balance) FROM accounts GROUP BY user_name;
```

Python使用SQLAlchemy操作TiDB（如同操作MySQL）：

```python
from sqlalchemy import create_engine, text

# 连接到TiDB——连接串与MySQL完全相同
engine = create_engine(
    "mysql+pymysql://root:@127.0.0.1:4000/test_db"
)
with engine.connect() as conn:
    result = conn.execute(text("SELECT user_name, balance FROM accounts"))
    for row in result:
        print(f"{row[0]}: {row[1]}")
```

CockroachDB的节点启动配置（命令行）：

```bash
# 启动一个本地三节点集群测试
cockroach start --insecure --store=node1 --listen-addr=localhost:26257 --http-addr=localhost:8080 --join=localhost:26257,localhost:26258,localhost:26259
cockroach start --insecure --store=node2 --listen-addr=localhost:26258 --http-addr=localhost:8081 --join=localhost:26257,localhost:26258,localhost:26259
cockroach start --insecure --store=node3 --listen-addr=localhost:26259 --http-addr=localhost:8082 --join=localhost:26257,localhost:26258,localhost:26259

# 初始化集群
cockroach init --insecure --host=localhost:26257

# 使用标准psql连接（CockroachDB兼容PostgreSQL协议）
psql "postgresql://root@localhost:26257/defaultdb?sslmode=disable"
```

## 关联页面

[[NoSQL概述]] [[CAP定理与BASE]] [[事务-ACID]] [[MVCC]]
