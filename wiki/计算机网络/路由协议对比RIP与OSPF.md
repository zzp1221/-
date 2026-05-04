---
title: "路由协议对比（RIP与OSPF）"
course: 计算机网络
chapter: 网络层
difficulty: INTERMEDIATE
tags: [计算机网络, RIP, OSPF, 路由协议, IGP]
aliases: [RIP, OSPF]
source: "RFC 2453 (RIPv2); RFC 2328 (OSPFv2); TCP/IP Illustrated (Stevens)"
updated_at: 2026-05-02
---

## 核心定义

RIP(路由信息协议)：距离向量协议，跳数为度量（最大15跳），每30s广播完整路由表，实现简单但收敛慢且不适用大型网络。OSPF(开放最短路径优先)：链路状态协议，使用Dijkstra计算最短路径树。基于区域(Area)层次化设计（Area 0为骨干），支持VLSM/CIDR。链路状态变化时通过LSA洪泛增量更新。

## 关键结论

1. RIP适用于小型扁平网络，OSPF适用于企业/ISP大型网络 2. OSPF的无环收敛远快于RIP的计数到无穷 3. OSPF Area划分减少LSA洪泛范围 4. IS-IS与OSPF功能类似，运营商更偏好IS-IS

## 关联页面

[[BGP协议与互联网路由]] [[最短路径Dijkstra]] [[网络层概述]]
