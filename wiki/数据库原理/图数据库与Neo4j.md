---
title: 图数据库与Neo4j
course: 数据库原理
chapter: NoSQL数据库
difficulty: INTERMEDIATE
tags: [数据库, 图数据库, Neo4j, 属性图, Cypher]
aliases: [Graph Database, Neo4j, 图查询]
source:
  - Neo4j官方文档
  - 《图数据库》(Ian Robinson等)
  - Apache TinkerPop/Gremlin规范
updated_at: 2026-05-03
---

## 核心定义

图数据库以图论为理论基础，使用节点（Node）、关系（Relationship/Edge）和属性（Property）来存储和查询数据。与关系数据库不同，图数据库的查询性能与数据总量无关，只与遍历的子图大小成正比，特别适合处理高度关联数据。属性图模型（Property Graph Model）是最主流的图数据模型：节点和关系都可以有属性，关系有方向和类型。主流图数据库：Neo4j（最流行的属性图数据库，使用Cypher查询语言）、Amazon Neptune（支持Gremlin和SPARQL）、JanusGraph（开源分布式图数据库）。图查询语言：Cypher（Neo4j首创，声明式）、Gremlin（Apache TinkerPop，命令式）、SPARQL（W3C标准，RDF图）。图数据库的存储引擎通常采用邻接表结构：每个节点存储其所有关系的指针，遍历操作是O(1)的指针跳转，不需要像关系数据库那样做JOIN。典型应用场景：社交网络、推荐系统、知识图谱、欺诈检测、路径规划。

## 关键结论

- 图数据库在多跳关联查询（如"朋友的朋友的朋友"）上比关系数据库快数个数量级
- Neo4j使用原生图存储（index-free adjacency），每个节点直接指向相邻节点，不需要全局索引
- Cypher语法直观：`MATCH (a:Person)-[:FRIEND]->(b:Person)-[:FRIEND]->(c:Person) WHERE a.name='张三' RETURN c`
- 图数据库不适合大量聚合分析（OLAP），适合关系遍历和模式匹配
- 知识图谱是图数据库的重要应用，RDF三元组(主语-谓语-宾语)是W3C标准的图数据模型

## 易错点

1. 图数据库不是万能的：对于简单的CRUD操作，关系数据库更高效；图数据库的优势在关联查询
2. 关系数据库存储图数据需要多对多关系表和递归CTE查询，性能随跳数指数下降
3. Neo4j Community Edition是单机免费版，Enterprise Edition才支持集群和因果一致性

## 例题

**例1：** 社交网络中有1000万用户，平均每人200个好友。查询"张三的3度好友"（朋友的朋友的朋友），对比关系数据库和图数据库的性能。

**解答：** 关系数据库：需要3次自JOIN（user表×friend表×3），假设使用索引，每次JOIN扫描约200条，总扫描200×200×200=800万条记录，加上去重和JOIN开销，可能需要数秒。图数据库：从张三节点出发，沿着FRIEND关系遍历3跳，原生图存储下每跳是O(1)指针跳转。第1跳200人，第2跳约200×200=4万人（去重后），第3跳约200×200×200=800万人（去重后）。图数据库的遍历操作是纯指针跳转，不需要全局扫描，通常在毫秒级完成。

## 关联页面

[[NoSQL概述]] [[NoSQL-键值与文档]] [[关系模型]]
