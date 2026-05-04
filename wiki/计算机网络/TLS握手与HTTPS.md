---
title: "TLS握手与HTTPS工作原理"
course: 计算机网络
chapter: 安全
difficulty: INTERMEDIATE
tags: [计算机网络, TLS, HTTPS, SSL, 安全]
aliases: [TLS Handshake, HTTPS]
source: "RFC 8446 (TLS 1.3); RFC 5246 (TLS 1.2); Bulletproof SSL and TLS (Ristic)"
updated_at: 2026-05-02
---

## 核心定义

TLS(传输层安全)在TCP之上提供加密、认证和完整性保护。TLS 1.2握手(2-RTT)：ClientHello→ServerHello+Certificate+ServerKeyExchange→ClientKeyExchange+ChangeCipherSpec→Finished。TLS 1.3(1-RTT)：简化为ClientHello(+Key Share)→ServerHello+EncryptedExtensions+Certificate+Finished→Finished。0-RTT支持PSK恢复会话。证书链由CA签发，客户端验证证书链到根CA。

## 关键结论

1. TLS 1.0/1.1已弃用（2021），TLS 1.3是当前标准 2. 前向安全性(Forward Secrecy)由DHE/ECDHE密钥交换保证 3. 证书透明度(Certificate Transparency)防止恶意CA签发 4. SNI(Server Name Indication)支持同一IP多域名HTTPS

## 关联页面

[[HTTPS安全超文本传输协议]] [[HTTP协议基础]] [[网络安全基础]]
