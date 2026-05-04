---
title: 消息认证码MAC与HMAC
course: 信息安全
chapter: 密码学基础
difficulty: INTERMEDIATE
tags: [MAC, HMAC, 消息认证, 完整性]
aliases: [Message Authentication Code, HMAC, CMAC, GMAC]
source:
  - 《密码学基础》Douglas Stinson 第4章
  - RFC 2104 (HMAC)
  - NIST SP 800-95
updated_at: 2026-05-03
---

## 核心定义

消息认证码（Message Authentication Code, MAC）是一种用于验证消息完整性和来源真实性的密码学原语。MAC是一个由密钥和消息共同决定的固定长度值：t = MAC(K, M)。发送方将MAC值附加到消息中，接收方使用相同的密钥重新计算MAC并比对，如果一致则确认消息来自持有相同密钥的发送方且未被篡改。

MAC与哈希函数的关键区别在于MAC使用密钥，而哈希函数不使用密钥。MAC与数字签名的关键区别在于MAC使用对称密钥（发送方和接收方共享），不提供不可否认性，因为双方都能生成相同的MAC。

**HMAC（Hash-based MAC）** 是基于哈希函数构造MAC的标准方案（RFC 2104），定义为：
HMAC(K, M) = H((K' ⊕ opad) || H((K' ⊕ ipad) || M))

其中K'是从密钥K派生的与哈希函数分组长度等长的密钥，ipad=0x36重复，opad=0x5C重复。HMAC的安全性被证明可以归约到底层哈希函数的抗碰撞性。HMAC-SHA256是当前最广泛使用的MAC方案。

**CMAC（Cipher-based MAC）** 是基于分组密码（如AES）构造的MAC方案，使用CBC模式的最后一个密文块作为MAC值。**GMAC** 是GCM模式的认证部分，基于GHASH函数，支持并行计算。

## 关键结论

- MAC提供消息完整性和来源认证，但不提供机密性（除非与加密结合）
- HMAC的安全性依赖于底层哈希函数的抗碰撞性，HMAC-SHA256是推荐选择
- MAC密钥必须保密且随机生成，密钥长度应与底层算法安全强度匹配
- MAC不提供不可否认性，因为接收方也持有密钥，可以生成相同的MAC
- 认证加密（AE）模式如GCM同时提供加密和认证，是当前最佳实践

## 易错点

1. 混淆MAC和数字签名：MAC使用共享密钥，不提供不可否认性；数字签名使用私钥签名、公钥验证，提供不可否认性
2. 忽略MAC的密钥管理：MAC的安全性完全依赖于密钥的保密性，密钥泄露意味着任何人都能伪造MAC
3. 误认为先加密再MAC（Encrypt-then-MAC不安全）：实际上Encrypt-then-MAC是推荐的安全组合方式，MAC-then-Encrypt存在安全风险（如SSL/TLS中的BEAST攻击）

## 例题

**题目：** Alice和Bob共享MAC密钥K，Alice向Bob发送消息M="Transfer $100 to Eve"。(1) 描述正常的消息认证过程；(2) 攻击者Mallory截获消息，她能否修改消息为"Transfer $1000 to Mallory"并生成有效的MAC？(3) 如果采用HMAC-SHA256，密钥长度应为多少位？

**解答：**
(1) 正常认证过程：①Alice计算t=MAC(K, M)，将(M, t)发送给Bob；②Bob收到后计算t'=MAC(K, M)，比较t'与收到的t；③如果t'=t，则确认消息来自Alice且未被篡改。
(2) Mallory无法生成有效MAC。因为她不知道密钥K，即使她知道消息M和对应的MAC值t，也无法为修改后的消息M'计算出正确的MAC值t'。MAC的安全性保证了在不知道密钥的情况下，为新消息伪造MAC在计算上不可行。
(3) HMAC-SHA256的推荐密钥长度为256位（32字节）。虽然HMAC允许任意长度密钥，但密钥长度应与底层哈希函数的安全强度匹配。SHA-256提供128位碰撞安全强度，但密钥长度通常取输出长度256位以提供完整安全性。

## 关联页面

[[哈希函数与SHA系列]] [[对称加密与DES-AES]] [[数字签名原理]] [[SSL与TLS协议详解]]
