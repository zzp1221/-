---
title: NoSQL—列族存储与图数据库
course: 数据库原理
chapter: NoSQL数据库
difficulty: INTERMEDIATE
tags: [NoSQL, 列族存储, 图数据库, HBase, Cassandra, Neo4j, 社交网络]
aliases: [Wide-Column Store, Column-Family Database, Graph Database, HBase, Cassandra, Neo4j]
source:
  - 王珊《数据库系统概论》第5版
updated_at: 2026-05-02

---

## 核心定义

列族存储（Wide-Column Store / Column-Family Database）和图数据库（Graph Database）是NoSQL家族中两种面向特定数据访问模式的数据库类型。列族存储将数据按行键（Row Key）组织，每行可以有动态的列族（Column Family），每个列族下包含任意数量的列（Column）——列是在插入时动态定义的，不同行可以有完全不同的列集合（Sparse Matrix特性）。列族存储借鉴了Google Bigtable的架构，适用于海量数据按时间排序顺序扫描（时间序列）、日志存储、内容管理和搜索引擎倒排索引等场景。代表性系统：Apache HBase（Hadoop生态的标准Bigtable实现——强一致性+自动分区）、Apache Cassandra（去中心化架构无单点故障+最终一致性——基于Dynamo论文）、ScyllaDB。图数据库专为处理高度关联的数据（社交关系、知识图谱、推荐引擎、欺诈检测）设计——以节点（Vertex/Node）代表实体、边（Edge/Relationship）代表实体间的关系，节点和边都可携带属性（Property）。图数据库提供专门的图遍历查询语言（Cypher/SPARQL/Gremlin），能够在大型图中通过索引搜索算法（如Neo4j的索引自由邻接）在常量邻接O(1)时间内完成邻居遍历——这是深度关联查询在关系型数据库中所不可能匹配的（多表JOIN递归在RDBMS中大图场景下性能崩溃）。

## 关键结论

- 列族存储的物理设计（LSM Tree与SSTable）：HBase底层采用LSM-Tree（Log-Structured Merge Tree）——写入先进入内存MemStore到达阈值后以有序SSTable文件刷写到HDFS——后台定期合并多个SSTable。优点：写入顺序、无随机IO开销，读取合并多个有序文件。Cassandra也使用类似LSM机制——满足极高的写吞吐量
- 列族数据模型的分层：Keyspace（类似"数据库模式"）→ Table（ColumnFamily）→ Row（RowKey）→ ColumnFamily → Column Qualifier:Value:Timestamp（三元组）。查询方式通过行键精确检索或行键范围扫描（Scan）——一般不在列Qualifier上跨行做全表条件过滤（避免COW-wide scan）。数据按行键排序——所以行键设计至关重要（热点倾斜行键导致某分区过热）
- 图数据库的邻接无索引遍历：Neo4j将边直接存储于节点对象的内存和磁盘结构上——查找某节点的全部关系只需在内置的邻接列表上进行O(1)遍历（无需全局索引查找）——这使图遍历（如查询"用户A的朋友的朋友中哪些购买了产品P"这种6度传播链）在大图下比传统索引RDBMS快好几个数量级
- 图查询语言Cypher模式匹配：MATCH (u:User)-[:FRIEND*2..3]->(f:User)-[:BOUGHT]->(p:Product) RETURN f.name, p.name——利用图模式的多跳遍历语法直接在图上递归解析关联路径——SQL需递归CTE多次JOIN才能做到，但性能和可读性远不及此
- Cassandra的读/写协商与一致性级别（Consistency Level）：通过设置W（写入必须该级别数的节点确认）和R（读取必须在多少节点上确认），可以调节一致性和响应的权衡。W+R > 副本数 → 可以获得强一致的保证（Quorum）。这种"可调一致性"是列族DB具备的有别于传统关系型的大灵活性

## 易错点

1. **列族存储不是"列式存储（Columnar Store）"**：列族宽表存储仍是行键定位一行中的所有列族，底层写的一行可能稀疏。列式存储（如ClickHouse、Vertica）按列的数据而非按行键来组织——是用于分析OLAP场景。这是两个独立概念不宜混淆。

