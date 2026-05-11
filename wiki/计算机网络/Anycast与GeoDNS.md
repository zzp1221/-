---
title: "Anycast与GeoDNS"
course: 计算机网络
chapter: 网络基础设施
difficulty: INTERMEDIATE
tags: [计算机网络, Anycast, GeoDNS, CDN, 负载均衡]
aliases: [Anycast, GeoDNS, Global Server Load Balancing]
source: "RFC 4786 (Anycast); RFC 1794 (DNS负载均衡); Cloudflare/CDN architecture docs"
updated_at: 2026-05-02
---

## 核心定义

Anycast是IP路由技术——多个节点广播同一IP地址，BGP路由选择最近的节点交付数据包(基于AS Path长度)。典型应用：DNS根服务器(13个IP地址但数千个物理节点——全部使用Anycast)。GeoDNS将DNS解析结果基于用户地理位置返回——用户查询www.example.com，权威DNS根据查询源IP选择最近的数据中心IP返回。不同于anycast的IP BGP路由，GeoDNS在DNS层做智能调度(能考虑更复杂的策略)。

## CDN中的使用

CDN(内容分发网络)中Anycast和GeoDNS通常分层使用：用户→DNS查询→GeoDNS解析(基于用户IP位置)→返回边缘CDN节点的Anycast IP→TCP连接到最近的CDN边缘节点。Anycast在网络层做粗粒度优化(用户到最近的PoP/Points of Presence)，GeoDNS在应用层做精细调度(健康检查、负载、成本)。Unicast vs Anycast：Anycast的优势——自动故障切换(节点离线时路由自动收敛)；挑战——TCP连接在Anycast变更时可能中断(不同节点不同状态)。

## 关键结论

1. Anycast+TCP不安全——连接中路由变更将导致RST 2. DNS使用Anycast极好(UDP简单查询)——这正是根服务器如此可靠的原因 3. Cloudflare通过Anycast防御DDoS——攻击流量被分散到全球各节点 4. GeoDNS返回的TTL越低切换越快但查询负载越高 5. BGP Anycast的精细化控制有限(只能影响路由策略不能完全控制)

## 关联知识点

[[计算机网络-DNS协议详解]] [[计算机网络-BGP与自治系统]] [[分布式系统-负载均衡策略]]
