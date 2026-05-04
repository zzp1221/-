---
title: "OAuth 2.0与OpenID Connect"
course: 软件工程
chapter: 安全
difficulty: INTERMEDIATE
tags: [OAuth2, OIDC, SSO, JWT, 认证]
aliases: [OAuth 2.0, OpenID Connect]
source: "RFC 6749 (OAuth 2.0); RFC 7519 (JWT); OpenID Connect Spec"
updated_at: 2026-05-02
---

## 核心定义

OAuth 2.0是授权框架而非认证协议：允许第三方应用获权访问用户资源而不暴露密码。四种授权模式：Authorization Code(服务器端App，最安全+PKCE防截获)、Implicit(已废弃)、Resource Owner Password(已废弃)、Client Credentials(服务间)。OpenID Connect(OIDC)在OAuth 2.0之上添加认证层(ID Token=JWT+签名)。JWT结构：Header(typ/alg)+Payload(claims: iss/sub/aud/exp/iat)+Signature(签名防篡改)。

## 关键结论

1. OAuth 2.0用的Token不是JWT(可只是随机字符串)，OIDC的ID Token是JWT 2. refresh token轮换+检测重用防丢失 3. SSO单点登录通常用OIDC实现

## 关联页面

[[SSL与PKI体系]] [[TLS握手与HTTPS]] [[RESTful API设计]]
