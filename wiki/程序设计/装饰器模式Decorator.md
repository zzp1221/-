---
title: "设计模式-装饰器模式（Decorator）"
course: 程序设计
chapter: 设计模式
difficulty: INTERMEDIATE
tags: [设计模式, 装饰器, 结构型, GoF, Decorator]
aliases: [Decorator Pattern]
source: "Design Patterns: Elements of Reusable OO Software (GoF)"
updated_at: 2026-05-02
---

## 核心定义

装饰器模式动态地给对象添加职责，比继承更灵活。角色：Component(接口)、ConcreteComponent(原始对象)、Decorator(抽象装饰器持有Component引用)、ConcreteDecorator。Java I/O流是典型应用：new BufferedReader(new InputStreamReader(new FileInputStream(path)))。Python的@装饰器是语法糖。

## 关联页面

[[设计模式概述]] [[SOLID设计原则]]
