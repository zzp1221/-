---
title: 安全开发生命周期SDL
course: 信息安全
chapter: 安全治理与工程
difficulty: INTERMEDIATE
tags: [SDL, 安全开发, DevSecOps, 威胁建模, 代码审计]
aliases: [Security Development Lifecycle, SDL, DevSecOps, Secure SDLC]
source:
  - Microsoft Security Development Lifecycle (SDL)
  - OWASP SAMM (Software Assurance Maturity Model)
  - NIST SP 800-218 (SSDF)
updated_at: 2026-05-03
---

## 核心定义

安全开发生命周期（Security Development Lifecycle, SDL）是将安全活动集成到软件开发各个阶段的系统化方法。SDL的核心理念是"安全左移"（Shift Left Security），在开发早期发现和修复安全问题，比在部署后修复成本低100倍以上。

**Microsoft SDL的七个阶段：**

1. **培训（Training）**：开发团队接受安全培训，了解常见漏洞和安全编码实践
2. **需求（Requirements）**：定义安全需求和隐私需求，建立安全质量门（Quality Gates）
3. **设计（Design）**：进行威胁建模（Threat Modeling），分析攻击面，设计安全架构
4. **实现（Implementation）**：使用安全编码标准，禁用不安全函数（如C的strcpy→strncpy），代码审查
5. **验证（Verification）**：静态应用安全测试（SAST）、动态应用安全测试（DAST）、模糊测试（Fuzzing）
6. **发布（Release）**：安全审查，事件响应计划就绪
7. **响应（Response）**：安全事件响应，漏洞修复和更新

**威胁建模（Threat Modeling）：** STRIDE模型是微软提出的威胁分类框架：
- **S**poofing（欺骗）→ 身份认证威胁
- **T**ampering（篡改）→ 完整性威胁
- **R**epudiation（否认）→ 不可否认性威胁
- **I**nformation Disclosure（信息泄露）→ 机密性威胁
- **D**enial of Service（拒绝服务）→ 可用性威胁
- **E**levation of Privilege（权限提升）→ 授权威胁

**DevSecOps** 将安全集成到CI/CD管道中：
- 代码提交时：SAST扫描（如SonarQube、Semgrep）
- 构建时：SCA扫描（如Snyk、Dependabot检查依赖漏洞）
- 部署前：DAST扫描（如OWASP ZAP）
- 运行时：RASP（运行时应用自我保护）

## 关键结论

- SDL的核心价值是"安全左移"，早期发现漏洞成本最低
- 威胁建模是SDL中最重要的安全活动，应在设计阶段进行
- SAST和DAST互补：SAST在编码阶段发现漏洞，DAST在运行时发现漏洞
- DevSecOps将安全自动化集成到CI/CD管道，实现持续安全
- OWASP SAMM提供安全开发成熟度评估框架

## 易错点

1. 忽略威胁建模：很多团队跳过威胁建模直接编码，导致设计层面的安全缺陷
2. 只依赖自动化工具：SAST/DAST有误报和漏报，人工代码审查和渗透测试不可替代
3. 忽略第三方组件安全：现代软件大量使用开源库，SCA（软件成分分析）必须纳入SDL

## 例题

**题目：** 某团队开发一个在线支付系统。(1) 在设计阶段如何进行威胁建模？(2) 在编码阶段应遵循哪些安全编码实践？(3) 如何在CI/CD管道中集成安全检查？

**解答：**
(1) 威胁建模过程：
①绘制数据流图（DFD）：识别外部实体（用户、支付网关）、处理过程（Web服务器、支付服务）、数据存储（订单库、用户库）、数据流
②使用STRIDE分析每个组件：
- 欺骗：用户身份是否可被伪造？→ 实施MFA
- 篡改：支付金额是否可被修改？→ 数字签名
- 否认：用户是否可否认交易？→ 审计日志
- 信息泄露：支付数据是否加密传输？→ TLS
- 拒绝服务：支付接口是否有频率限制？→ 限流
- 权限提升：普通用户能否调用管理接口？→ 权限验证
③制定安全需求和缓解措施
(2) 安全编码实践：
①输入验证：所有用户输入进行白名单验证
②输出编码：根据输出上下文进行正确编码
③参数化查询：防止SQL注入
④密码安全：使用bcrypt/Argon2存储密码
⑤会话管理：登录后更换Session ID
⑥错误处理：不暴露堆栈信息和系统细节
⑦日志记录：记录安全相关事件
(3) CI/CD安全集成：
①代码提交：pre-commit hooks运行SAST（Semgrep）
②构建阶段：SCA检查依赖漏洞（Snyk），镜像扫描（Trivy）
③测试阶段：SAST全面扫描（SonarQube），DAST扫描（OWASP ZAP）
④部署阶段：配置检查（kube-bench），密钥扫描（git-secrets）
⑤运行时：WAF防护，RASP保护

## 关联页面

[[OWASP Top 10]] [[渗透测试方法论]] [[SQL注入攻击与防御]] [[缓冲区溢出攻击与防御]]
