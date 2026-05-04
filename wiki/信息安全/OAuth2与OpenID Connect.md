---
title: OAuth2与OpenID Connect
course: 信息安全
chapter: 网络安全协议
difficulty: INTERMEDIATE
tags: [OAuth, OpenID Connect, 身份认证, 授权, SSO]
aliases: [OAuth 2.0, OIDC, OpenID Connect, Authorization Framework]
source:
  - RFC 6749 (OAuth 2.0)
  - RFC 6750 (Bearer Token)
  - OpenID Connect Core 1.0
updated_at: 2026-05-03
---

## 核心定义

OAuth 2.0是一个授权框架（RFC 6749），允许第三方应用在用户授权下访问其在资源服务器上的受保护资源，而无需暴露用户凭证。OAuth 2.0的核心角色包括：资源拥有者（Resource Owner，即用户）、客户端（Client，第三方应用）、授权服务器（Authorization Server）和资源服务器（Resource Server）。

**OAuth 2.0的四种授权模式：**
1. **授权码模式（Authorization Code）**：最安全的模式，客户端通过授权服务器获取授权码，再用授权码换取访问令牌。适用于有后端服务器的Web应用。
2. **隐式模式（Implicit）**：直接返回访问令牌给客户端，适用于纯前端SPA应用（已不推荐）。
3. **密码模式（Resource Owner Password Credentials）**：用户直接向客户端提供凭证，仅适用于高度信任的客户端。
4. **客户端凭证模式（Client Credentials）**：客户端以自身身份获取令牌，适用于机器到机器通信。

**OpenID Connect（OIDC）** 是构建在OAuth 2.0之上的身份认证层。OAuth 2.0只解决授权问题（"允许访问什么"），OIDC增加了身份认证能力（"用户是谁"）。OIDC引入ID Token（JWT格式），包含用户身份信息（sub、name、email等），由身份提供商签发。

**授权码模式流程：**
1. 客户端将用户重定向到授权服务器
2. 用户登录并授权
3. 授权服务器返回授权码（authorization_code）给客户端
4. 客户端用授权码换取访问令牌（access_token）和刷新令牌（refresh_token）
5. 客户端使用访问令牌访问资源服务器

## 关键结论

- OAuth 2.0是授权框架，OpenID Connect是认证协议，两者常被混淆
- 授权码模式是最安全的授权模式，PKCE扩展使其也适用于原生应用和SPA
- 访问令牌应设置较短有效期（如1小时），刷新令牌有效期较长用于续期
- 隐式模式因安全问题已被OAuth 2.1草案废弃，推荐使用授权码+PKCE
- JWT（JSON Web Token）是ID Token和Access Token的常用格式，需验证签名和声明

## 易错点

1. 混淆OAuth和OIDC：OAuth只做授权（获取资源访问权限），OIDC在OAuth之上增加认证层（验证用户身份）
2. 忽略state参数防CSRF：授权码模式必须使用state参数防止CSRF攻击，攻击者可诱骗用户绑定攻击者的账户
3. 误认为Access Token应长期有效：Access Token应短有效期（分钟级），泄露后影响有限；Refresh Token用于续期

## 例题

**题目：** 某网站使用Google OAuth 2.0实现第三方登录。(1) 为什么不能直接将Google的用户名密码传递给该网站？(2) 描述授权码模式的完整流程；(3) 如果授权码被截获会怎样？如何防护？

**解答：**
(1) 直接传递用户名密码违反最小权限原则：网站将获得用户Google账户的完全访问权限（包括邮件、文件等），而网站只需要用户身份信息。OAuth 2.0允许用户精确控制授权范围（scope），网站只能访问被授权的资源。
(2) 授权码模式流程：①用户点击"Google登录"，网站将用户重定向到Google授权端点，携带client_id、redirect_uri、scope、state参数；②用户在Google页面登录并授权；③Google将用户重定向回redirect_uri，携带authorization_code和state；④网站后端用authorization_code、client_id、client_secret向Google token端点换取access_token和id_token；⑤网站验证id_token获取用户身份，使用access_token访问Google API获取用户信息。
(3) 授权码被截获的风险：攻击者可尝试用授权码换取令牌。防护措施：①授权码一次性使用（RFC要求）；②授权码有效期短（通常10分钟）；③client_secret保密（攻击者没有secret无法换取令牌）；④使用PKCE扩展（code_verifier/code_challenge）为公共客户端提供额外保护。

## 关联页面

[[身份认证技术]] [[SSL与TLS协议详解]] [[会话安全与Cookie安全]] [[跨站请求伪造CSRF]]
