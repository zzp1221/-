---
title: "VLAN与802.1Q"
course: 计算机网络
chapter: 数据链路层
difficulty: INTERMEDIATE
tags: [计算机网络, VLAN, 802.1Q, Trunk, 交换机]
aliases: [Virtual LAN]
source: "IEEE 802.1Q标准; CCNA Official Cert Guide"
updated_at: 2026-05-02
---

## 核心定义

VLAN(虚拟局域网)在二层交换机上将物理网络划分为多个逻辑隔离的广播域。802.1Q标签插入以太网帧Header中（4字节：TPID 0x8100 + PCP 3bit + DEI 1bit + VLAN ID 12bit = 4094个VLAN）。Trunk端口承载多个VLAN流量（打标签），Access端口承载单个VLAN（不打标签）。VLAN间通信需通过三层路由（SVI或路由子接口）。

## 关键结论

1. VLAN隔离广播域（不经过三层路由无法跨VLAN通信）2. Native VLAN的帧不打标签（默认为VLAN 1）3. VXLAN(24bit VNI)解决数据中心VLAN ID不足问题 4. VLAN跳跃攻击通过双标签绕过VLAN隔离

## 关联页面

[[以太网帧格式]] [[交换机工作原理]] [[网络虚拟化]]
