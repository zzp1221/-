---
title: "公钥基础设施（PKI）与数字证书"
course: 计算机网络
chapter: 安全
difficulty: INTERMEDIATE
tags: [计算机网络, PKI, 证书, CA, x509]
aliases: [Public Key Infrastructure]
source: "RFC 5280 (X.509); Bulletproof SSL and TLS (Ristic)"
updated_at: 2026-05-02
---

## 核心定义

PKI是管理数字证书的体系，解决公钥认证问题。核心组件：CA(证书颁发机构，验证身份后签发证书)、RA(注册机构，审核请求)、证书吊销列表(CRL)、OCSP(在线证书状态协议)。X.509证书内容：主题(CN/SAN)、颁发者、有效期、公钥、签名、扩展(密钥用法/SAN/基本约束)。证书链：EE证书←中间CA←根CA(自签名，预装于信任库)。

## 关键结论

1. 信任锚(Trust Anchor)是预装的根CA证书（操作系统的信任存储）2. 任何CA颁发的证书都能被信任→最弱环节 3. Let's Encrypt通过ACME协议免费自动签发DV证书 4. 证书吊销：CRL(全量列表)+OCSP(在线查询)+OCSP Stapling(服务端主动附带)

## 关联页面

[[TLS握手与HTTPS]] [[HTTPS安全超文本传输协议]] [[RSA与非对称加密]]
