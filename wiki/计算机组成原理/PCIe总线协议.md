---
title: "PCIe总线协议基础"
course: 计算机组成原理
chapter: IO系统
difficulty: INTERMEDIATE
tags: [计算机组成原理, PCIe, 总线, DMA, IO]
aliases: [PCI Express]
source: "PCI Express Base Specification; Computer Organization and Design (Patterson & Hennessy)"
updated_at: 2026-05-02
---

## 核心定义

PCIe是点对点串行互连总线替代PCI并行总线。层次结构：事务层(TLP组包+QoS虚拟通道VC)、数据链路层(DLLP可靠性+ACK/NAK协议)、物理层(LTSSM链路训练+8b/10b编码Gen1-2或128b/130b编码Gen3+)。通信模型：基于地址路由(address routing)、ID路由(BDF)、隐式路由(消息only-root)。支持SR-IOV(单物理设备虚拟化为多个VF)、ATS(地址翻译服务)、PRI(页面请求接口)。

## 关键结论

1. Lane是差分信号对(1/2/4/8/16/32 lanes) 2. 各代速率：Gen3=8GT/s, Gen4=16GT/s, Gen5=32GT/s 3. PCIe的DMA通过IOMMU(SMMU)隔离 4. CXL(Compute Express Link)基于PCIe物理层和高层协议堆叠

## 关联页面

[[DMA直接存储器访问]] [[中断系统]] [[IO系统概述]]
