---
title: "Python深入-类型注解与静态检查"
course: Python深入
chapter: 类型系统
difficulty: INTERMEDIATE
tags: [Python, 类型注解, mypy, static checking, PEP 484, Protocol]
aliases: [Python Type Hints, mypy, Static Type Checking]
source: "PEP 484 (Type Hints); PEP 526 (Variable Annotations); PEP 604 (X|Y Union); PEP 544 (Protocols); mypy docs"
updated_at: 2026-05-02
---

## 核心定义

PEP 484引入类型提示(Type Hints): def greet(name: str, times: int = 1) -> str: ...。运行时类型提示存储在__annotations__字典中(可通过typing.get_type_hints解析字符串前向引用)。Python本身不做类型检查——mypy/pyright/pytype等静态检查工具在编译期验证类型一致性。PEP 526引入变量注解x: int = 5。PEP 604引入X|Y联合类型(Python 3.10+)，语法更简洁。PEP 544定义Protocol(结构化子类型)：类不需要显式继承协议，只要实现所需方法即视为满足协议(类似Go interface的duck typing)。typing模块提供: List[T], Dict[K,V], Optional[T], Callable[...], TypeVar用于泛型。

## 关键结论

1.类型提示不提升运行时性能——mypy完全是离线检查工具 2.Literal['small','medium','large']可限制字符串枚举(PEP 586, Python 3.8+) 3.TypedDict用于表示固定键名的字典(类似JSON schema) 4.overload装饰器让mypy理解同一函数的不同类型签名组合 5.Protocol的主要场景：函数参数要求'类文件对象'(有read/write方法)，不强制继承特定基类 6.Final装饰器标记不可重写的类/方法/变量；@final标记不可继承的类 7.pydantic/dataclasses-json利用运行时注解做数据验证和序列化 8.mypy支持增量类型检查(.mypy_cache/)使大型项目检查保持在秒级

## 关联知识点

[[Python深入-dataclass与attrs]] [[TypeScript-类型系统]] [[Go语言-接口与类型系统]]
