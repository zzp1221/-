---
title: SQL数据控制语言DCL
course: 数据库原理
chapter: SQL
difficulty: BASIC
tags: [SQL, DCL, GRANT, REVOKE, 权限管理, 角色]
aliases: [Data Control Language, GRANT, REVOKE, Privileges, Roles]
source:
  - 王珊《数据库系统概论》第5版
updated_at: 2026-05-02

---

## 核心定义

DCL（Data Control Language，数据控制语言）是SQL中用于管理数据库用户权限和访问控制的语句集合。DCL的核心命令是GRANT（授予权限）和REVOKE（撤销权限）。权限（Privilege）是对特定数据库对象（表、视图、存储过程等）执行特定操作（SELECT、INSERT、UPDATE、DELETE、EXECUTE等）的授权许可。SQL权限分为系统权限（创建表、创建用户、备份数据库等数据库级别的操作）和对象权限（对具体表/视图/列的数据操作权限）。可以通过角色（Role）一组权限的命名集合来简化权限管理——将权限授予角色，再将角色授予用户。DCL实现了数据库的自主访问控制（Discretionary Access Control, DAC），是数据库多用户环境安全体系的基础层。

## 关键结论

- GRANT语法：GRANT privilege_list ON object TO user_or_role [WITH GRANT OPTION]。privilege_list 可以是ALL PRIVILEGES（所有权限）、SELECT/INSERT/UPDATE/DELETE/USAGE等列表。ON object可以指定表名、视图名、数据库名.*（库中的所有对象）或*.*（全局所有对象）。WITH GRANT OPTION允许被授权者将权限再次授予其他用户
- REVOKE语法：REVOKE privilege_list ON object FROM user_or_role [RESTRICT|CASCADE]。RESTRICT模式——如果被撤销权限的用户曾将此权限授予他人，拒绝撤销；CASCADE模式——级联撤销，从被授权用户及所有其授予链上的所有用户一并撤销
- 角色的管理：CREATE ROLE role_name（创建角色）；GRANT privilege ON object TO role_name（将权限授予角色）；GRANT role_name TO user_name（将角色授予用户）。修改角色权限后，拥有该角色的所有用户自动继承变更。角色可嵌套（角色授予另一个角色形成角色层级）
- 权限的常见类型：SELECT（查询数据）、INSERT（插入行）、UPDATE（更新列值——可在特定列范围限制）、DELETE（删除行）、REFERENCES（定义外键约束引用此表）、INDEX（在表上创建索引）、EXECUTE（执行存储过程/函数）、USAGE（使用sequence、特定模式对象等）、ALL PRIVILEGES（该对象上的所有权限集合）
- 权限信息的存储：DBMS在数据字典中维护权限表（MySQL是mysql.user, mysql.db, mysql.tables_priv, mysql.columns_priv等）。通过查询information_schema.user_privileges等视图查看当前用户权限

## 易错点

1. **GRANT ALL不等于DBA权限**：GRANT ALL PRIVILEGES ON db.table TO user仅授予该表上的所有对象操作权限，不包括创建表、创建用户、SHUTDOWN等系统级管理权限。系统权限(SYSTEM PRIVILEGE)需要通过特定DBMS的语法单独授给。

2. **REVOKE的级联效应**：如果用户A授予用户B权限，用户B又授予用户C，当A撤销B的权限时(CASCADE模式下)C的权限也随之被撤销。这可能导致连锁反应——自动化管理脚本需要注意依赖链上的其他授权。

3. **权限和视图的关系**：为用户创建特定视图并只授予该视图的SELECT权限（不给原表权限）是实现列级和行级权限管理的常用方式。但是该视图必须要有原表的相同授权（且视图的所有者也需有表权限）—— 即通过视图链实现更细粒度的访问控制的中间件方案。

4. **MySQL的特权系统刷新**：使用GRANT/REVOKE后权限自动生效（内存中变更），但直接修改mysql.*表后需执行FLUSH PRIVILEGES才能生效——不推荐直接改表。此特定行为是MySQL独特机制。

## 例题

**例题1**：写出SQL语句实现：(1)授予用户u1对Student表的SELECT、INSERT权限，并允许其将该权限授予他人。(2)撤销u1对Student表的INSERT权限，级联撤销所有经u1获得的该权限的用户。

**解答**：
```sql
-- (1) 授予带管理选项
GRANT SELECT, INSERT ON Student TO u1 WITH GRANT OPTION;

-- (2) 级联撤销
REVOKE INSERT ON Student FROM u1 CASCADE;
-- (注意：MySQL中用REVOKE自动CASCADE，不支持RESTRICT语法)
```

**例题2**：创建角色reporter，授予对所有表的只读和创建视图权限。将u2、u3用户加入该角色。当需要收回所有人报表权限时如何操作最有效率？

**解答思路**：
```sql
CREATE ROLE reporter;
GRANT SELECT ON database_name.* TO reporter;
GRANT CREATE VIEW ON database_name.* TO reporter;
GRANT reporter TO u2, u3;

-- 需要撤销所有人报表权限时，只需撤销角色权限或删除该角色
REVOKE SELECT, CREATE VIEW ON database_name.* FROM reporter;
-- 或直接删除角色
DROP ROLE reporter;  -- 拥有该角色的用户的权限自动被撤销
```
角色方法显著简化了权限管理——无需逐用户执行REVOKE。

## 关联页面

[[SQL-视图]] [[安全性]] [[完整性约束]]
