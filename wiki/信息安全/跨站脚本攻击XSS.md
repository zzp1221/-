---
title: 跨站脚本攻击XSS
course: 信息安全
chapter: Web应用安全
difficulty: INTERMEDIATE
tags: [XSS, 跨站脚本, DOM, Web安全, 内容安全策略]
aliases: [Cross-Site Scripting, XSS, Reflected XSS, Stored XSS, DOM-based XSS]
source:
  - OWASP XSS Prevention Cheat Sheet
  - OWASP Testing Guide v4
  - CWE-79 (Cross-site Scripting)
updated_at: 2026-05-03
---

## 核心定义

跨站脚本攻击（Cross-Site Scripting, XSS）是一种代码注入攻击，攻击者将恶意脚本（通常是JavaScript）注入到Web页面中，在其他用户的浏览器中执行。XSS是最常见的Web安全漏洞之一，可导致会话劫持、钓鱼攻击、页面篡改等后果。

**XSS的类型：**

1. **反射型XSS（Reflected XSS）**：恶意脚本通过URL参数注入，服务器将未过滤的参数直接嵌入HTML响应中。攻击需要用户点击恶意链接。示例：搜索功能将搜索词直接嵌入页面。

2. **存储型XSS（Stored XSS）**：恶意脚本永久存储在服务器（如数据库），当其他用户访问包含恶意脚本的页面时触发。影响范围最广，因为不需要诱导用户点击特定链接。示例：论坛帖子、评论区注入脚本。

3. **DOM型XSS（DOM-based XSS）**：漏洞存在于前端JavaScript代码中，恶意脚本通过DOM操作注入，不经过服务器。示例：JavaScript从URL取值直接写入innerHTML。

**XSS攻击的危害：**
- **会话劫持**：窃取Cookie中的Session ID，冒充用户身份
- **钓鱼攻击**：伪造登录表单，诱导用户输入凭证
- **页面篡改**：修改页面内容，显示虚假信息
- **键盘记录**：监听用户键盘输入，窃取敏感信息
- **蠕虫传播**：利用XSS自动传播（如Samy蠕虫）

**XSS防御措施：**
- **输出编码**：根据输出上下文（HTML、JavaScript、URL、CSS）使用正确的编码
- **Content Security Policy（CSP）**：限制页面可以加载和执行的脚本来源
- **输入验证**：对用户输入进行白名单验证
- **HttpOnly Cookie**：防止JavaScript访问敏感Cookie

## 关键结论

- 输出编码是防御XSS的最根本方法，编码必须匹配输出上下文
- CSP是防御XSS的有效补充，但不能替代输出编码
- DOM型XSS完全在客户端，服务器端防护无效，需要前端代码审查
- HttpOnly标志可以防止XSS窃取Cookie，但不能阻止XSS的其他危害
- 现代框架（React、Vue）默认对输出进行编码，但dangerouslySetInnerHTML等API会绕过保护

## 易错点

1. 仅依赖输入过滤防御XSS：输入过滤容易被绕过（如使用HTML实体编码、Unicode转义），必须在输出时编码
2. 忽略DOM型XSS：传统WAF和服务器端防护无法检测DOM型XSS，需要前端代码审计
3. 误认为HTTPS能防XSS：HTTPS只保护传输层安全，不防范应用层XSS攻击

## 例题

**题目：** 以下HTML页面存在XSS漏洞：
```html
<input type="text" id="search">
<div id="results"></div>
<script>
  var query = new URLSearchParams(window.location.search).get('q');
  document.getElementById('results').innerHTML = '搜索结果: ' + query;
</script>
```
(1) 这是什么类型的XSS？(2) 构造一个攻击payload；(3) 给出修复方案。

**解答：**
(1) 这是DOM型XSS。漏洞存在于前端JavaScript代码中：从URL参数取值（q参数），直接写入innerHTML，不经过服务器。攻击完全在客户端完成。
(2) 攻击payload：
```
http://example.com/search?q=<img src=x onerror=alert(document.cookie)>
```
当用户访问此URL时，浏览器解析HTML，img标签加载失败触发onerror事件，执行alert(document.cookie)窃取Cookie。更隐蔽的攻击可以将Cookie外传到攻击者服务器。
(3) 修复方案：
① 使用textContent替代innerHTML（最简单有效）：
```javascript
document.getElementById('results').textContent = '搜索结果: ' + query;
```
② 如果必须使用innerHTML，先进行HTML编码：
```javascript
function encodeHTML(str) {
  return str.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}
document.getElementById('results').innerHTML = '搜索结果: ' + encodeHTML(query);
```
③ 配置CSP头，限制脚本来源，禁止内联脚本；
④ 设置Cookie的HttpOnly标志，防止JavaScript访问。

## 关联页面

[[SQL注入攻击与防御]] [[跨站请求伪造CSRF]] [[OWASP Top 10]] [[会话安全与Cookie安全]]
