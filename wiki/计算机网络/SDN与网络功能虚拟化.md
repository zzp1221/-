---
title: SDN与网络功能虚拟化
course: 计算机网络
chapter: 网络架构
difficulty: INTERMEDIATE
tags: [计算机网络, SDN, NFV, OpenFlow, 网络虚拟化]
aliases: [Software Defined Networking, NFV, 软件定义网络]
source:
  - Open Networking Foundation SDN白皮书
  - OpenFlow规范1.5
  - ETSI NFV白皮书
updated_at: 2026-05-03
---

## 核心定义

软件定义网络（SDN）将网络的控制平面（Control Plane）与数据平面（Data Plane）分离，通过集中式控制器（如OpenDaylight、ONOS）统一管理网络设备。传统网络中每个交换机独立运行路由协议（如OSPF），SDN将路由决策集中到控制器，交换机只负责按流表（Flow Table）转发。OpenFlow是SDN的标准南向接口协议，定义了控制器与交换机之间的通信协议。SDN的核心优势：集中视图（全局网络拓扑可见）、可编程性（通过软件定义网络行为）、快速配置（不用逐台设备配置）。网络功能虚拟化（NFV）将传统硬件网络设备（防火墙、负载均衡器、路由器）以虚拟机/容器形式运行在通用服务器上。NFV与SDN互补：SDN解决网络控制问题，NFV解决网络功能部署问题。NFV架构：NFVI（基础设施）→ VNF（虚拟网络功能）→ MANO（管理编排）。

## 关键结论

- SDN的核心价值是网络可编程和集中管控，适合数据中心、园区网等需要灵活配置的场景
- OpenFlow流表由匹配字段（如MAC/IP/端口）+ 动作（如转发/丢弃/修改）组成
- SDN控制器是单点故障风险，需要集群化部署（如ONOS的分布式控制平面）
- NFV使网络功能从专用硬件解耦，降低了运营商的设备成本
- P4（Programming Protocol-independent Packet Processors）是新一代可编程数据平面语言

## 易错点

1. SDN不只是"用软件管理网络"：核心是控制面与数据面分离，不是简单地加个网管系统
2. SDN控制器不是传统网管：网管只做监控配置，SDN控制器直接决定数据包的转发路径
3. NFV不等于SDN：NFV可以不依赖SDN独立部署（用传统网络），SDN也可以不使用NFV

## 例题

**例1：** 在一个数据中心网络中，使用SDN实现动态流量调度。当检测到某条链路拥塞时，控制器如何调整流量路径？

**解答：** (1)SDN控制器通过OpenFlow的Packet-In消息获取链路状态（或通过sFlow/NetFlow采集流量数据）。(2)控制器检测到链路A→B拥塞（利用率>80%）。(3)控制器使用全局拓扑视图计算替代路径（如A→C→D→B），使用最短路径算法（Dijkstra）或ECMP均衡。(4)控制器通过OpenFlow的Flow-Mod消息向沿途交换机下发新流表：交换机1的匹配字段匹配相关流量→动作改为转发到端口C。(5)新流表立即生效，后续匹配的数据包走新路径。整个过程不需要重启设备，毫秒级完成。

## 关联页面

[[交换机与VLAN]] [[负载均衡技术]] [[路由选择算法]]
