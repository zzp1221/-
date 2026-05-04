---
title: "领域驱动设计（DDD）核心"
course: 软件工程
chapter: 软件设计
difficulty: ADVANCED
tags: [软件工程, DDD, 领域驱动, 设计]
aliases: [Domain-Driven Design]
source: "Domain-Driven Design (Evans 2003); Implementing DDD (Vernon)"
updated_at: 2026-05-02
---

## 核心定义

DDD将复杂业务逻辑建模为领域模型。战略设计：限界上下文(Bounded Context)——每个上下文有独立的语言和模型；上下文映射(Context Map)——各上下文间的关系。战术设计：实体(Entity)——身份标识不变(用ID比较)；值对象(Value Object)——通过属性值比较(不可变)；聚合(Aggregate)——一致性边界(根实体为入口)；领域事件(Domain Event)——已发生的重要业务事实。通用语言(Ubiquitous Language)：团队共用同一套术语。

## 关键结论

1. DDD的核心是将复杂业务逻辑映射到合理的代码结构 2. 限界上下文是微服务拆分的天然指导 3. CQRS(命令查询职责分离)+Event Sourcing常与DDD配合

## 关联页面

[[微服务架构设计]] [[SOLID设计原则]] [[面向对象设计]]
