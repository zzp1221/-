---
title: "中断系统（APIC与中断处理）"
course: 计算机组成原理
chapter: IO系统
difficulty: INTERMEDIATE
tags: [计算机组成原理, 中断, APIC, MSI, 中断处理]
aliases: [Interrupt System]
source: "Intel x86架构手册第三卷; Linux内核中断处理文档"
updated_at: 2026-05-02
---

## 核心定义

中断是外设异步通知CPU的方式。x86中断系统：I/O APIC汇聚外设中断→LAPIC(本地APIC，每核一个)分发到各CPU核心。中断向量号(0-255)映射到IDT(中断描述符表)的处理程序。MSI(Message Signaled Interrupts)：外设直接往LAPIC地址写中断向量(绕过I/O APIC，更灵活)。MSI-X支持每个中断独立的向量和地址。Linux中断处理：顶半部(top half/硬中断，ISR)快速响应+底半部(tasklet/workqueue/threaded_irq)处理耗时工作。

## 关键结论

1. 中断亲和性(affinity)绑定中断到特定CPU(减少缓存miss) 2. 软中断(SWI)在中断返回前在软中断上下文中执行 3. NMI(不可屏蔽中断)用于最紧急事件(硬件错误/看门狗) 4. 中断风暴(interrupt storm)可由中断共享或设备故障引发

## 关联页面

[[DMA直接存储器访问]] [[设备驱动程序模型]]
