---
title: SQL数据定义语言DDL
course: 数据库原理
chapter: SQL
difficulty: BASIC
tags: [SQL, DDL, CREATE, ALTER, DROP, 数据定义, 表结构]
aliases: [Data Definition Language, CREATE TABLE, ALTER TABLE, DROP TABLE]
source:
  - 王珊《数据库系统概论》第5版
updated_at: 2026-05-02

---

## 核心定义

DDL（Data Definition Language，数据定义语言）是SQL语言中用于定义、修改和删除数据库对象（表、视图、索引、存储过程、触发器等）的语句集合。DDL的核心操作是CREATE（创建对象）、ALTER（修改对象结构）和DROP（删除对象）。DDL语句直接影响到数据库的模式（Schema），执行后通常会隐式提交事务（无法回滚，在多数DBMS中——MySQL的DDL从5.6开始支持部分原子DDL）。DDL定义的对象中最重要的就是表（TABLE），表定义包括：列名、列的数据类型（如INT、VARCHAR(n)、DATE、DECIMAL(p,s)等）、列级和表级完整性约束（PRIMARY KEY、FOREIGN KEY、UNIQUE、NOT NULL、CHECK、DEFAULT）。除基本表外，DDL还负责定义视图（VIEW，虚表）、索引（INDEX，加速检索的物理存取路径）和模式（SCHEMA，数据库对象的命名空间）。

## 关键结论

- CREATE TABLE定义基本表结构：CREATE TABLE table_name (col1 datatype [约束1 约束2...]，col2 datatype，...，[表级约束]，...)。列级约束直接写在列定义后面；表级约束独立写在所有列定义之后并可涵盖多个列（如复合主键、复合外键、跨列CHECK（部分DBMS支持））
- 常用SQL数据类型：CHAR(n)（定长字符串）、VARCHAR(n)（变长字符串，最大字符限制）、INT/BIGINT/SMALLINT（有符号整数，按存储字节数）、DECIMAL/NUMERIC(p,s)（精度p位定点小数，s位小数）、FLOAT/REAL/DOUBLE（近似浮点数）、DATE/TIME/TIMESTAMP（日期/时间/时间戳）、BOOLEAN（布尔）、TEXT/BLOB（大文本/二进制大对象）。各DBMS数据类型存在差异——需参考具体DBMS文档
- ALTER TABLE修改已有表结构：ADD COLUMN（新增列）、DROP COLUMN（删除列）、MODIFY/ALTER COLUMN（修改列的数据类型或约束）、ADD/DROP CONSTRAINT（增加/删除约束）、RENAME TO（重命名表）。注意：删除列需要该列无其他对象（视图、索引、触发器等）依赖
- DROP TABLE table_name [CASCADE|RESTRICT]：删除表的定义及表中所有数据。CASCADE表示级联删除基于此表的视图和约束；RESTRICT表示如果该表被其他对象引用则拒绝删除（默认通常为RESTRICT）
- 模式SCHEMA的管理：CREATE SCHEMA schema_name [AUTHORIZATION user]（创建模式并设定所有者）。在MySQL中SCHEMA与DATABASE同义（CREATE DATABASE即创建模式，MySQL没有单独的SCHEMA对象）

## 易错点

1. **DDL的自动提交特性**：多数DBMS中DDL语句会隐式提交当前事务（即使写在了事务中也会在DDL执行前自动COMMIT先前的DML操作），然后独立事务执行DDL再立刻自动提交——此后的ROLLBACK无法回滚DDL修改的表结构。设计应用程序时需注意这一行为。

2. **ALTER MODIFY COLUMN的危险操作**：修改列的数据类型时，如果已有数据无法无损转换为新类型，将导致数据截断或报错。在包含数百万行的大表上进行ALTER TABLE操作可能锁定全表极长时间（在MySQL 5.6前ALTER TABLE使用表拷贝+替换方式极大影响性能；MySQL 5.6+支持Online DDL但仍有若干操作限制）。

3. **DROP TABLE与DELETE FROM的区别**：DROP删除表定义和所有数据行（表结构不复存在）；DELETE FROM删除所有数据但保留表结构（表仍存在只是空表）。DELETE是DML（可以被回滚），DROP是DDL（通常不可回滚）。

4. **DEFAULT值只在插入时有效**：ALTER TABLE设置列的默认值不会影响表中已存在的行——旧行该列保持原值不变。新增列时若设置了DEFAULT，旧行的该列会被填充为默认值或NULL（取决于DBMS和是否指定NOT NULL）。很多人误以为加DEFAULT后历史数据会自动填充。

## 例题

**例题1**：定义一个包含完整性约束的学生表Student(sno, sname, ssex, sage, sdept)，并满足：(1)sno为主键；(2)sname不允许为空；(3)ssex只能是'男'或'女'；(4)sage在10-60之间；(5)sdept默认值为'计算机系'。

**解答**：
```sql
CREATE TABLE Student (
    sno   CHAR(8) PRIMARY KEY,
    sname VARCHAR(20) NOT NULL,
    ssex  CHAR(2) CHECK (ssex IN ('男', '女')),
    sage  INT CHECK (sage BETWEEN 10 AND 60),
    sdept VARCHAR(20) DEFAULT '计算机系'
);
```

**例题2**：现有一个大型表Orders(order_id, customer_id, order_date, amount)，需要新增加列status（订单状态VARCHAR(20)，默认为'处理中'）。写出DDL语句，指出应该考虑的性能影响。

**解答思路**：ALTER TABLE Orders ADD COLUMN status VARCHAR(20) DEFAULT '处理中'。注意：在MySQL 5.6及之前的版本中，添加带默认值的列会导致全表拷贝重建（因为每一行都要写入默认值）。在这类版本中建议分步操作——先加NULL列（瞬时完成），再分批更新旧行（UPDATE分批提交），最后ALTER修改为NOT NULL DEFAULT。MySQL 8.0的Instant DDL对于新增列默认值几乎瞬时完成。在PostgreSQL中，加可空列是瞬时元数据操作，加带默认值的NOT NULL列会触发全表扫描。建议在生产环境先在测试库评估DEFAULT值操作的时间开销。

## 关联页面

[[SQL-DML]] [[SQL-SELECT基础]] [[完整性约束]] [[SQL-视图]]
