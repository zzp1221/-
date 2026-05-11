---
title: "领域事件与EventStorming"
course: 软件工程
chapter: 领域驱动设计
difficulty: INTERMEDIATE
tags: [软件工程, EventStorming, 领域事件, DDD]
aliases: [EventStorming, Domain Events, DDD]
source: "Brandolini 2009 (EventStorming); Evans《Domain-Driven Design》; Vernon《Implementing DDD》"
updated_at: 2026-05-02
---

## 核心定义

EventStorming是一种协作式领域建模工作坊，由Alberto Brandolini创建。核心概念：在大型墙面上用不同颜色的便签贴代表领域事件(变化已发生的记录,橙色)、命令(触发行为的动作,蓝色)、聚合(一致性边界内的事件处理单元,黄色)、外部系统(红色)、政策/策略(policy——何时触发,紫色)、读取模型(read model,绿色)。时间轴从左到右展开——业务专家和开发者共同描述整个业务流程(不区别角色)。EventStorming代替传统的需求文档讨论——加速共识形成。

## 在实现中的体现

在实现中Domain Event转化为event-driven architecture的核心。Event是已发生的不可撤销的事实(通常使用过去式动词命名——'OrderPlaced'而非'PlaceOrder')。CQRS(Command Query Responsibility Segregation)配合事件：将写模型(聚合)和读模型(投影/projection)分离——写端发布事件,读端处理并更新查询优化模型。Event Sourcing将聚合的状态存储为事件序列而非当前状态快照(事件流回放重构当前状态——提供完整的审计日志和时间旅行调试)。

## 关键结论

1. EventStorming的产出是一张可视化全景图(所有参会者理解一致) 2. Domain Events一经发布不可修改(append-only) 3. Event Sourcing解决了状态变化的审计问题但增加了系统复杂性(read/eventual consistency/replay性能) 4. Bounded Context边界的划分通常基于领域专家语言(统一语言UBiquitous Language)的一致性 5. EventStorming可以作为敏捷团队做需求发现的常规实践(Kick-off每sprint/feature)

## 关联知识点

[[软件工程-微服务架构]] [[软件工程-契约式设计DbC]] [[分布式系统-事件驱动架构]]