2. **图数据库的设计起始要使用高连通度的数据**：图数据库不在于将关系型表简单地转化为图节点（因为大量查询并不需要图的多跳），如果应用并非深度图的连接分析——使用图数据库反而增加了学习的维护开销。选择任何类型数据库的准则就是根据自身数据问的问题。

3. **HBase的Region热Split问题**：按Row Key升序单调插入（如时间戳）会导致所有写操作全部针对同一Region Server——这不仅造成热点并且丧失了分布式优势——通过反哈希前缀/Salt/dd-mm-yyyy倒序的RowKey来散开写入是列族存储的基本技巧。

4. **图库中不需要对边的属性做"强一致性"保证**：图引擎的首要目标是为复杂的图分析做高效查询——对一些图DB去中心化的同步机制而言，同时对边的实时改写如极端并发时要加上应用层乐观锁或选支持ACID图的Neo4j（企业版）才能一致。

## 例题

**例题1**：说明Cassandra为何适用于IoT传感器数据的时序存储，给出最终的最佳实践设计TTL和行键构成的策略。

**解答**：IoT数据是大量传感器连续产生时序记录（每传感器定期报告温度/湿度）——写入速率极高、传感器ID固定、频繁时间范围扫描。Cassandra优点：(1)LSM树适合大量顺序写入；(2)行键按(sensor_id, day)复合——相同传感器的不同天划分在不同物理行而每天内的列逻辑相邻（满足时间范围扫描）；(3)TTL可使数据旧的过了N天自动删除节省空间；(4)无单点故障+多DC复制——适用于多地传感器场。行键：sensor_id:day避免该传感器持续写入热点（因为每天一个新RowKey）。

**例题2**：利用Neo4j Cypher 查询算法解决简单的"推荐好友可能认识的人"功能——基于共同好友数。

**解答思路**：
```cypher
MATCH (u:User {name:'Alice'})-[:FRIEND]->(f:User)-[:FRIEND]->(foaf:User)
WHERE NOT (u)-[:FRIEND]-(foaf) AND u <> foaf
RETURN foaf.name, COUNT(*) AS commonFriends
ORDER BY commonFriends DESC LIMIT 10
```
该查询遍历节点Alice的一度朋友→二度朋友（非自身且不与Alice直接朋友关系）统计不同的共同好友计数×即可定推荐排名——图库天然递归跳和多跳查询的高效。

## 代码示例

Cassandra CQL建表/插入（IoT传感器数据）：

```sql
CREATE KEYSPACE iot_data WITH replication = {
    'class': 'NetworkTopologyStrategy',
    'datacenter1': 3
};

CREATE TABLE iot_data.sensor_readings (
    sensor_id TEXT,
    day TEXT,
    event_time TIMESTAMP,
    temperature FLOAT,
    humidity FLOAT,
    PRIMARY KEY ((sensor_id, day), event_time)
) WITH CLUSTERING ORDER BY (event_time DESC)
   AND default_time_to_live = 864000; -- 10天后过期

INSERT INTO iot_data.sensor_readings(sensor_id, day, event_time, temperature, humidity)
VALUES ('sensor_001', '2026-05-01', '2026-05-01T10:00:00Z', 22.5, 65.0);
```

Neo4j 社交图创建与查询（Cypher）：

```cypher
CREATE
  (alice:User {name:'Alice', age:30}),
  (bob:User {name:'Bob', age:25}),
  (charlie:User {name:'Charlie', age:35}),
  (alice)-[:FRIEND {since:2020}]->(bob),
  (bob)-[:FRIEND {since:2021}]->(charlie),
  (charlie)-[:FRIEND {since:2022}]->(alice);

-- 查询Alice→所有朋友→朋友的年龄
MATCH (alice:User {name:'Alice'})-[:FRIEND]->(friend)
RETURN friend.name, friend.age;
```

## 关联页面

[[NoSQL概述]] [[NoSQL-键值与文档]] [[CAP定理与BASE]] [[NewSQL]]
