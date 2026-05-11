---
title: "Python深入-数据类与attrs对比"
course: Python深入
chapter: 数据建模
difficulty: BASIC
tags: [Python, dataclass, attrs, 数据建模, PEP 557]
aliases: [Python dataclass, attrs library, Data Class]
source: "PEP 557 (Data Classes); Python docs: dataclasses; attrs documentation (https://www.attrs.org); PEP 681 (dataclass_transform)"
updated_at: 2026-05-02
---

## 核心定义

@dataclass装饰器(Python 3.7+)自动生成__init__/__repr__/__eq__/__hash__等方法，减少样板代码。字段通过类型注解声明：@dataclass class Point: x: int; y: int = 0。field()函数定制字段：default/default_factory(默认值)、init/repr/compare/hash(参与哪些方法)、metadata(元信息字典)。attrs是第三方库(2015年至今)，提供attr.s()/attr.ib()等价功能，但附加更丰富的验证器、转换器、冻结(frozen)等特性。两者都支持__slots__优化(Python 3.10+的dataclass slotted=True)。PEP 681引入dataclass_transform，允许attrs/Pydantic等库声明自身模仿dataclass行为，让mypy能理解。

## 关键结论

1.dataclass的__post_init__进行后处理验证(字段就绪后执行) 2.frozen=True使用__setattr__重载阻止修改(不可变实例) 3.attrs的validator支持多种内建校验(instance_of/lt/gt/in_)和自定义可调用对象；支持converter管道(输入值自动转换) 4.Pydantic BaseModel提供运行时类型验证+JSON序列化，区别在于Pydantic验证输入数据而dataclass信任源码 5.field(init=False)创建非初始化字段(如从其他字段计算) 6.Inheritance: dataclass子类继承父类字段(子类字段在__init__中放在父类字段之后) 7.Ordering: 设置order=True自动生成__lt__/__le__/__gt__/__ge__比较方法(按字段定义顺序)

## 关联知识点

[[Python深入-类型注解与mypy]] [[Python深入-描述符协议]] [[Python深入-CPython对象模型]]
