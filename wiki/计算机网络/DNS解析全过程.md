---
title: "DNS解析全过程"
course: 计算机网络
chapter: 应用层
difficulty: BASIC
tags: [计算机网络, DNS, 域名解析, 应用层]
aliases: [DNS Resolution]
source: "RFC 1034; RFC 1035"
updated_at: 2026-05-02
---

## 核心定义

DNS将域名转换为IP地址。解析顺序：浏览器缓存→OS hosts文件→本地DNS服务器→根域名服务器(.)→顶级域名服务器(.com/.org)→权威DNS服务器。递归查询：客户端→本地DNS→根→顶级→权威，层层代为查询。迭代查询：本地DNS逐个向根、顶级、权威查询。DNS使用UDP端口53(≤512字节)和TCP端口53(区域传送/大响应)。

## 关键结论

1. 根服务器全球13组(A-M)，采用Anycast 2. DNS劫持/DNS污染是常见安全问题 3. DNSSEC通过数字签名防止DNS欺骗 4. DNS over HTTPS(DoH)和DNS over TLS(DoT)加密DNS查询

## 关联页面

[[DNS域名系统]] [[HTTP协议基础]] [[HTTPS安全超文本传输协议]]
