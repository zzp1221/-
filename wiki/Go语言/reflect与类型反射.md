---
title: "Go语言-reflect与类型反射"
course: Go语言
chapter: 元编程
difficulty: INTERMEDIATE
tags: [Go语言, reflect, 反射, struct tags, 元编程]
aliases: [Go Reflection, reflect.Type, reflect.Value]
source: "Go官方文档 reflect包; Go Blog: The Laws of Reflection; Effective Go"
updated_at: 2026-05-02
---

## 核心定义

""reflect包提供运行时类型检查(reflection)。reflect.Type(接口)表示Go类型的元信息，通过reflect.TypeOf(x)获取。reflect.Value表示值的运行时表示，可获取、设置、调用。reflect.Type和reflect.Value都区分Kind(基础类别int/struct/ptr/...)和具体类型名。reflect.Indirect(v)获取指针指向的值，reflect.New(typ)分配新零值并返回指针。

## Struct Tag与JSON映射

""Go的结构体标签(struct tags)通过reflect.StructTag获取。标签格式：`key1:"value1" key2:"value2"`。encoding/json、gorm等库通过反射读取标签实现序列化映射、ORM映射。Tag.Get(key)按key查找值。反射的基本定律：1. 从接口值可得反射对象 2. 从反射对象可得接口值 3. 要修改反射对象其值必须可设置(Settable)。

## 关键结论

""1. 反射比直接访问慢10~100倍 2. 反射代码更脆弱，编译期检查丧失 3. Value.IsValid()/IsZero()需要先检查 4. 调用Call时方法签名必须完全匹配 5. 大量使用reflect的代码应抽象为代码生成工具替代 6. 不要对未导出的字段进行Set操作——会panic

## 关联知识点

""[[Go语言-接口与类型系统]] [[Go语言-泛型与类型约束]] [[Java深入-反射与动态代理]]
