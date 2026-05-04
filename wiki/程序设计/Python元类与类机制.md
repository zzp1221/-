---
title: "Python元类与类机制"
course: 程序设计
chapter: Python
difficulty: ADVANCED
tags: [Python, 元类, metaclass, 描述符]
aliases: [Python Metaclasses]
source: "Python Language Reference; Fluent Python (Ramalho); Python Cookbook"
updated_at: 2026-05-02
---

## 核心定义

一切都是对象——包括类本身。类是type的实例。元类是创建类的类。class创建流程：1.解析类体得到namespace字典 2.调用metaclass(name, bases, namespace)→得到类对象。type(name, bases, dict)是默认元类。__new__(cls,...)创建实例，__init__初始化。描述符协议：实现__get__/__set__/__delete__的对象控制属性访问，property/@classmethod/@staticmethod都是描述符。

## 关键结论

1. 元类的典型应用：ORM(Django/SQLAlchemy)、接口注册、单例 2. class decorator比metaclass更简单(先考虑decorator) 3. MRO方法解析顺序由C3线性化算法确定

## 关联页面

[[Python垃圾回收机制]] [[Python GIL与并发]]
