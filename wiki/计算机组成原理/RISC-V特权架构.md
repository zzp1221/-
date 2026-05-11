---
title: "RISC-V特权架构"
course: 计算机组成原理
chapter: 指令集架构
difficulty: INTERMEDIATE
tags: [计算机组成, RISC-V, 特权架构, 指令集]
aliases: [RISC-V Privileged Architecture, Machine Mode, Supervisor Mode]
source: "RISC-V Privileged Specification v1.12; Patterson & Waterman《The RISC-V Reader》; RISC-V International"
updated_at: 2026-05-02
---

## 核心定义

RISC-V特权架构定义了三个(或四个)特权级(Modes)：Machine Mode(M-mode,最高权限——固件/安全管理器)，Supervisor Mode(S-mode,操作系统内核)，User Mode(U-mode,应用程序)。可选Hypervisor Mode(H-mode,H扩展——虚拟机监视器)。每个级别有独立的CSR(Control and Status Register)集合。模式切换通过异常(exception)和中断(interrupt)触发——mret/sret指令从陷阱处理返回。物理内存保护(PMP)在M-mode配置以约束低特权模式的物理内存访问。

## 中断与虚拟内存

RISC-V的中断有三种：软件中断(通过设置CSR中的相应位进而触发)、定时器中断(timer)、外部中断(PLIC——Platform-Level Interrupt Controller)。AI(AIA Advanced Interrupt Architecture)引入了MSI(Message-signaled Interrupts)。虚拟内存支持Sv32(两级页表, 32位)、Sv39(三级页表, 39位VA, RV64)、Sv48和Sv57(更大的虚拟地址空间)。TLB的管理通过SFENCE.VMA指令同步——将VA或ASID指定的TLB条目失效。每个页表项包含accessed(A)和dirty(D)位(硬件管理或软件模拟)。

## 关键结论

1. RISC-V的开放性令其特权架构极适用于教学和定制处理器 2. M-mode在简单的嵌入式系统中可以实现全部功能(无OS——裸机/bare metal) 3. 可选ISA扩展(Vector/Kryptography等)可通过CSR的misa寄存器检测 4. 调试支持(JTAG触发模块——trigger module) 5. 不同于x86的ring模型,RISC-V的固定三模式相对更简单一致

## 关联知识点

[[计算机组成原理-指令集架构]] [[计算机组成原理-分支预测器深度]] [[操作系统-虚拟内存与TLB]]
