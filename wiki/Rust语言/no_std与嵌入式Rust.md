---
title: "Rust语言-no_std与嵌入式Rust"
course: Rust语言
chapter: 嵌入式开发
difficulty: ADVANCED
tags: [Rust, no_std, 嵌入式, PAC, HAL, bare metal]
aliases: [Rust Embedded, no_std, PAC/HAL Pattern]
source: "The Embedded Rust Book; Rust Reference: #![no_std]; Rust Embedded Working Group"
updated_at: 2026-05-02
---

## 核心定义

""#![no_std]属性移除标准库依赖(操作系统抽象的集合)，仅保留core库(语言特性的最小子集)。core提供：基础类型(Option/Result/Iterator)、内存操作(mem/manually_drop)、fmt/格式化、Future trait、基本宏。core不提供：堆分配(Box/Vec)、IO(File/println)、线程(thread)。嵌入式Rust使用两抽象层：PAC(Peripheral Access Crate)——内存映射寄存器的薄封装。HAL(Hardware Abstraction Layer)——高层次的硬件抽象。

## no_std生态

""alloc crate提供堆分配(String/Vec/Box/Rc等需要全局分配器的类型)——比std更轻量且不需要操作系统。全局分配器通过#[global_allocator]设置。embedded-hal trait定义跨芯片通用的硬件接口(spi/i2c/serial/digital IO)，允许驱动的一次编写到处可用。panic_handler和exception handler必须在no_std中定义。cortex-m/riscv crate为各自架构提供启动代码和中断处理。

## 关键结论

""1. no_std无panic unwind(默认panic=abort节省闪存) 2. 格式化宏(write!/format!)在core中可用但需要实现fmt::Write 3. 浮点运算不保证硬件支持(soft-float) 4. .cargo/config.toml指定target和三元组 5. 链接脚本控制内存布局(ld file)

## 关联知识点

""[[Rust语言-Drop与资源管理]] [[Rust语言-FFI与unsafe Rust]] [[计算机组成原理-嵌入式系统基础]]
