---
title: SQL数据操纵语言DML
course: 数据库原理
chapter: SQL
difficulty: BASIC
tags: [SQL, DML, INSERT, UPDATE, DELETE, 数据操纵]
aliases: [Data Manipulation Language, INSERT, UPDATE, DELETE]
source:
  - 王珊《数据库系统概论》第5版
updated_at: 2026-05-02

---

## 核心定义

DML（Data Manipulation Language，数据操纵语言）是SQL中用于查询和修改数据库中数据的语句子集。标准的DML包括四大操作：SELECT（查询数据）、INSERT（插入新数据）、UPDATE（更新已有数据）和DELETE（删除数据）。DML与DDL的关键区别在于：DML操作的是数据行，通常包含在事务中可以回滚（受事务管理），而DDL操作的是数据库模式对象。DML操作的特点：（1）INSERT向表中添加新的元组（行），可以指定插入值列表（VALUES子句）或从查询结果中获取插入数据（INSERT ... SELECT）；（2）UPDATE修改满足条件的已有行的列值，SET子句指定新值，WHERE子句限定修改范围（如果没有WHERE则修改全表所有行——常见但危险的操作）；（3）DELETE删除满足条件的行，如果没有WHERE则删除全表所有行但表定义保留。DML操作可能因为违反完整性约束而被DBMS拒绝（如插入了一个参照外键不存在的行、更新主键值导致外键关联断裂等）。

## 关键结论

- INSERT插入语句的三种形式：（1）INSERT INTO table VALUES (val1, val2, ..., valn) ——按表定义的列顺序提供全部字段值；（2）INSERT INTO table(col1, col3, col5) VALUES (val1, val3, val5) ——指定部分列，被省略的列取DEFAULT值或NULL（需该列允许NULL或有默认值）；（3）INSERT INTO table1 SELECT ... FROM table2 WHERE ... ——从查询结果集进行批量插入（非常高效，可用于数据复制/迁移/归档/ETL操作）
- UPDATE针对符合条件的行进行原位更新：UPDATE table SET col1=expr1, col2=expr2 WHERE condition。更新表达式中可以引用当前列的值（如UPDATE inventory SET quantity = quantity - 1 WHERE product_id = 123）。如果没有WHERE条件，全表所有行的指定列被更新为新值。
- DELETE删除符合条件的行：DELETE FROM table WHERE condition。WHERE通常基于主键或用子查询过滤。如果不指定WHERE，删除全表（小心！）。DELETE逐行删除并产生相应的事务日志（在日志恢复型DBMS中），对于全表删除，TRUNCATE TABLE比DELETE FROM快得多（TRUNCATE是DDL，通过释放数据页方式实现，几乎不写日志）
- DML与事务的关系：所有DML默认在事务中运行（自动提交模式下每条语句是一个事务）。显式事务BEGIN→DML→COMMIT/ROLLBACK可组合多个DML。如果ROLLBACK，从BEGIN以来所有的INSERT/UPDATE/DELETE修改被撤销——数据恢复至事务开始前的状态
- INSERT/UPDATE/DELETE的返回信息：在MySQL/PostgreSQL中，执行DML后可以获取影响的行数（affected rows），如"Query OK, 3 rows affected"；MySQL的ON DUPLICATE KEY UPDATE返回更新的行数2倍为实际影响行（在存在重复时先插入后更新视为2个操作）。

## 易错点

1. **INSERT未指定列的陷阱**：如果INSERT语句省略列名列表，必须为表的每一列都提供值（按表的CREATE定义顺序），包括auto-increment列（通常用NULL或DEFAULT代替让DBMS自动生成）。表结构变更后（加了新列），原有不带列名的INSERT语句可能会因列数不匹配而执行失败。

2. **UPDATE忘写WHERE导致全表更新**：这是最常见的数据误操作事故。应先在SELECT查询确认WHERE条件正确地选择了目标行后再替换为UPDATE执行。在繁忙系统中建议加LIMIT限制影响的批量范围——每次UPDATE 1000行后暂停再继续，避免锁住全表大量行影响并发。

3. **DELETE只删数据不回收磁盘空间**：DELETE只是标记行被删除，在多数DBMS中磁盘空间并未释放（MySQL InnoDB的碎片保留、PostgreSQL的行保留为新事务的历史版本）。需要用OPTIMIZE TABLE/VACUUM FULL等命令回收被删除的空间。TRUNCATE则直接释放数据页。

4. **触发器和外键的副作用**：INSERT/UPDATE/DELETE 可能触发相关联的触发器级联操作或外键的ON DELETE CASCADE等动作，影响超出了主表中看到的行数。在做大批量DML前需要理解表间完整的外键设置和触发器。

## 例题

**例题1**：表Employee(emp_id, name, dept_id, salary)中，写SQL语句实现：(1)插入一条新员工记录；(2)给全部IT部门（dept_id=3）员工的薪资增10%；(3)删除已在职超过5年且薪水在最低档（工资低于3000）的老员工;(4)将IT部门所有员工调出到新成立部门（dept_id=8），在新部门/原部门管理关系保留在外键参照合法的前提下执行。

**解答**：
```sql
-- (1) 插入新员工
INSERT INTO Employee VALUES (1001, '王五', 3, 8000.00);

-- (2) IT部门薪资涨10%
UPDATE Employee SET salary = salary * 1.1 WHERE dept_id = 3;

-- (3) 删除5年以上低薪员工（假设有hire_date字段）
DELETE FROM Employee WHERE hire_date < DATE_SUB(CURDATE(), INTERVAL 5 YEAR) AND salary < 3000;

-- (4) 调出IT部门员工到新部门
UPDATE Employee SET dept_id = 8 WHERE dept_id = 3;
-- 需保证Foreign Key允许此更新（ON UPDATE CASCADE可在部门表更名时自动传播）
```

**例题2**：对比DELETE、TRUNCATE和DROP的异同，从执行速度、事务回滚、空间回收和外键约束四个方面说明。

**解答思路**：(1)DELETE是DML——可用WHERE选择行，产生REDO/UNDO日志，可回滚，触发器触发，空间不释放，外键级联生效。(2)TRUNCATE是DDL——不可加WHERE（清空全表），几乎不写日志（极快），在PostgreSQL可回滚、MySQL 8.0原子DDL但一般不回滚，不触发触发器，外键参照TRUNCATED表时可能报错或被拒（除非用CASCADE删外键）。删除速度DELETE < TRUNCATE。(3)DROP是DDL——连表结构一并删除，不能回滚，外键全部失效。三者递进功能使数据库管理员根据需求选择。

## 关联页面

[[SQL-DDL]] [[SQL-SELECT基础]] [[完整性约束]] [[事务-ACID]]
