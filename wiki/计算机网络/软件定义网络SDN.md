---
title: "软件定义网络SDN"
course: 计算机网络
chapter: 网络架构
difficulty: ADVANCED
tags: [计算机网络, SDN, OpenFlow, 控制面, 转发面]
aliases: [Software-Defined Networking, OpenFlow, SDN]
source: "ONF (Open Networking Foundation) SDN Architecture; McKeown et al. 2008 (OpenFlow); RFC 7426 SDN Layers"
updated_at: 2026-05-02
---

## 核心定义

SDN(软件定义网络)将网络设备的控制面(control plane,决定如何转发)与数据面(data plane,执行转发)分离。控制面集中部署在SDN控制器(如OpenDaylight, ONOS, Ryu)中，通过南向接口协议(如OpenFlow)下发流表规则到交换机。数据面交换机仅根据流表匹配和转发数据包。这使得网络行为可通过软件编程——无需逐台配置网络设备。SDN的三个核心原则：开放接口、网络虚拟化、网络可编程。

## OpenFlow协议

OpenFlow 1.3/1.5定义了流表(flow table)、组表(group table)和计量表(meter table)。每个流表项包含：匹配字段(12元组——入端口、src/dst MAC、src/dst IP、src/dst Port、EtherType等)、优先级、计数器、指令集(输出到端口、转到下一流表、改写头部字段)。多级流表(pipeline)处理包——先匹配表0再表1...。OpenFlow通道是控制器与交换机间的TLS连接。P4(Programming Protocol-independent Packet Processors)更进一步发展——允许自定义包转发处理逻辑。

## 关键结论

1. SDN的核心价值在数据中心网络中体现最充分(Google的B4 WAN使用SDN获得近乎100%链路利用率) 2. OpenFlow的匹配依赖TCAM(三态内容寻址内存)——昂贵且有限(通常几千条) 3. 控制器的单点故障(SPOF)需通过集群化解决 4. SDN+NFV(网络功能虚拟化)实现端到端可编程网络 5. White-box交换机+开源NOS(SONiC/Stratum)推动网络硬件解耦

## 关联知识点

[[计算机网络-网络命名空间]] [[计算机网络-Anycast与GeoDNS]] [[分布式系统-软件定义存储SDS]]
