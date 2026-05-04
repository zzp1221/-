---
title: "NAT技术与穿透方案"
course: 计算机网络
chapter: 网络层
difficulty: INTERMEDIATE
tags: [计算机网络, NAT, 端口映射, 穿透, IPv4]
aliases: [Network Address Translation]
source: "RFC 2663 (NAT); RFC 3489 (STUN); RFC 8656 (TURN); RFC 8445 (ICE)"
updated_at: 2026-05-02
---

## 核心定义

NAT(网络地址转换)将私有IP映射为公网IP解决IPv4地址枯竭。类型：SNAT(源地址转换/内网出)、DNAT(目的地址转换/端口映射)、PAT(端口地址转换/NAPT——IP+Port复用)。穿透方案：STUN(获取公网映射地址)、TURN(中继转发，最可靠但带宽成本高)、ICE(综合STUN+TURN自动选择最佳路径)、UPnP/NAT-PMP(端口映射协议)。

## 关键结论

1. Full Cone NAT最宽松（任何外部主机可访问映射端口）2. Symmetric NAT最严格（仅被访问过的外部主机可回访）3. 运营商级NAT(CGNAT/Carrier-Grade NAT)使一个公网IP共享给数百用户 4. IPv6下的NAT66一般不推荐

## 关联页面

[[IP协议基础]] [[IPv4与IPv6]] [[P2P网络]]
