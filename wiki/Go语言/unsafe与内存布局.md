---
title: "Go语言-unsafe与内存布局"
course: Go语言
chapter: 系统编程
difficulty: ADVANCED
tags: [Go语言, unsafe, 内存布局, 指针, cgo]
aliases: [Go unsafe, Memory Layout, unsafe.Pointer]
source: "Go官方文档 unsafe包; Go Spec: unsafe.Pointer; Go Blog: unsafe.Pointer rules"
updated_at: 2026-05-02
---

## 核心定义

""unsafe.Pointer是通用指针类型，可与其他任意指针类型互转(类似于C的void*)。unsafe.Sizeof(x)返回变量x占用的字节数(不含其引用数据),unsafe.Offsetof(f)返回结构体字段f距结构体开头的偏移量,unsafe.Alignof(x)返回对齐要求。unsafe.Pointer的四条合法规则：T1→unsafe.Pointer→T2转换(仅T1和T2内存布局兼容时安全)；unsafe.Pointer→uintptr(用于打印/调试)。

## 内存布局详解

""Go结构体内存布局遵循对齐规则：每个字段的偏移量必须是其对齐大小的倍数，结构体整体大小必须是最大对齐的倍数。空struct{}大小为0(zero-width type)，常作为map的value用于实现set(map[T]struct{})。slice、string、interface、map、channel的底层结构都是header+pointer组合。unsafe.Sizeof(string)在64位系统为16字节(data ptr + len)。

## 关键结论

""1. uintptr不被GC追踪——保存uintptr期间若原对象不再被引用可能导致悬挂指针 2. 严禁对Go托管内存进行指针算术 3. cgo调用会将Go指针传给C需要特殊处理(Go 1.6引入的cgocheck机制) 4. reflect.SliceHeader/StringHeader是unsafe的reflect版等价物

## 关联知识点

""[[Go语言-Slice内部实现]] [[Go语言-String与[]byte转换]] [[Go语言-cgo与FFI]]
