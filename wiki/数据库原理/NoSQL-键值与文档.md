---
title: NoSQL—键值存储与文档数据库
course: 数据库原理
chapter: NoSQL数据库
difficulty: INTERMEDIATE
tags: [NoSQL, 键值存储, 文档数据库, Redis, MongoDB, JSON, 哈希表]
aliases: [Key-Value Store, Document Database, Redis, MongoDB]
source:
  - 王珊《数据库系统概论》第5版
updated_at: 2026-05-02

---

## 核心定义

键值存储（Key-Value Store）和文档数据库（Document Database）是NoSQL数据库中最常用的两种类型，虽然都采用去关系化的数据模型，二者的设计目标和使用场景存在本质差异。键值存储是最简单的NoSQL模型——每个数据条目是一个键值对（Key→Value），数据库通过键（Key）的哈希定位快速读写值（Value），而值内部结构对数据库完全不透明——数据库不解析值的内容也不基于值内部属性提供索引或查询。键值存储提供的访问接口极其简练：GET/SET/DELETE/EXISTS，查询只能通过Key进行，无任何类WHERE句式。Redis、Amazon DynamoDB和Riak是代表性的键值存储系统。与之相对，文档数据库将记录存储为自描述的层次化结构化文档（通常为JSON/BSON/XML格式），数据库能解析文档内容并对其中的字段建立索引——允许通过嵌套的属性查询、过滤、聚合和排序文档。这类数据库在灵活Schema（每个文档可拥有不同的字段集）的同时保持了数据内部结构的可查询性。MongoDB、Couchbase、Elasticsearch（搜索引擎基线也是文档存储）是典型的文档数据库系统。键值和文档数据库都可以横向扩展分布数据，通过分片/分区来承载TB级别的大数据负载。

## 关键结论

- 键值存储的核心数据结构——全局哈希表：所有数据节点形成一个分布式哈希环（一致性哈希环），Key经过哈希函数映射到环上的一个虚拟节点，由该节点负责存储对应的键值对。当加入或移除节点时仅重分布受影响的Key范围（不是全量重哈希），实现了高效的弹性伸缩
- Redis的数据结构多样性：Redis不只是简单的Key→String的映射，它还提供了List（列表——用作简单队列/栈）、Set（集——标签去重）、Sorted Set（有序集——排行榜）、Hash（用于存对象子字段）、Bitmaps、HyperLogLog（近似基数）和Stream等丰富数据结构——这些结构都是基于Key定位后操作，赋予了键值模式更广的应用范围
- 文档数据库的索引与查询能力：MongoDB支持丰富的查询表达式和聚合管道（Aggregation Pipeline）——{ $match, $group, $sort, $project, $lookup}一系列阶段对文档处理，可媲美SQL的许多分析功能。但JOIN能力受限——$lookup（左外连接）仅一个文档连接，与关系型的多表关联有本质性能差距
- 文档更新的精读：MongoDB使用原子单文档操作（updateOne内对单文档的多个字段增/删/修改是原子性的），但不支持跨多文档事务的ACID（MongoDB从4.0版本起引入了多文档事务但性能代价大）。键值存储Redis用单线程串行执行命令从而天然原子化且避免了写冲突
- 文档模型中的嵌入 vs 引用对比：在关系模型中使用外键JOIN的表，通常在MongoDB可以通过"嵌入式文档（将相关的从记录直接嵌入父文档内）"实现单次IO读出全部数据（避免JOIN）。然而嵌入文档无法被其他文档引用回、重复嵌入会导致数据冗余——需权衡文档整体大小（16MB限制）和访问模式决定嵌入还是引用

## 易错点

1. **Redis当作数据库来存持久数据是危险的**：默认Redis将全部数据存在内存中做周期快照（RDB）和AOF增量写盘——两者不是实时性持久化——若机器掉电会丢失最近若干秒的修改。DynamoDB或RocksDB等持久化键值引擎是为持久化设计的正确选择。

2. **MongoDB不应该嵌入过深或无限增长的数组**：嵌入文档大小扩大导致I/O变大和文档迁移碎片化——单个文档最大16MB，不可预计会增长的元素（如订单的评论列表）宜分开集合用引用——而非全部嵌入。

3. **"文档数据库没有Schema"不代表不需数据治理**：虽然没有数据库级约束检查——但应用代码通常仍旧要求某个"隐含Schema"（字段的存在和类型）正确运行。需要一个应用层验证防范不合格数据进入存储造成查询失败和业务逻辑异常。

4. **Redis的Key设计对性能影响巨大**：所有数据只由Key检索——若Key的命名方案不经过规划（例如将相同前缀的上百万Key全部分布在一个DB实例中）可能导致键空间扫描变慢或大量Key淘汰策略不适合。设计好命名空间和分配是关键。

## 例题

**例题1**：用户画像存储——每个用户有uid、name、tags（字符串数组）、last_login、preferences（嵌套对象）。对比Redis与MongoDB的存储和查询用户的方式。

**解答**：
- Redis方案：用Hash结构存储——HSET user:{uid} name "张三" tags "[python,java]" preferences "{theme:dark...}"
  可O(1)取某用户全量，但查询"所有tags含python的用户"需遍历全部用户Hash——做不到。
- MongoDB方案：db.users.insertOne({uid:1, name:"张三", tags:["python","java"], last_login: ISODate("..."), preferences:{theme:"dark"}}); db.users.createIndex({tags:1})——查询tags含python的用户非常简单：db.users.find({tags:"python"}) 利用索引快速检索。所以此场景适合文档模型。

**例题2**：Redis如何实现一个简单的访问频率限流（速率限制）——"每用户每分钟最多10次请求"。

**解答思路**：用Key = rate_limit:{user_id}:{minute_timestamp}，值为计数器，INCR之后设置TTL让Key在该分钟后自动过期——每次请求=>INCR这个Key→检查返回值是否小于等于10→否的话拒绝请求。利用Redis的原子INCR和有效期TTL形成无锁计数器。

## 代码示例

MongoDB文档查询（Mongo Shell / Node.js Driver）：

```javascript
// 插入文档
db.products.insertMany([
   { _id: 1, item: "apple", price: 1.5, tags: ["fruit"], stock: 100 },
   { _id: 2, item: "banana", price: 0.8, tags: ["fruit","yellow"], stock: 50 },
   { _id: 3, item: "cucumber", price: 1.2, tags: ["vegetable"], stock: 0 }
]);

// 创建复合索引
db.products.createIndex({ price: 1, stock: -1 });

// 聚合管道：计算每种标签的平均价格
db.products.aggregate([
   { $unwind: "$tags" },
   { $group: { _id: "$tags", avgPrice: { $avg: "$price" } } },
   { $sort: { avgPrice: -1 } }
]);
```

Redis速率限制示例（Python）：

```python
import redis, time

r = redis.Redis(host='localhost', port=6379, decode_responses=True)

def is_rate_limited(user_id: str, max_req: int = 10, window: int = 60) -> bool:
    minute_key = f"rate:{user_id}:{int(time.time() // window)}"
    current = r.incr(minute_key)
    if current == 1:
        r.expire(minute_key, window)  # 首次设置过期时间
    return current > max_req

# 调用
if is_rate_limited("user_1001"):
    print("请求过于频繁，请稍后再试")
```

## 关联页面

[[NoSQL概述]] [[NoSQL-列族与图]] [[CAP定理与BASE]] [[NewSQL]]
