---
title: PKI信任模型
course: 信息安全
chapter: 密码学进阶
difficulty: ADVANCED
tags: [PKI, 信任模型, CA层次, 交叉认证, 信任锚]
aliases: [PKI Trust Model, Hierarchical PKI, Bridge CA, Web of Trust]
source:
  - RFC 5280 (Internet X.509 PKI)
  - NIST SP 800-32 (Introduction to PKI)
updated_at: 2026-05-03
---

## 核心定义

PKI信任模型定义了PKI中各方如何建立和管理信任关系。信任模型决定了证书验证者如何确定一个证书是否可信，是PKI体系设计的核心问题。

**主要PKI信任模型：**

1. **层次信任模型（Hierarchical Trust Model）**：最常用的模型，采用树形结构，根CA位于顶层，是所有信任的锚点。信任自上而下传递：信任根CA意味着信任其下所有中间CA签发的证书。优点是结构清晰、证书路径短；缺点是根CA是单点故障。典型应用：Web PKI（浏览器内置根CA列表）。

2. **网状信任模型（Mesh Trust Model）**：多个CA之间通过交叉认证（Cross-Certificate）建立双向信任关系。任意两个CA之间都可以交叉认证。优点是灵活；缺点是证书路径可能很长，验证复杂。适用于对等组织之间的信任。

3. **桥接信任模型（Bridge Trust Model）**：引入一个桥接CA（Bridge CA）作为中心节点，各根CA分别与桥接CA交叉认证，但根CA之间不直接交叉认证。优点是比网状模型更简洁；缺点是桥接CA成为新的信任锚。FBCA（Federal Bridge CA）是美国联邦政府采用的模型。

4. **Web of Trust（信任网络）**：PGP/GPG采用的去中心化信任模型。用户直接互相签名公钥，信任关系通过用户之间的签名链传递。没有中心CA，每个用户自己决定信任谁。优点是去中心化；缺点是信任关系难以管理，不适合大规模使用。

**信任锚（Trust Anchor）**：验证者预先信任的根证书，是证书链验证的起点。浏览器和操作系统内置了可信根CA列表（如Microsoft Trusted Root Store、Mozilla NSS）。

**证书路径验证：** RFC 5280定义了证书路径验证算法，包括：签名验证、有效期检查、吊销状态检查、Basic Constraints检查、Key Usage检查、名称约束检查等。

## 关键结论

- Web PKI采用层次信任模型，浏览器内置约100-150个可信根CA
- 交叉认证实现了不同PKI域之间的互操作，但增加了验证复杂性
- Certificate Transparency通过公开日志弥补了Web PKI中CA信任问题
- 去中心化身份（DID）正在挑战传统PKI的信任模型
- 根CA的私钥保护是整个PKI安全的关键，通常使用离线存储和HSM保护

## 易错点

1. 混淆信任和验证：信任是主观决策（预装根CA），验证是客观过程（检查签名链）
2. 忽略证书路径长度约束：Basic Constraints中的pathLenConstraint限制了中间CA的层级深度
3. 误认为Web of Trust比层次模型更安全：Web of Trust缺乏集中管理，恶意签名难以发现

## 例题

**题目：** 企业A和企业B需要安全通信，各自有自己的PKI体系。(1) 如何实现跨域信任？(2) 证书路径验证需要检查哪些内容？(3) 如果某个中间CA的私钥泄露，影响范围有多大？

**解答：**
(1) 跨域信任方案：
①交叉认证：A的根CA和B的根CA互相签发交叉证书。A的用户信任A的根CA，通过交叉证书也信任B的根CA，从而信任B的用户。
②桥接CA：引入第三方桥接CA，A和B的根CA分别与桥接CA交叉认证。优点是A和B不直接交叉，变更更灵活。
③共同信任第三方：A和B都信任同一个公共CA（如DigiCert），使用该公共CA签发的证书。
(2) 证书路径验证内容（RFC 5280）：
①签名验证：每级证书的签名必须由上级CA的公钥验证
②有效期：每个证书必须在有效期内
③吊销状态：检查CRL或OCSP，确保证书未被吊销
④Basic Constraints：CA证书必须设置CA:TRUE，路径长度约束满足
⑤Key Usage：CA证书必须包含keyCertSign用途
⑥名称约束：如果有名称约束扩展，验证证书主题在允许范围内
⑦策略约束：证书策略映射和策略约束检查
(3) 中间CA私钥泄露的影响：
攻击者可以签发任意域名的证书（如google.com、bank.com），这些证书会被浏览器信任。影响范围取决于该中间CA在证书层次中的位置——越靠近根CA影响越大。缓解措施：①CA立即吊销该中间CA证书；②操作系统和浏览器更新信任存储，移除该CA；③Certificate Transparency日志可帮助发现恶意签发的证书。

## 关联页面

[[PKI与证书体系]] [[数字证书与X.509]] [[数字签名原理]] [[SSL与TLS协议详解]]
