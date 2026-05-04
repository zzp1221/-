---
title: "测试驱动开发（TDD）"
course: 软件工程
chapter: 软件测试
difficulty: INTERMEDIATE
tags: [软件工程, TDD, 测试, 敏捷, 重构]
aliases: [Test-Driven Development]
source: "Test-Driven Development: By Example (Beck 2002)"
updated_at: 2026-05-02
---

## 核心定义

TDD红绿重构循环：Red→写一个失败测试(定义期望行为)→Green→写最少代码让测试通过(不必优雅)→Refactor→重构代码消除重复/改善设计(测试仍通过)。三个法则：1.不允许写任何产品代码除非它让失败的测试通过 2.不允许写超过一个失败测试 3.不允许写超过刚好让测试通过的产品代码。

## 关键结论

1. TDD使代码天然可测试(低耦合、依赖注入) 2. 测试即文档(测试描述行为规范) 3. 回归测试套件是重构的安全网 4. TDD不适合探索性编程(UI布局/原型)

## 关联页面

[[敏捷Scrum与Kanban]] [[软件测试-单元与集成测试]] [[重构技术]]
