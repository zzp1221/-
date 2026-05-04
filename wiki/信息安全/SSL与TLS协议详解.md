---
title: SSL与TLS协议详解
course: 信息安全
chapter: 网络安全协议
difficulty: INTERMEDIATE
tags: [SSL, TLS, HTTPS, 密钥交换, 传输安全]
aliases: [SSL, TLS, Transport Layer Security, TLS 1.2, TLS 1.3, HTTPS]
source:
  - 《网络安全基础：应用与标准》William Stallings 第5章
  - RFC 5246 (TLS 1.2)
  - RFC 8446 (TLS 1.3)
  - RFC 6101 (SSL 3.0)
updated_at: 2026-05-03
---

## 核心定义

TLS（Transport Layer Security）是保护网络通信安全的密码学协议，其前身是Netscape开发的SSL（Secure Sockets Layer）。TLS工作在传输层之上，为应用层协议（如HTTP、SMTP）提供端到端的安全通信，包括机密性、完整性和身份认证三个核心安全服务。

**TLS协议架构包含四个子协议：**
1. **握手协议（Handshake Protocol）**：协商密码套件、验证身份、交换密钥
2. **记录协议（Record Protocol）**：使用协商的密钥对应用数据进行分片、压缩、加密和认证
3. **告警协议（Alert Protocol）**：传输警告和错误信息
4. **变更密码规范协议（ChangeCipherSpec Protocol）**：通知密码参数切换

**TLS 1.2握手流程：**
1. ClientHello：客户端发送支持的密码套件列表、随机数、扩展
2. ServerHello：服务器选择密码套件，发送随机数、证书
3. 服务器密钥交换（如DHE/ECDHE）
4. 客户端验证证书，发送密钥交换消息
5. 双方计算主密钥（Master Secret），切换到加密通信

**TLS 1.3的重要改进：**
- 握手从2-RTT简化为1-RTT（首次连接）和0-RTT（恢复连接）
- 移除所有不安全的密码套件（RSA密钥交换、CBC模式、SHA-1、静态DH等）
- 强制使用前向安全的密钥交换（DHE/ECDHE）
- 密码套件简化为仅5种，基于AEAD加密（AES-GCM、ChaCha20-Poly1305）
- 握手消息全部加密（除ClientHello/ServerHello外）

## 关键结论

- SSL 2.0/3.0和TLS 1.0/1.1已被废弃，应使用TLS 1.2或TLS 1.3
- TLS 1.3强制前向安全性，消除了RSA密钥交换模式
- HTTPS = HTTP over TLS，默认端口443
- 证书验证是TLS安全的关键环节，证书钉扎（Certificate Pinning）可防止CA被攻陷的风险
- TLS 1.3的0-RTT模式存在重放攻击风险，不应用于非幂等操作

## 易错点

1. 混淆TLS握手和数据传输：握手阶段使用非对称加密协商密钥，数据传输阶段使用对称加密
2. 忽略密码套件的安全性：TLS 1.2支持不安全的密码套件（如RC4、NULL加密），必须在服务器配置中禁用
3. 误认为HTTPS完全安全：HTTPS只保护传输层安全，不防范应用层攻击（如XSS、SQL注入）

## 例题

**题目：** 分析TLS 1.2与TLS 1.3的主要区别。(1) TLS 1.3移除了哪些密码组件？为什么？(2) TLS 1.3握手如何从2-RTT减少到1-RTT？(3) 什么是0-RTT，它有什么安全风险？

**解答：**
(1) TLS 1.3移除的组件及原因：①RSA密钥交换——不提供前向安全性，私钥泄露可解密所有历史流量；②CBC模式——存在填充预言攻击（POODLE）和时序攻击风险；③SHA-1——已被证明不安全；④静态DH——不提供前向安全性；⑤压缩——存在CRIME攻击；⑥协商重放——存在降级攻击风险。
(2) TLS 1.3在ClientHello中直接发送密钥共享（KeyShare）扩展，包含客户端的ECDHE公钥。服务器在ServerHello中返回自己的ECDHE公钥，双方立即计算共享密钥，后续消息全部加密。省去了TLS 1.2中证书交换和密钥交换的额外往返，实现1-RTT。
(3) 0-RTT允许客户端在ClientHello中携带加密的应用数据（Early Data），使用预共享密钥（PSK）派生的密钥加密。安全风险：0-RTT数据没有前向安全性（使用PSK派生的密钥）；可能被重放攻击（攻击者截获并重放ClientHello），因此不应用于非幂等操作（如转账）。

## 关联页面

[[对称加密与DES-AES]] [[非对称加密RSA]] [[Diffie-Hellman密钥交换]] [[数字证书与X.509]]
