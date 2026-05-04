---
title: SQL注入攻击与防御
course: 信息安全
chapter: Web应用安全
difficulty: INTERMEDIATE
tags: [SQL注入, 注入攻击, Web安全, 数据库安全]
aliases: [SQL Injection, SQLi, Blind SQL Injection, Second Order SQLi]
source:
  - OWASP SQL Injection Prevention Cheat Sheet
  - OWASP Testing Guide v4
  - CWE-89 (SQL Injection)
updated_at: 2026-05-03
---

## 核心定义

SQL注入（SQL Injection）是针对Web应用程序的代码注入攻击，攻击者通过在用户输入中插入恶意SQL语句，欺骗后端数据库执行非预期的SQL命令。SQL注入可导致数据泄露、数据篡改、身份绕过甚至远程代码执行，是Web应用最严重的安全漏洞之一。

**SQL注入的类型：**

1. **带内注入（In-band SQLi）**：攻击结果直接在HTTP响应中显示
   - **基于错误的注入**：利用数据库错误信息获取数据（如' UNION SELECT...）
   - **基于联合查询的注入**：使用UNION SELECT合并攻击者查询结果

2. **盲注（Blind SQLi）**：攻击结果不直接显示，需要通过间接方式获取
   - **基于布尔的盲注**：通过页面返回的True/False推断数据
   - **基于时间的盲注**：通过响应延迟推断数据（如IF(1=1, SLEEP(5), 0)）

3. **带外注入（Out-of-band SQLi）**：通过DNS请求或HTTP请求将数据外传（如Oracle的UTL_HTTP）

4. **二次注入（Second Order SQLi）**：恶意数据先存储在数据库中，后续使用时触发注入

**SQL注入示例：**
```
原始查询：SELECT * FROM users WHERE username='$user' AND password='$pass'
攻击输入：user = admin' --，pass = 任意值
实际查询：SELECT * FROM users WHERE username='admin' --' AND password='任意值'
结果：跳过密码验证，以admin身份登录
```

## 关键结论

- 参数化查询（预编译语句）是防御SQL注入的最有效方法，绝对不应拼接SQL语句
- 输入验证是辅助防御手段，不能单独依赖（黑名单过滤容易被绕过）
- 最小权限原则：数据库账户只授予必要的权限，禁止使用DBA权限
- ORM框架不能完全防止SQL注入，动态查询拼接仍可能引入漏洞
- WAF可以作为额外防护层，但不能替代代码级修复

## 易错点

1. 误认为存储过程能防止SQL注入：存储过程内部如果动态拼接SQL，仍然存在注入风险
2. 依赖黑名单过滤：攻击者可使用编码（URL编码、Unicode）、注释符、大小写变换绕过过滤
3. 忽略二次注入：数据存储时过滤但使用时不过滤，仍可能被利用

## 例题

**题目：** 以下PHP代码存在SQL注入漏洞：
```php
$username = $_POST['username'];
$password = $_POST['password'];
$sql = "SELECT * FROM users WHERE username='$username' AND password='$password'";
$result = mysql_query($sql);
```
(1) 指出漏洞所在；(2) 给出至少两种SQL注入攻击payload；(3) 给出修复方案。

**解答：**
(1) 漏洞在于直接将用户输入拼接到SQL语句中，没有进行任何过滤或参数化处理。
(2) 攻击payload：
① 绕过登录：username = admin' --，password = 任意值。效果：注释掉密码验证部分。
② 万能密码：username = ' OR '1'='1，password = ' OR '1'='1。效果：条件永远为真，匹配所有用户。
③ UNION注入获取数据：username = ' UNION SELECT 1,username,password,4 FROM users --。效果：返回所有用户密码。
④ 基于时间的盲注：username = ' AND IF(SUBSTRING((SELECT password FROM users LIMIT 1),1,1)='a', SLEEP(5), 0) --。效果：通过响应延迟推断密码首字母。
(3) 修复方案：
① 使用参数化查询（预编译语句）：
```php
$stmt = $pdo->prepare("SELECT * FROM users WHERE username=? AND password=?");
$stmt->execute([$username, $password]);
```
② 使用ORM框架（如Doctrine、Eloquent）；
③ 输入验证：用户名只允许字母数字；
④ 最小权限：数据库连接账户只授予SELECT权限；
⑤ 错误信息不暴露数据库细节（使用自定义错误页面）。

## 关联页面

[[跨站脚本攻击XSS]] [[跨站请求伪造CSRF]] [[OWASP Top 10]] [[会话安全与Cookie安全]]
