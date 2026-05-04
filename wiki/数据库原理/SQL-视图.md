---
title: SQL视图
course: 数据库原理
chapter: SQL
difficulty: INTERMEDIATE
tags: [SQL, 视图, VIEW, 虚表, 安全控制, 可更新视图]
aliases: [View, SQL VIEW, Virtual Table, Updatable View, Materialized View]
source:
  - 王珊《数据库系统概论》第5版
updated_at: 2026-05-02

---

## 核心定义

视图（View）是由SQL查询定义的一个虚拟表（虚表），其内容由定义视图的查询语句（子查询）在每次被引用时动态计算得出。视图本身不存储物理数据——只存储其查询定义，当用户使用视图时，DBMS将视图的查询定义与用户对视图的查询组合起来（查询重写或查询合并）转化为对底层基本表的查询后执行。使用CREATE VIEW view_name [(column_list)] AS <子查询> [WITH CHECK OPTION] 来创建视图。视图提供了三个核心价值：（1）数据安全——隐藏不希望被特定用户看到的列或行，只暴露视图中的部分数据给用户；（2）数据独立性——当基本表结构变化时修改视图定义而不需修改应用程序；（3）简化复杂查询——将复杂的多表连接、聚合和子查询定义为视图，使得用户可以用简单的SELECT * FROM view查询长而晦涩的复杂逻辑。WITH CHECK OPTION选项确保通过视图插入/更新的数据行满足视图定义的条件（即通过视图操作的数据行仍能被视图本身查询到）。

## 关键结论

- 视图的查询机制：对视图V的查询Q → DBMS将Q和V的定义子查询合并为等价的底层基本表查询Q'。对于要求更新视图（INSERT/UPDATE/DELETE）的操作，底层基本表也受到影响（视图不存数据，操作最终转为对基本表的修改）。更新视图的操作受到许多限制：不可更新通过GROUP BY/HAVING、DISTINCT、聚合函数、集合操作和多表连接定义的视图（除非使用触发器/INSTEAD OF规则）
- 物化视图（Materialized View，某些DBMS如Oracle/PostgreSQL支持）：区别于普通视图，物化视图将查询结果实际存储在磁盘上（定时或手动刷新）。适用于数据仓库和大表预聚合结果的预计算，通过牺牲存储空间和刷新开销换取查询性能。普通视图牺牲了查询时计算时间换取存储空间（不占用空间）。MySQL不支持物化视图
- 可更新视图的限制条件：(1)FROM子句仅涉及一个基本表；（2）SELECT中不包含聚合函数、DISTINCT、GROUP BY/HAVING；（3)属性来自基本表（不能来自表达式或常量）。满足条件的单表视图可以像基本表一样被更新（DELETE/INSERT/UPDATE），DBMS自动将操作翻译为对底层表的更新
- WITH CHECK OPTION的使用场景：当视图定义WHERE dept='IT'时，如果WITH CHECK OPTION存在，通过视图插入的新行必须满足WHERE条件使它能出现在该视图中（即dept字段必须是IT），否则拒绝INSERT。用于约束通过视图的操作不会出现"插入到视图中后在该视图中不可见"的情况
- 视图的权限管理：授予用户对视图的访问权限而不授予基表权限——用户通过视图看到的数据子集受视图定义限制。这是安全数据访问的主要手段

## 易错点

1. **视图不存储数据**：很多初学者想当然地以为视图是"复制的表副本"。实际上这是一个逻辑层而非物理层——修改基本表数据且视图会实时反映新数据（因为查询视图时动态执行视图定义查询），反过来通过视图更新数据也反过来更新到基本表（视图的更新实际修改基本表的行）。

2. **视图查询可能产生惊人性能开销**：因为每次引用视图都重新执行整个视图定义查询（多层嵌套），复杂的视图链可能导致惊人的全表扫描+多表连接的开销——而表面看上去是一个简单的SELECT FROM view。优化器会将查询重写组合但复杂时仍有性能陷阱。

3. **WITH CHECK OPTION是可选的且默认不启用**：这意味着没有加该选项时，用户可以通过视图插入不满足视图WHERE条件的数据（如视图是WHERE dept='IT'的IT部门员工视图，但通过视图插入了dept='HR'的新员工——导致插入成功但在该视图中不可见）。这通常违背视图的设计意图，因此建议定义视图时总是添加WITH CHECK OPTION。

4. **物化视图需手动刷新**：物化视图的查询结果是一份"快照"并不自动更新——除非执行REFRESH MATERIALIZED VIEW。过期的物化视图可能返回错误/旧的数据，这点最容易在生产中踩坑。

## 例题

**例题1**：创建视图CS_Students只包含计算机系(CS)学生的学号、姓名和年龄，通过视图插入、更新和删除操作的边界是什么？

**解答**：
```sql
CREATE VIEW CS_Students AS
SELECT sno, sname, sage
FROM Student
WHERE sdept = 'CS'
WITH CHECK OPTION;

-- 通过视图插入：只能插入行指定的sno,sname,sage，而sdept自动被填充为CS（因为WHERE强制）
INSERT INTO CS_Students VALUES ('20210100', '新同学', 19);  -- 成功，sdept设为CS以通过CHECK OPTION
-- 更新：只能设置IT系行的sname,sage字段
UPDATE CS_Students SET sage = 20 WHERE sno = '20210001';  -- 成功
-- 删除：只删除IT系的行
DELETE FROM CS_Students WHERE sage > 22;  -- 成功
-- 无法通过视图修改sno（因为sno改变了但行仍存在）
```

**例题2**：管理层需要一份各系学生平均年龄的报表。创建视图Dept_AvgAge(dept, avg_age)。此视图可以被更新吗？

**解答思路**：
```sql
CREATE VIEW Dept_AvgAge AS
SELECT sdept AS dept, AVG(sage) AS avg_age
FROM Student
GROUP BY sdept;
```
此图包含GROUP BY和聚合函数AVG，因此是不可更新视图——因为无法将"更新平均年龄"操作唯一映射到基表的行级修改。不可更新的视图：不能使用INSERT、UPDATE、DELETE，但SELECT正常。如果需要修改这类视图的数据，可以定义INSTEAD OF触发器（PostgreSQL的触发器触发替代操作）将操作转化为对基表的对应操作。

## 关联页面

[[SQL-DDL]] [[SQL-SELECT基础]] [[SQL-GROUP BY-HAVING]] [[SQL-存储过程]] [[完整性约束]]
