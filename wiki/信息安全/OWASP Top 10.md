---
title: OWASP Top 10
course: 信息安全
chapter: Web应用安全
difficulty: BASIC
tags: [OWASP, Web安全, Top 10, 安全风险]
aliases: [OWASP Top 10, OWASP Top Ten, Web Application Security Risks]
source:
  - OWASP Top 10 2021
  - OWASP Testing Guide v4
updated_at: 2026-05-03
---

## 核心定义

OWASP Top 10是由开放式Web应用安全项目（OWASP, Open Web Application Security Project）发布的Web应用最关键安全风险清单，是Web安全领域最权威的参考标准。OWASP Top 10基于全球真实漏洞数据统计，每4年更新一次。2021版十大风险如下：

**A01:2021 访问控制失效（Broken Access Control）**：用户能够访问超出其权限的功能或数据。如越权访问（IDOR）、权限提升、目录遍历。从2017版第五位升至第一位，说明其普遍性和严重性。

**A02:2021 加密机制失效（Cryptographic Failures）**：敏感数据因加密不足或未加密而泄露。包括使用弱加密算法、密钥管理不当、明文传输等。原名"敏感数据泄露"。

**A03:2021 注入（Injection）**：用户输入被解释为代码执行。包括SQL注入、NoSQL注入、OS命令注入、LDAP注入等。XSS从注入中分离，单独列为A07。

**A04:2021 不安全设计（Insecure Design）**：应用程序架构和设计层面的安全缺陷，无法通过实现修复。强调威胁建模和安全设计的重要性。

**A05:2021 安全配置错误（Security Misconfiguration）**：应用程序、框架、服务器的安全配置不当。包括默认凭证、不必要的功能启用、错误信息泄露等。

**A06:2021 过时或有漏洞的组件（Vulnerable and Outdated Components）**：使用已知存在漏洞的第三方库或组件。

**A07:2021 身份识别和认证失败（Identification and Authentication Failures）**：认证机制薄弱或缺失。包括弱密码策略、暴力破解无防护、会话管理缺陷等。

**A08:2021 软件和数据完整性故障（Software and Data Integrity Failures）**：CI/CD管道缺乏完整性验证、不安全的反序列化。

**A09:2021 安全日志和监控失败（Security Logging and Monitoring Failures）**：安全事件未被记录或监控不足，导致攻击无法被检测。

**A10:2021 服务端请求伪造（Server-Side Request Forgery, SSRF）**：攻击者诱导服务器向非预期的目标发起请求。

## 关键结论

- 访问控制失效连续多年位列第一，是最普遍的Web安全风险
- OWASP Top 10是安全基线而非完整清单，实际风险可能更多
- 不安全设计是2021版新增类别，强调安全左移（Shift Left）
- SSRF是2021版新增类别，随着云环境普及而日益重要
- OWASP Top 10应作为安全培训、代码审计和渗透测试的基础参考

## 易错点

1. 误认为OWASP Top 10是完整的安全清单：它只是最常见风险的统计排名，不代表所有可能的安全问题
2. 忽略不安全设计：很多安全问题源于设计阶段，仅靠代码审计无法发现
3. 只关注技术漏洞而忽视配置错误：安全配置错误是最容易预防但最常被忽视的风险

## 例题

**题目：** 某Web应用在安全评估中发现以下问题，请对应OWASP Top 10分类：(1) 管理员页面可被普通用户直接访问；(2) 数据库密码以明文存储在配置文件中；(3) 系统使用存在已知漏洞的Apache Struts版本。

**解答：**
(1) A01:2021 访问控制失效——普通用户能够访问管理员功能，属于越权访问（水平或垂直越权）。修复：实施服务端权限验证，每个请求检查用户角色和权限；使用RBAC/ABAC模型管理访问控制。
(2) A02:2021 加密机制失效——密码明文存储，一旦配置文件泄露将暴露数据库凭证。修复：使用环境变量或密钥管理服务（如HashiCorp Vault）存储敏感配置；密码使用强哈希存储；配置文件权限限制为600。
(3) A06:2021 过时或有漏洞的组件——Apache Struts存在已知RCE漏洞（如S2-045 CVE-2017-5638）。修复：及时更新组件到最新安全版本；使用软件成分分析（SCA）工具持续监控依赖漏洞；建立漏洞响应流程。

## 关联页面

[[SQL注入攻击与防御]] [[跨站脚本攻击XSS]] [[跨站请求伪造CSRF]] [[服务端请求伪造SSRF]]
