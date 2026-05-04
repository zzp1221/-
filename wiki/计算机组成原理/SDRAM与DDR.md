---
title: SDRAM与DDR
course: 计算机组成原理
chapter: 第四章 存储器系统
difficulty: INTERMEDIATE
tags: [SDRAM, DDR, DDR4, DDR5, 同步DRAM, 内存, DIMM]
aliases: [Synchronous DRAM, Double Data Rate, DDR SDRAM]
source:
  - Patterson & Hennessy, Computer Organization and Design
updated_at: 2026-05-02

---

## 核心定义

SDRAM（Synchronous Dynamic RAM，同步动态随机存取存储器）是一种与系统总线时钟同步工作的 DRAM 技术，相较于异步 DRAM，SDRAM 在时钟信号的协调下可流水化地处理命令和数据传输。SDRAM 的命令协议包含激活（ACTIVATE）一个行、经过 tRCD（行到列延迟）后执行读/写（READ/WRITE）命令、CAS 延迟（CL）后数据在数据总线上出现、最后通过预充电（PRECHARGE）关闭行。DDR SDRAM（Double Data Rate SDRAM）是 SDRAM 的演化版本，在时钟信号的上升沿和下降沿均传输数据（双倍数据速率），同时使用预取技术（DDR 预取 2bit、DDR2 4bit、DDR3 8bit、DDR4 8bit、DDR5 16bit）以降低内部存储阵列的频率要求。DDR 的每一代都大幅提升了带宽和降低了功耗：DDR5 的带宽可达 DDR4 的两倍（单根 DIMM 约 38-51GB/s），操作电压从 DDR 的 2.5V 降到 DDR5 的 1.1V。

## 关键结论

- SDRAM 的"同步"在于命令接口与总线时钟同步，内部仍是 DRAM 异步存储阵列
- DDR 预取（Prefetch）机制：时钟 200MHz 的内部阵列配合 8n 预取可实现 1600MT/s 的数据率
- DDR 访问时序关键参数：CL（CAS Latency）、tRCD（行到列延迟）、tRP（预充电时间）
- DDR 内存以 DIMM（Dual Inline Memory Module）模块形式提供，通过内存通道（Channel）与内存控制器连接
- 双通道/四通道：多个内存通道并行工作进一步扩展带宽

## 易错点

1. DDR 的有效频率 ≠ 时钟频率：DDR 的数据率 = 2 * 时钟频率 * 预取深度。例如 DDR4-3200 表示 3200 MT/s 的数据率，其 I/O 时钟频率为 1600MHz（DDR 双沿），内核频率可能只有 400MHz（8n 预取）。
2. CAS 延迟的单位是时钟周期而非纳秒：DDR4-3200 CL16 的延迟 = 16 / (3200/2) * 1000 = 10ns 实际延迟。

## 例题

**例题1：** DDR4-3200 的单通道带宽计算。

**解答：** 数据率 = 3200 MT/s。通道宽度 = 64 bit = 8 B。带宽 = 3200 * 10^6 * 8 = 25.6 GB/s。双通道 = 51.2 GB/s。

**例题2：** DDR5 相比 DDR4 的主要改进。

**解答：** (1) 数据率提升到 4800-8400MT/s；(2) 电压从 1.2V 降到 1.1V，功耗降低；(3) 引入芯片内 ECC（On-Die ECC）；(4) 双通道 DIMM（每 DIMM 两个独立的 40bit 通道而非单个 64bit 通道）；(5) 相同 Bank 刷新（Same Bank Refresh）改进。

## 关联页面

[[SRAM与DRAM]] [[存储器层次结构]] [[存储器容量扩展]]
