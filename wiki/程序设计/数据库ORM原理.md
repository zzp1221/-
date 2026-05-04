---
title: "ORM框架原理与ActiveRecord"
course: 程序设计
chapter: 数据库编程
difficulty: INTERMEDIATE
tags: [ORM, ActiveRecord, 数据库映射, SQLAlchemy]
aliases: [Object-Relational Mapping]
source: "Martin Fowler PoEAA; SQLAlchemy文档; Hibernate/JPA文档"
updated_at: 2026-05-02
---

## 核心定义

ORM(对象关系映射)在面向对象模型和关系数据库之间架桥。模式：ActiveRecord——每个实体类映射一张表，自身包含CRUD操作(Rails/Django ORM)。DataMapper——实体和持久化分离，映射器负责同步(SQLAlchemy Core/Hibernate)。核心问题(对象-关系阻抗失配)：继承映射(单表继承/类表继承/具体表继承)、关联映射(一对一/一对多/多对多)、延迟加载(Lazy Loading → N+1查询问题)→用eager loading(JPA join fetch/SQLAlchemy joinedload)解决。

## 关键结论

1. ORM让95%的查询更方便但5%复杂查询仍需要SQL 2. Unit of Work模式跟踪变更集中flush 3. Identity Map保证同一session内同一行对应同一对象 4. 数据库迁移管理(Alembic/Flyway)是ORM配套的必要组件

## 关联页面

[[数据库索引设计]] [[SQL执行计划分析]] [[微服务架构设计]]
