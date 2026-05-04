---
title: "IPv4与IPv6全面对比"
course: 计算机网络
chapter: 网络层
difficulty: BASIC
tags: [计算机网络, IPv4, IPv6, 网络层, 地址空间]
aliases: [IPv4 vs IPv6]
source: "RFC 791 (IPv4); RFC 8200 (IPv6); TCP/IP Illustrated"
updated_at: 2026-05-02
---

## 核心定义

IPv4: 32位地址(约43亿)，点分十进制，有类/无类(CIDR)，需NAT解决枯竭。头部20-60字节含checksum需路由器重新计算。IPv6: 128位地址(约3.4×10^38)，冒号十六进制，无NAT(端到端)，头部固定40字节无checksum。地址类型：全球单播(2000::/3)、链路本地(fe80::/10)、唯一本地(fc00::/7)、多播(ff00::/8)。IPv6无广播(用多播替代)。过渡技术：双栈、隧道(6to4/6in4/6rd)、NAT64/DNS64。

## 关键结论

1. IPv6无checksum(由上层保证)→路由器转发更快 2. SLAAC(无状态自动配置)实现即插即用 3. 过渡缓慢因迁移成本高昂→双栈+CGNAT将长期共存 4. 移动IPv6比移动IPv4更简洁(路由优化)

## 关联页面

[[IP分片与重组]] [[NAT技术与穿透]] [[ICMP协议]]
