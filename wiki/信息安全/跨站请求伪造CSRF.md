---
title: 跨站请求伪造CSRF
course: 信息安全
chapter: Web应用安全
difficulty: INTERMEDIATE
tags: [CSRF, 跨站请求伪造, Web安全, Token防护]
aliases: [Cross-Site Request Forgery, CSRF, XSRF, One-Click Attack]
source:
  - OWASP CSRF Prevention Cheat Sheet
  - CWE-352 (Cross-Site Request Forgery)
updated_at: 2026-05-03
---

## 核心定义

跨站请求伪造（Cross-Site Request Forgery, CSRF）是一种利用用户已认证状态发起非预期请求的攻击。攻击者诱骗已登录用户访问恶意页面，该页面自动向目标网站发送请求，浏览器会自动附带目标网站的Cookie（包括Session ID），使请求看起来是用户自愿发起的。

**CSRF攻击原理：**
1. 用户登录银行网站A，浏览器保存了A的Session Cookie
2. 用户在不退出A的情况下访问恶意网站B
3. 网站B的页面包含自动向A发起请求的代码（如隐藏表单、img标签）
4. 浏览器自动附带A的Cookie，A认为是用户正常操作
5. 用户在不知情的情况下执行了转账等操作

**CSRF攻击条件：**
- 目标网站基于Cookie进行身份认证
- 攻击者知道请求的URL和参数格式
- 用户已登录目标网站且未退出

**CSRF防御措施：**

1. **CSRF Token**：服务器生成随机Token嵌入表单，提交时验证Token。攻击者无法获取Token（受同源策略保护）。这是最可靠的防御方法。

2. **SameSite Cookie属性**：限制Cookie在跨站请求中的发送
   - SameSite=Strict：完全不发送（过于严格，影响正常导航）
   - SameSite=Lax：仅在顶级导航的GET请求中发送（推荐默认值）
   - SameSite=None：跨站发送（需配合Secure属性）

3. **双重Cookie验证**：JavaScript从Cookie读取Token，放入请求头，服务器验证Cookie和请求头中的Token是否一致。

4. **验证Referer/Origin头**：检查请求来源是否为可信域名（可被某些环境剥离，不可单独依赖）。

## 关键结论

- CSRF利用的是浏览器自动发送Cookie的机制，而非XSS那样的代码注入
- SameSite=Lax是现代浏览器的默认Cookie策略，有效缓解CSRF
- GET请求不应执行状态变更操作（应使用POST/PUT/DELETE）
- CSRF Token应与用户会话绑定，每次请求后更新
- CSRF和XSS可以组合利用：XSS可以窃取CSRF Token，因此必须同时防御两者

## 易错点

1. 混淆CSRF和XSS：XSS注入恶意脚本执行，CSRF利用已认证状态伪造请求。XSS可以在客户端执行任意操作，CSRF只能发送预定义的请求
2. 忽略JSON API的CSRF：即使使用JSON格式，如果基于Cookie认证且允许简单请求（Content-Type: application/x-www-form-urlencoded），仍存在CSRF风险
3. 误认为验证码能完全防CSRF：验证码可以缓解但不能完全防御，且影响用户体验

## 例题

**题目：** 银行网站有一个转账接口：POST /transfer，参数为to_account和amount。(1) 设计一个CSRF攻击页面；(2) 解释为什么CSRF Token能防御此攻击；(3) 如果应用使用JWT（Authorization头）而非Cookie进行认证，是否还存在CSRF风险？

**解答：**
(1) CSRF攻击页面：
```html
<html>
<body onload="document.getElementById('csrf-form').submit()">
  <form id="csrf-form" action="https://bank.com/transfer" method="POST">
    <input type="hidden" name="to_account" value="attacker_account">
    <input type="hidden" name="amount" value="10000">
  </form>
</body>
</html>
```
用户访问此页面时，表单自动提交，浏览器附带银行网站的Cookie，完成转账。也可以使用img标签：`<img src="https://bank.com/transfer?to=attacker&amount=10000">`
(2) CSRF Token防御原理：①服务器在表单中嵌入随机Token（如<input name="csrf_token" value="随机值">）；②Token存储在用户Session中；③提交时服务器验证Token是否匹配；④攻击者无法获取Token，因为同源策略阻止恶意网站读取银行网站的页面内容；⑤没有有效Token的请求被拒绝。
(3) 使用JWT + Authorization头不存在传统CSRF风险。原因：①JWT通过Authorization头发送，不是Cookie，浏览器不会自动附加；②恶意网站的JavaScript无法读取JWT（同源策略保护）；③恶意网站无法设置Authorization头（跨域请求需要CORS预检）。但如果JWT存储在localStorage中，可能受XSS攻击窃取，因此仍需防御XSS。

## 关联页面

[[跨站脚本攻击XSS]] [[SQL注入攻击与防御]] [[会话安全与Cookie安全]] [[OWASP Top 10]]
