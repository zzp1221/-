---
title: Kerberos认证协议
course: 信息安全
chapter: 网络安全协议
difficulty: INTERMEDIATE
tags: [Kerberos, 认证协议, 票据, 域认证]
aliases: [Kerberos, Ticket Granting Service, KDC]
source:
  - 《网络安全基础：应用与标准》William Stallings 第6章
  - RFC 4120 (Kerberos V5)
updated_at: 2026-05-03
---

## 核心定义

Kerberos是一种基于对称加密和可信第三方的网络认证协议，由MIT开发，以希腊神话中的三头犬命名。Kerberos的核心思想是：用户只需向认证服务器证明一次身份，即可获得访问多个网络服务的票据，实现单点登录（SSO）。

**Kerberos的核心组件：**
- **KDC（Key Distribution Center）**：包含AS（认证服务器）和TGS（票据授予服务器）
- **客户端（Client）**：请求服务的用户
- **服务端（Server）**：提供资源的服务

**Kerberos认证流程（简化的三方认证）：**
1. **AS_REQ**：客户端向AS发送用户ID和TGS请求
2. **AS_REP**：AS验证用户身份，返回TGT（票据授予票据），用用户密钥加密
3. **TGS_REQ**：客户端向TGS出示TGT和请求的服务ID
4. **TGS_REP**：TGS验证TGT，返回服务票据（Service Ticket）
5. **AP_REQ**：客户端向服务端出示服务票据
6. **AP_REP**：服务端验证票据，建立双向认证

Kerberos使用时间戳防止重放攻击，要求所有参与方的时钟同步（默认容忍5分钟偏差）。票据有有效期（通常10小时），过期需要重新认证。

## 关键结论

- Kerberos基于对称加密（默认AES），不使用公钥密码学（除非启用PKINIT扩展）
- 单点登录是Kerberos的核心优势：一次认证即可访问域内所有授权服务
- Kerberos是Active Directory域认证的基础协议
- 时间同步是Kerberos正常工作的前提，时钟偏差超过容忍值会导致认证失败
- Kerberos的主要局限：不适合跨域认证扩展、依赖中心化KDC

## 易错点

1. 混淆TGT和Service Ticket：TGT用于向TGS申请服务票据，不直接用于访问服务；Service Ticket用于访问具体服务
2. 忽略时间同步要求：Kerberos使用时间戳防重放，时钟不同步会导致认证失败，这是实际部署中最常见的问题
3. 误认为Kerberos提供加密通信：Kerberos只提供认证服务，数据加密需要额外机制

## 例题

**题目：** 在Windows域环境中，用户登录后访问文件服务器。(1) 描述完整的Kerberos认证流程；(2) 如果用户密码被修改，是否需要注销重新登录？(3) 攻击者能否截获TGT冒充用户？

**解答：**
(1) 完整流程：①用户输入密码，客户端从密码派生密钥K_client；②客户端向KDC的AS发送AS_REQ（用户ID）；③AS查找用户密钥，用K_client加密TGT（包含会话密钥K_c_tgs），返回AS_REP；④客户端解密得到TGT和K_c_tgs；⑤客户端向TGS发送TGS_REQ（TGT + 服务ID + Authenticator）；⑥TGS验证TGT和Authenticator，返回Service Ticket（用服务器密钥加密）；⑦客户端向文件服务器发送AP_REQ（Service Ticket + Authenticator）；⑧服务器验证票据，返回AP_REP完成双向认证。
(2) 修改密码后不需要立即注销。TGT在有效期内仍可使用，因为它用旧密钥加密。但TGT过期后，AS_REQ将使用新密码派生的密钥，此时需要使用新密码重新认证。
(3) 攻击者无法仅通过截获TGT冒充用户，因为：①TGT用用户密钥加密，攻击者无法解密获得会话密钥K_c_tgs；②客户端需要向TGS发送Authenticator（包含时间戳，用K_c_tgs加密），攻击者没有K_c_tgs无法构造有效的Authenticator。但如果攻击者获取了用户密码（如通过键盘记录），则可以完全冒充用户。

## 关联页面

[[身份认证技术]] [[对称加密与DES-AES]] [[访问控制模型RBAC与ABAC]] [[SSL与TLS协议详解]]
