---
title: "SDRAM与DDR内存技术"
course: 计算机组成原理
chapter: 存储器层次
difficulty: INTERMEDIATE
tags: [计算机组成原理, DDR, SDRAM, 内存控制器]
aliases: [DDR SDRAM]
source: "Computer Architecture: A Quantitative Approach (Hennessy & Patterson); JEDEC DDR标准"
updated_at: 2026-05-02
---

## 核心定义

DRAM存储单元是1T1C(1晶体管+1电容)，需要周期性刷新(几十ms刷新一次)。SDRAM(Synchronous DRAM)同步于时钟。DDR(Double Data Rate)在时钟上升沿和下降沿都传输数据。DDR4/5：bank group并行访存、预取(prefetch n=8/16)匹配burst length、burst chop、ZQ校准。内存控制器时序：tRCD(RAS-to-CAS延迟)、tCL(CAS延迟)、tRP(预充电时间)、tRAS(行活跃最小时间)。

## 关键结论

1. Row Buffer Locality：同行访问最快(open page policy) 2. 内存控制器重排请求以最大化row buffer命中 3. 地址映射影响性能：行/列/bank交错 4. 3D堆叠(HBM/HMC)提供更高带宽和更低延迟

## 关联页面

[[缓存体系结构]] [[内存层次结构]] [[NUMA架构]]
