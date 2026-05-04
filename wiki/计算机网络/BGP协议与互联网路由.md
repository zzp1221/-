---
title: "BGP协议与互联网路由"
course: 计算机网络
chapter: 网络层
difficulty: ADVANCED
tags: [计算机网络, BGP, 路由协议, AS, 互联网]
aliases: [Border Gateway Protocol]
source: "RFC 4271 (BGP-4); BGP Design and Implementation (Zhang & Bartell)"
updated_at: 2026-05-02
---

## 核心定义

BGP是互联网的核心路由协议，运行在自治系统(AS)之间。使用路径向量协议，AS_PATH记录路由经过的AS序列（防止环路——收到含自身AS的路径则忽略）。BGP Speaker通过TCP 179端口建立对等连接，交换NLRI(网络层可达信息)。选路流程按属性优先级：Local Preference→AS_PATH长度→Origin→MED→eBGP>iBGP→最低IGP metric→最低Router ID。

## 关键结论

1. BGP是策略路由（非性能路由），选路体现商业关系 2. 前缀劫持是重大安全威胁（通过RPKI防御）3. BGP收敛慢（分钟级），影响全球可达性 4. iBGP全互联需求通过Route Reflector或Confederation解决

## 关联页面

[[路由协议对比RIP与OSPF]] [[IP协议基础]] [[自治系统]]
