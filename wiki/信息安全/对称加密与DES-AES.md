---
title: 对称加密与DES-AES
course: 信息安全
chapter: 密码学基础
difficulty: BASIC
tags: [对称加密, DES, AES, 分组密码, 密码学]
aliases: [Symmetric Encryption, DES, AES, Data Encryption Standard, Advanced Encryption Standard]
source:
  - 《密码学基础》Douglas Stinson 第2-3章
  - 《网络安全基础：应用与标准》William Stallings 第2章
  - FIPS 46-3 (DES)
  - FIPS 197 (AES)
updated_at: 2026-05-03
---

## 核心定义

对称加密（Symmetric Encryption）是指加密和解密使用相同密钥的密码体制，也称为单密钥密码或秘密密钥密码。其核心思想是发送方和接收方共享一个秘密密钥K，发送方用K将明文P加密为密文C=E(K,P)，接收方用同一K将密文解密为明文P=D(K,C)。对称加密的安全性完全依赖于密钥的保密性，而非算法的保密性（Kerckhoffs原则）。

DES（Data Encryption Standard）是1977年由NIST采纳的对称加密标准，采用Feistel结构，分组长度64位，密钥长度56位（实际64位中8位用于奇偶校验）。DES包含16轮Feistel轮函数，每轮使用48位子密钥，轮函数包括扩展置换E、与子密钥异或、8个S盒替换和P盒置换。S盒是DES的核心非线性组件，每个S盒将6位输入映射为4位输出。DES的主要弱点是56位密钥太短，1998年EFF的Deep Crack机器在56小时内破解DES。

AES（Advanced Encryption Standard）是2001年NIST选定的替代DES的标准，原名Rijndael，由比利时密码学家Daemen和Rijmen设计。AES采用替代-置换网络（SPN）结构，分组长度128位，支持128/192/256位三种密钥长度。AES-128执行10轮，AES-192执行12轮，AES-256执行14轮。每轮操作包括四个步骤：SubBytes（S盒替换字节）、ShiftRows（行移位）、MixColumns（列混淆）和AddRoundKey（轮密钥加）。最后一轮省略MixColumns操作。AES的设计强调数学可证明性，S盒基于有限域GF(2^8)上的乘法逆元构造。

## 关键结论

- 对称加密分为分组密码和流密码两大类，DES和AES属于分组密码
- DES的56位密钥已不安全，实际应用必须使用3DES或AES替代
- 3DES使用三个不同密钥K1/K2/K3执行E-D-E操作，有效密钥长度112位，但速度仅为DES的1/3
- AES-128已足够安全，AES-256提供更高的安全裕度，适用于绝密级信息
- 分组密码工作模式（ECB/CBC/CTR/GCM）的选择对安全性至关重要，ECB模式因相同明文产生相同密文而存在安全问题

## 易错点

1. 混淆DES密钥长度：DES密钥输入为64位，但实际有效密钥长度为56位，每字节的第8位用于奇偶校验，不参与加密运算
2. 误认为AES使用Feistel结构：AES采用SPN（替代-置换网络）结构而非Feistel结构，这是AES与DES的重要架构区别
3. 忽略工作模式的安全影响：即使使用AES-256，如果采用ECB模式，仍会泄露明文模式。推荐使用CTR或GCM等安全模式

## 例题

**题目：** 假设使用AES-128对一个1MB的文件进行加密，密钥为K。请回答：(1) AES-128的分组长度和轮数分别是多少？(2) 如果使用ECB模式，相同的128位明文分组会产生什么安全问题？(3) 推荐使用什么工作模式来解决此问题？

**解答：**
(1) AES-128的分组长度为128位（16字节），轮数为10轮。
(2) ECB模式下，相同的明文分组在相同密钥下总是产生相同的密文分组。攻击者可以通过观察密文模式推断明文模式，例如图像加密后仍可看出轮廓。这破坏了语义安全性。
(3) 推荐使用CBC模式（需随机IV）、CTR模式或GCM模式（同时提供加密和认证）。GCM模式（Galois/Counter Mode）是当前最推荐的选择，因为它同时提供机密性和完整性保护，且支持并行处理。

## 关联页面

[[非对称加密RSA]] [[哈希函数与SHA系列]] [[消息认证码MAC与HMAC]] [[数字签名原理]]
