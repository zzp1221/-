---
title: "分布式事务与两阶段提交（2PC）"
course: 数据库原理
chapter: 分布式数据库
difficulty: ADVANCED
tags: [数据库, 分布式事务, 2PC, 3PC, XA]
aliases: [Two-Phase Commit, XA]
source: "Distributed Systems (van Steen & Tanenbaum); XA规范; MySQL XA文档"
updated_at: 2026-05-02
---

## 核心定义

2PC(两阶段提交)实现跨多个数据库的原子提交。协调者(Coordinator)管理事务。阶段1(Prepare)：协调者向所有参与者发送准备请求，参与者执行事务但不提交，记录REDO/UNDO日志后回复Yes/No。阶段2(Commit/Abort)：若全部Yes则协调者发Commit，否则发Abort。3PC增加预提交阶段减少阻塞概率。XA是2PC的开放标准，RDBMS通过XA接口支持。

## 关键结论

1. 2PC是阻塞协议——协调者崩溃导致参与者锁资源悬挂 2. 实际场景中2PC性能开销大（多轮网络+日志刷盘）3. 业务层通过补偿事务(Saga)替代2PC是趋势 4. Seata的AT模式实现了应用层2PC

## 关联页面

[[事务ACID特性]] [[分布式一致性协议]] [[CAP与BASE理论]]
