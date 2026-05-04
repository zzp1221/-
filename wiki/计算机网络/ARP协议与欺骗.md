---
title: "ARP协议与ARP欺骗"
course: 计算机网络
chapter: 数据链路层
difficulty: INTERMEDIATE
tags: [计算机网络, ARP, ARP欺骗, 中间人攻击, MAC]
aliases: [Address Resolution Protocol]
source: "RFC 826 (ARP); TCP/IP Illustrated (Stevens) 第4章"
updated_at: 2026-05-02
---

## 核心定义

ARP将IP地址解析为MAC地址。主机广播ARP Request(Who has IP x.x.x.x?)，目标主机单播ARP Reply(I have, MAC=aa:bb:cc)。ARP缓存保存IP-MAC映射（动态条目的过期时间通常几分钟）。ARP欺骗(ARP Spoofing/Poisoning)：攻击者发送伪造ARP Reply将IP映射到自己的MAC，实现中间人攻击。防御：静态ARP、DAI(动态ARP检测)、802.1X。

## 关键结论

1. ARP是无状态协议（可接收未请求的Reply）→本质不安全 2. Gratuitous ARP用于IP变更通知和冲突检测 3. ARP仅限同一广播域（二层网络）4. IPv6用NDP(邻居发现协议)替代ARP

## 关联页面

[[以太网帧格式]] [[IP协议基础]] [[网络安全基础]]
