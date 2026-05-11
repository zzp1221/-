---
title: "Go语言-Slice内部实现"
course: Go语言
chapter: 数据结构
difficulty: INTERMEDIATE
tags: [Go语言, slice, 内存管理, append, slice header]
aliases: [Go Slice Internals, Slice Header, Append Mechanics]
source: "Go Blog: Go Slices: usage and internals; Go runtime源码 slice.go; Effective Go"
updated_at: 2026-05-02
---

## 核心定义

""Go的Slice是动态数组的抽象，底层由3字段的header结构表示：type slice struct { array unsafe.Pointer; len int; cap int }。Slice不拥有底层数组(底层数组可能被多个slice共享)。make([]T, len, cap)创建一个新切片和底层数组。切片操作s[i:j]截取底层数组的一段，新slice与原slice共享同一底层数组。len=s[j]-s[i], cap=从i到原切片末尾。

## Append扩容机制

""append(s, x...)向slice追加元素。如果cap足够则直接在底层数组后添加(原地); cap不足时分配新底层数组(通常翻倍扩容)，复制原数据，添加新元素。Go 1.18后扩容策略更平滑：小于256时翻倍，大于256时以(1.63-2.0)之间逐步过渡。扩容后原slice的底层数组不变(可能成为垃圾)，新slice指向新数组。append始终返回新header值(即使原地也可能改变len)。

## 关键结论

""1. 函数传递slice只复制header(24字节),修改元素影响原slice 2. append可能导致底层数组分离——不要同时依赖新旧slice 3. 多slice共享底层数组时修改需小心 4. copy()可避免共享底层数组 5. full slice expression s[a:b:c]控制cap

## 关联知识点

""[[Go语言-Map内部实现]] [[Go语言-String与[]byte转换]] [[Go语言-unsafe与内存布局]]
