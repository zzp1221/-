---
title: Diffie-Hellman密钥交换
course: 信息安全
chapter: 密码学基础
difficulty: INTERMEDIATE
tags: [密钥交换, Diffie-Hellman, 离散对数, 前向安全]
aliases: [DH Key Exchange, Diffie-Hellman, DHE, ECDHE]
source:
  - 《密码学基础》Douglas Stinson 第7章
  - 《网络安全基础：应用与标准》William Stallings 第2章
  - RFC 2631 (Diffie-Hellman)
  - RFC 7919 (FFDHE)
updated_at: 2026-05-03
---

## 核心定义

Diffie-Hellman（DH）密钥交换是1976年由Whitfield Diffie和Martin Hellman提出的第一个公钥密码学方案，它允许两个通信方在不安全的信道上协商出一个共享秘密密钥，而无需事先共享任何秘密信息。DH密钥交换的安全性基于离散对数问题（Discrete Logarithm Problem, DLP）的困难性。

**DH密钥交换协议过程：**
1. 公共参数：选择大素数p和生成元g（g是模p的原根）
2. Alice选择随机私钥a，计算公钥A = g^a mod p，发送A给Bob
3. Bob选择随机私钥b，计算公钥B = g^b mod p，发送B给Alice
4. Alice计算共享密钥K = B^a mod p = (g^b)^a mod p = g^(ab) mod p
5. Bob计算共享密钥K = A^b mod p = (g^a)^b mod p = g^(ab) mod p

双方计算出相同的共享密钥g^(ab) mod p，而窃听者只能看到g^a mod p和g^b mod p，要从中计算g^(ab) mod p面临计算Diffie-Hellman问题（CDH）的困难性。

**前向安全性（Forward Secrecy）**：静态DH使用长期固定的密钥对，如果长期私钥泄露，所有历史会话密钥都可被计算。临时DH（DHE）每次会话使用新的临时密钥对，会话结束后立即销毁，即使长期私钥泄露也不影响历史会话的安全性。

ECDHE（Elliptic Curve Diffie-Hellman Ephemeral）是DH的椭圆曲线版本，在提供同等安全性的同时使用更短的密钥（256位ECDHE ≈ 3072位DH），计算效率更高。TLS 1.3强制使用ECDHE。

## 关键结论

- DH密钥交换不提供身份认证，容易受到中间人攻击（MITM），必须与数字签名或证书结合使用
- DHE提供前向安全性，TLS 1.3要求使用DHE或ECDHE
- DH的安全参数选择至关重要：素数p至少2048位，建议使用标准化的FFDHE参数（RFC 7919）
- Logjam攻击利用了弱DH参数（512/1024位），展示了参数选择不当的风险
- 椭圆曲线DH（ECDHE）因效率优势已成为主流选择

## 易错点

1. 忽略DH不提供认证性：基础DH协议只建立共享密钥，不验证通信对方身份，必须配合认证机制使用
2. 混淆静态DH和临时DH：静态DH（DH）使用长期密钥，不提供前向安全性；临时DH（DHE）每次生成新密钥，提供前向安全性
3. 低估参数选择的重要性：弱素数或小生成元会导致离散对数问题变得容易求解

## 例题

**题目：** Alice和Bob使用DH密钥交换协议，公共参数p=23, g=5。Alice选择私钥a=6，Bob选择私钥b=15。(1) 计算Alice和Bob各自的公钥；(2) 计算共享密钥；(3) 如果攻击者Eve截获了两个公钥A和B，她如何计算共享密钥？为什么这在实际中不可行？

**解答：**
(1) Alice的公钥A = g^a mod p = 5^6 mod 23
5^1=5, 5^2=25 mod 23=2, 5^4=4, 5^6=5^4×5^2=4×2=8，所以A=8
Bob的公钥B = g^b mod p = 5^15 mod 23
5^8=(5^4)^2=16, 5^15=5^8×5^4×5^2×5^1=16×4×2×5=640 mod 23=640-27×23=640-621=19，所以B=19
(2) Alice计算K = B^a mod p = 19^6 mod 23
19 mod 23=19, 19^2=361 mod 23=361-15×23=16, 19^3=16×19=304 mod 23=304-13×23=5
19^6=(19^3)^2=25 mod 23=2，K=2
Bob计算K = A^b mod p = 8^15 mod 23 = 2（验证一致），共享密钥K=2
(3) Eve知道g=5, p=23, A=8, B=19。要计算g^(ab) mod p=2，需要先从A=g^a mod p=8求出a=6（离散对数问题），然后计算B^a mod p。在本例中p很小，可暴力求解；但当p为2048位大素数时，求解离散对数在计算上不可行。

## 关联页面

[[非对称加密RSA]] [[数字签名原理]] [[SSL与TLS协议详解]] [[PKI与证书体系]]
