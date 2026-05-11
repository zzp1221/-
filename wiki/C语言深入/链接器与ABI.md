---
title: "C语言-链接器与ABI详解"
course: C语言深入
chapter: 编译与链接
difficulty: ADVANCED
tags: [C语言, 链接器, ABI, ELF, 符号表, 动态链接]
aliases: [Linker, ABI, ELF, Dynamic Linking]
source: "ELF Specification (System V ABI); Levine《Linkers and Loaders》"
updated_at: 2026-05-02
---

## 核心定义

链接器将多个目标文件(.o)合并为可执行文件或共享库。主要任务：1.)符号解析(symbol resolution) 2.)重定位(relocation)。ABI(应用二进制接口)定义了：类型大小与对齐、调用约定(calling convention)、name mangling、异常处理和栈展开规则。

## ELF格式

ELF(Executable and Linkable Format)是Linux/Unix的标准二进制格式。.text节存放代码，.data存放已初始化全局变量，.bss存放未初始化全局变量(零填充)，.rodata存放只读数据。PLT(Procedure Linkage Table)和GOT(Global Offset Table)实现延迟绑定动态链接。

## 动态链接过程

1.)execve加载ELF→2.)动态链接器ld.so映射依赖库→3.)执行重定位(RELOC/GLOB_DAT/JUMP_SLOT)→4.)执行.init段→5.)调用main()。RTLD_LAZY(使用时解析)优于RTLD_NOW(加载时全部解析)但可能触发运行时错误。

## 关联知识点

[[C语言-静态库与动态库构建]] [[C语言-预处理器宏与条件编译]]
