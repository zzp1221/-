---
title: "数据库安全与SQL注入防御"
course: 数据库原理
chapter: 安全
difficulty: INTERMEDIATE
tags: [数据库, 安全, SQL注入, 访问控制, 加密]
aliases: [Database Security, SQL Injection Defense, Access Control]
source: "OWASP Top Ten; SQL标准ISO/IEC 9075; PostgreSQL安全管理文档; Bell-La Padula模型"
updated_at: 2026-05-02
---

## 核心定义

数据库安全层次：1.)访问控制(GRANT/REVOKE——基于角色的访问控制RBAC) 2.)行级安全(RLS/Row-Level Security——基于用户属性的过滤条件自动附加到查询) 3.)数据加密(透明数据加密TDE——加密文件/表空间——后丢失密钥数据永久不可用) 4.)加密传输(TLS between client and DB server) 5.)审计日志(audit——记录所有敏感查询的who/when/what)。SQL注入是OWASP #1:注入攻击——不信任的输入直接拼接SQL字符串导致攻击者任意执行SQL。

## 注入防御

SQL注入防御的黄金法则：1.)永远参数化查询(prepared statement——?占位符,将查询编译阶段与参数绑定阶段分离,防止SQL语法注入) 2.)输入验证(严格的类型和格式验证——白名单,黑名单不够) 3.)最小权限原则(应用程序的数据库账户仅拥有必需的权限) 4.)ORM的正确使用(虽然使用ORM也不能完全免疫注入——对native SQL查询仍要参数化)。存储过程调用也需要参数化。二阶SQL注入——攻击数据首先存储在数据库中(looks clean),随后被其他查询读取和执行——需全部数据始终参数化(不使用拼接)。

## 关键结论

1. 永远不要信任输入——always parameterize 2. 数据库应用账户绝不应是owner(db_owner)账户 3. WAF(Web Application Firewall)可以检测注入攻击特征但不保证全面防御 4. 信息安全标准(PCI DSS/HIPAA/GDPR)要求对数据库中的PII加密或假名化 5. 安全扫描(静态分析/动态测试/渗透测试)应定期进行

## 关联知识点

[[数据库原理-查询优化器深度]] [[信息安全-SQL注入与XSS防御]] [[信息安全-访问控制与身份认证]]
