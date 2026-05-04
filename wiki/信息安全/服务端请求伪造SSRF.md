---
title: 服务端请求伪造SSRF
course: 信息安全
chapter: Web应用安全
difficulty: INTERMEDIATE
tags: [SSRF, 服务端请求伪造, 内网探测, Web安全]
aliases: [Server-Side Request Forgery, SSRF, Blind SSRF]
source:
  - OWASP SSRF Prevention Cheat Sheet
  - CWE-918 (Server-Side Request Forgery)
updated_at: 2026-05-03
---

## 核心定义

服务端请求伪造（Server-Side Request Forgery, SSRF）是一种攻击者诱导服务器向非预期的目标发起HTTP请求的漏洞。SSRF是OWASP Top 10 2021新增的风险类别（A10），随着云环境和微服务架构的普及而日益重要。

**SSRF攻击原理：** Web应用接受用户提供的URL参数，服务器端发起请求获取内容。攻击者将URL修改为内网地址或云服务元数据地址，服务器以自身权限发起请求，绕过网络访问控制。

**SSRF攻击目标：**
1. **内网探测**：扫描内网主机和端口（如http://192.168.1.1:8080）
2. **云元数据服务**：访问云平台元数据API（如http://169.254.169.254/latest/meta-data/），获取IAM凭证、实例信息
3. **本地文件读取**：使用file://协议读取服务器本地文件（如file:///etc/passwd）
4. **攻击内部服务**：向内部Redis、Elasticsearch等服务发送恶意命令
5. **端口扫描**：通过响应时间或错误信息推断端口状态

**SSRF绕过技术：**
- IP地址表示：十进制（2130706433=127.0.0.1）、十六进制（0x7f000001）、八进制（0177.0.0.1）
- DNS重绑定：第一次解析返回允许的IP，第二次解析返回内网IP
- URL解析差异：利用不同语言URL解析库的差异
- 重定向：先访问外部URL，重定向到内网地址

**SSRF防御措施：**
- URL白名单验证（协议、域名、端口、路径）
- 禁止请求内网IP地址（包括127.0.0.0/8、10.0.0.0/8、172.16.0.0/12、192.168.0.0/16）
- 禁用不必要的URL协议（file://、gopher://、dict://）
- 使用DNS解析验证（解析后检查IP是否为内网）
- 限制响应内容和超时时间
- 云环境禁用元数据服务或使用IMDSv2（需要Token认证）

## 关键结论

- SSRF在云环境中尤其危险，可获取IAM凭证导致整个云环境被入侵
- AWS IMDSv2要求Token认证，有效防御SSRF窃取元数据
- DNS重绑定可以绕过基于IP的防护，需要在DNS解析后再次验证IP
- 限制服务器的出站流量是防御SSRF的有效补充措施
- SSRF常与其他漏洞组合利用（如结合Redis未授权访问执行命令）

## 易错点

1. 仅验证域名不验证IP：域名可以解析到内网IP，必须在DNS解析后验证实际IP地址
2. 忽略重定向绕过：外部URL可以重定向到内网，需要限制重定向次数或禁止重定向
3. 忽略协议多样性：除了HTTP/HTTPS，file://、gopher://、dict://都可以用于SSRF攻击

## 例题

**题目：** 某Web应用有图片预览功能，URL格式为：/preview?url=http://example.com/image.jpg。服务器从该URL下载图片并返回。(1) 分析SSRF攻击场景；(2) 构造一个读取AWS元数据的payload；(3) 设计防御方案。

**解答：**
(1) SSRF攻击场景：
①内网探测：/preview?url=http://192.168.1.1:8080，通过响应判断内网主机存活；
②端口扫描：/preview?url=http://127.0.0.1:3306，通过响应时间判断MySQL是否运行；
③云元数据：/preview?url=http://169.254.169.254/latest/meta-data/，获取实例凭证；
④文件读取：/preview?url=file:///etc/passwd，读取服务器敏感文件；
⑤攻击内部服务：/preview?url=gopher://127.0.0.1:6379/_SET%20key%20value，向Redis发送命令。
(2) AWS元数据读取payload：/preview?url=http://169.254.169.254/latest/meta-data/iam/security-credentials/。获取IAM角色名称后，请求该角色的临时凭证（AccessKeyId、SecretAccessKey、Token）。
(3) 防御方案：
①URL白名单：只允许特定域名（如cdn.example.com）；
②协议限制：只允许http://和https://；
③内网IP过滤：DNS解析后检查IP，拒绝127.0.0.0/8、10.0.0.0/8、172.16.0.0/12、192.168.0.0/16、169.254.0.0/16；
④禁用重定向或限制重定向目标；
⑤使用专用网络请求服务（不在Web应用进程内发起请求）；
⑥云环境使用IMDSv2（需要Token认证元数据服务）。

## 关联页面

[[OWASP Top 10]] [[SQL注入攻击与防御]] [[云安全架构]] [[防火墙技术]]
