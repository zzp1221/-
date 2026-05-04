---
title: IPSec协议体系
course: 信息安全
chapter: 网络安全协议
difficulty: INTERMEDIATE
tags: [IPSec, AH, ESP, IKE, VPN, 网络层安全]
aliases: [IPSec, Internet Protocol Security, AH, ESP, IKEv2]
source:
  - 《网络安全基础：应用与标准》William Stallings 第8章
  - RFC 4301 (IPSec Architecture)
  - RFC 4302 (AH)
  - RFC 4303 (ESP)
  - RFC 7296 (IKEv2)
updated_at: 2026-05-03
---

## 核心定义

IPSec（Internet Protocol Security）是IETF制定的网络层安全协议族，为IP数据包提供认证、完整性、机密性和防重放保护。IPSec是构建VPN（虚拟专用网络）的基础协议，可在网络层实现端到端的安全通信。

**IPSec包含两个核心协议：**
1. **AH（Authentication Header，认证头）**：提供数据源认证、完整性和防重放保护，但不提供机密性。AH对整个IP数据包（包括IP头的部分字段）进行认证。
2. **ESP（Encapsulating Security Payload，封装安全载荷）**：提供数据源认证、完整性、机密性和防重放保护。ESP对载荷数据进行加密，并对加密后的数据进行认证。

**IPSec的两种工作模式：**
- **传输模式（Transport Mode）**：只加密/认证IP载荷，IP头不变。适用于主机到主机的通信。
- **隧道模式（Tunnel Mode）**：加密/认证整个原始IP包，并封装在新的IP头中。适用于VPN网关之间的通信。

**SA（Security Association，安全关联）** 是IPSec的核心概念，由三元组唯一标识：SPI（安全参数索引）+ 目的IP地址 + 安全协议（AH/ESP）。SA定义了安全参数：加密算法、认证算法、密钥、序列号等。

**IKE（Internet Key Exchange）** 协议用于自动协商和管理SA。IKEv2（RFC 7296）通过两阶段协商：阶段1建立IKE SA（使用DH交换建立安全通道），阶段2建立子SA（协商IPSec SA的具体参数）。

## 关键结论

- AH因不提供机密性且NAT不兼容，实际应用中已被ESP取代
- IPSec隧道模式是构建站点到站点VPN的标准方式
- IKEv2相比IKEv1更高效、更安全，支持MOBIKE（移动性和多宿主扩展）
- IPSec与NAT的兼容性问题通过NAT-T（NAT Traversal，UDP封装ESP）解决
- 传输模式适用于主机间通信，隧道模式适用于网关间VPN

## 易错点

1. 混淆AH和ESP的功能：AH提供认证但不加密，ESP同时提供认证和加密。实际应用中优先选择ESP
2. 混淆传输模式和隧道模式：传输模式不改变IP头，隧道模式封装整个IP包。VPN场景使用隧道模式
3. 忽略SA的方向性：每个SA是单向的，双向通信需要两个SA（入站SA和出站SA）

## 例题

**题目：** 企业总部和分支机构通过IPSec VPN连接。(1) 应选择传输模式还是隧道模式？为什么？(2) 应选择AH还是ESP？为什么？(3) 描述IKEv2阶段1的简化流程。

**解答：**
(1) 应选择隧道模式。原因：①隧道模式封装整个原始IP包，隐藏内部网络拓扑结构；②分支机构的私有IP地址需要在公网传输，隧道模式通过新的IP头解决路由问题；③VPN场景需要保护整个IP包而非仅载荷。
(2) 应选择ESP。原因：①ESP同时提供加密和认证，AH仅提供认证不加密；②AH与NAT不兼容（AH认证IP头，NAT修改IP头会破坏认证），而ESP通过NAT-T可以穿越NAT；③企业VPN需要保护数据机密性，仅AH无法满足。
(3) IKEv2阶段1（IKE_SA_INIT交换）简化流程：①Initiator发送IKE_SA_INIT请求，包含密码套件列表、DH公钥、Nonce；②Responder选择密码套件，返回DH公钥和Nonce；③双方使用DH共享密钥和Nonce派生IKE SA密钥。此阶段建立安全通道，后续通信加密保护。阶段2（IKE_AUTH交换）在安全通道中交换身份、证书和子SA参数。

## 关联页面

[[VPN技术]] [[SSL与TLS协议详解]] [[防火墙技术]] [[Diffie-Hellman密钥交换]]
