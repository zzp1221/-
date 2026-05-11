---
title: "Go语言-cgo与FFI"
course: Go语言
chapter: 系统编程
difficulty: ADVANCED
tags: [Go语言, cgo, FFI, CGO_ENABLED, 外部函数接口]
aliases: [Go cgo, Foreign Function Interface, CGo]
source: "Go官方文档 cmd/cgo; Go Blog: C? Go? Cgo!; Go Wiki: cgo"
updated_at: 2026-05-02
---

## 核心定义

""cgo是Go的C语言互操作机制。通过在Go文件顶部import 'C'(必须紧随特殊注释块中的C代码)，可以在Go中调用C函数和使用C类型。CGo将Go+C代码分开编译处理：Go编译为Go目标文件，C编译为C目标文件，最后链接。调用C函数有明显开销：每调用约40ns vs 直接Go调用~1ns(goroutine切换和栈切换)。

## 内存管理与性能

""cgo调用不可在goroutine间任意迁移(锁定OS线程)。C.malloc分配的内存不受Go GC管理，必须用C.free手动释放。C.CString将Go字符串复制到C堆(需手动free)。Go 1.6+的指针传递规则：不能将Go指针(含引用的Go内存)存储到C内存中超过一次调用(cgocheck检测)。大量cgo调用可设置runtime.LockOSThread()绑定goroutine到特定OS线程。

## 关键结论

""1. cgo是工具不是包——CGO_ENABLED=0可禁用 2. CGo不是Go对象链接格式，导致编译慢、交叉编译困难 3. 考虑用纯Go替代方案(golang.org/x/sys替代cgo syscall) 4. 批量cgo调用可减少开销 5. CGo代码通常性能显著低于纯Go实现

## 关联知识点

""[[Go语言-unsafe与内存布局]] [[C语言深入-链接器与ABI详解]] [[Rust语言-FFI与unsafe Rust]]
