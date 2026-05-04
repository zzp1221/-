---
title: 数字证书与X.509
course: 信息安全
chapter: 密码学进阶
difficulty: INTERMEDIATE
tags: [X.509, 数字证书, CA, PKI, 证书格式]
aliases: [X.509, Digital Certificate, X.509 Certificate, PKCS]
source:
  - RFC 5280 (Internet X.509 PKI Certificate)
  - RFC 7468 (Textual Encodings of PKIX)
  - 《密码学基础》Douglas Stinson 第6章
updated_at: 2026-05-03
---

## 核心定义

X.509是ITU-T制定的公钥证书标准，是PKI（公钥基础设施）的基础。X.509数字证书将公钥与实体身份进行绑定，由可信的证书颁发机构（CA）签名保证其真实性。

**X.509证书的核心字段：**
- **Version**：证书版本（v1、v2、v3），v3支持扩展项
- **Serial Number**：CA分配的唯一序列号
- **Signature Algorithm**：CA签名使用的算法（如sha256WithRSAEncryption）
- **Issuer**：颁发者DN（Distinguished Name），即CA的名称
- **Validity**：有效期（Not Before和Not After）
- **Subject**：持有者DN，即证书主体的名称
- **Subject Public Key Info**：持有者的公钥和算法标识
- **Extensions（v3）**：扩展项，定义证书用途和约束

**关键扩展项：**
- **Subject Alternative Name（SAN）**：证书绑定的域名/IP，替代CN作为域名验证的主要字段
- **Key Usage**：密钥用途（digitalSignature、keyEncipherment等）
- **Extended Key Usage**：扩展密钥用途（serverAuth、clientAuth等）
- **Basic Constraints**：是否为CA证书，路径长度约束
- **CRL Distribution Points**：CRL下载地址
- **Authority Info Access**：OCSP响应地址

**证书编码格式：**
- **PEM（Privacy Enhanced Mail）**：Base64编码，以-----BEGIN CERTIFICATE-----开头，可读文本格式
- **DER（Distinguished Encoding Rules）**：二进制格式，不可读
- **PKCS#12（.p12/.pfx）**：包含证书和私钥的加密容器格式

**证书链：** 终端实体证书 ← 中间CA证书 ← 根CA证书（自签名）。验证证书链时，从终端证书开始逐级向上验证签名，直到找到可信根CA。

## 关键结论

- X.509 v3是当前最广泛使用的证书版本，扩展项提供了灵活的功能
- SAN（Subject Alternative Name）已取代CN成为域名验证的主要字段
- 证书格式转换：PEM和DER可以互相转换，PKCS#12用于导出证书+私钥
- Let's Encrypt使用ACME协议自动化证书颁发，支持DV证书
- 证书透明度（Certificate Transparency）通过公开日志监控CA行为

## 易错点

1. 混淆证书和密钥：证书包含公钥和身份信息，由CA签名；私钥由持有者保密存储，不应包含在证书中
2. 忽略SAN扩展：现代浏览器主要检查SAN而非CN，证书配置必须包含正确的SAN
3. 混淆PEM和DER格式：PEM是文本格式（Base64），DER是二进制格式。OpenSSL默认输出PEM

## 例题

**题目：** 企业需要为其Web服务器申请SSL证书。(1) 生成证书签名请求（CSR）的步骤；(2) 证书中应包含哪些关键字段？(3) 如何验证证书链的完整性？

**解答：**
(1) CSR生成步骤：
①生成私钥：openssl genrsa -out server.key 2048
②生成CSR：openssl req -new -key server.key -out server.csr
③填写信息：国家、省份、组织名称、通用名称（域名）
④将CSR提交给CA进行验证和签名
⑤CA签名后返回证书，安装到Web服务器
(2) 关键字段：
①Subject：CN=www.example.com（或使用SAN）
②SAN：DNS:www.example.com, DNS:example.com, IP:1.2.3.4
③Key Usage：digitalSignature, keyEncipherment
④Extended Key Usage：serverAuth
⑤Validity：建议1年（Let's Encrypt为90天）
⑥Signature Algorithm：sha256WithRSAEncryption或ecdsa-with-SHA256
(3) 证书链验证步骤：
①获取终端证书和中间CA证书（服务器应配置完整的证书链）
②验证终端证书的签名：用中间CA的公钥验证
③验证中间CA证书的签名：用根CA的公钥验证
④验证根CA是否在本地信任存储中
⑤检查每个证书的有效期、吊销状态、Basic Constraints、Key Usage
使用命令验证：openssl verify -CAfile root.pem -untrusted intermediate.pem server.pem

## 关联页面

[[PKI与证书体系]] [[PKI信任模型]] [[SSL与TLS协议详解]] [[数字签名原理]]
