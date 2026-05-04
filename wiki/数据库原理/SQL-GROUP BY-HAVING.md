---
title: SQL分组与聚合-GROUP BY与HAVING
course: 数据库原理
chapter: SQL
difficulty: INTERMEDIATE
tags: [SQL, GROUP BY, HAVING, 聚合函数, COUNT, SUM, AVG, MAX, MIN]
aliases: [GROUP BY, HAVING, Aggregate Functions, COUNT, SUM, AVG]
source:
  - 王珊《数据库系统概论》第5版
updated_at: 2026-05-02

---

## 核心定义

GROUP BY子句是SQL中用于对查询结果进行分组以执行各类聚合计算的操作。它将FROM/WHERE过滤后的行集按照指定的分组列值划分成若干个组，每个组（具有相同分组列值的行集合）被压缩为结果集中的一行，然后可以在SELECT和HAVING中对这些组应用聚合函数（Aggregate Functions）进行计算。常用的聚合函数包括：COUNT(*)或COUNT(column)——计算行数（COUNT(*)计所有行含NULL, COUNT(column)只计非NULL值）、SUM(column)——对数值列求和、AVG(column)——求平均值、MAX(column)/MIN(column)——求最大值/最小值。HAVING子句对分组后的结果做进一步过滤（功能类似WHERE但WHERE过滤分组前的各行，HAVING过滤分组后的各组）。GROUP BY是SQL中数据分析、统计报表和多维聚合查询的核心工具，配合EXISTS、JOIN和子查询可以完成复杂的数据统计任务。正确理解GROUP BY意味着理解SELECT后的表达式必须满足单值原则——聚合键或聚合函数（或函数依赖于聚合键）。

## 关键结论

- SQL标准要求SELECT中出现的非聚合列必须是GROUP BY子句中出现的列（分组键），否则逻辑上有歧义——每个组内有多个不同的列值，无法确定选哪一个。MySQL在默认模式下（ONLY_FULL_GROUP_BY关闭时）会任意选其中一个值（结果是未定义的/随机的），这是MySQL早期版本的宽容行为，不符合SQL标准。PostgreSQL和严格模式MySQL会拒绝这种查询
- 聚合函数与NULL：COUNT(column)忽略NULL（不计数NULL所在行），SUM/AVG/MAX/MIN自动跳过NULL（如果该列全为NULL则结果为NULL）。注意AVG = SUM/COUNT（仅计非NULL行），所有NULL被跳过；
- GROUP BY的多种表达形式：按单列分组(单层)，按多列分组(列组合形成分组键)，按表达式分组(GROUP BY YEAR(date_column))，GROUP BY ROLLUP/CUBE/GROUPING SETS ——高级多维聚合运算符（支持小计和总合计行），用于OLAP报表。MySQL支持WITH ROLLUP生成超级聚合行
- HAVING vs WHERE：WHERE过滤原始行（聚合前），HAVING过滤分组结果（聚合后）。"查询总销售额超过10000元的客户"用HAVING SUM(amount)>10000——聚合后的条件。"仅统计2023年的订单"用WHERE year=2023——聚合前的行级过滤。二者可以结合使用
- GROUP BY的执行顺序：FROM→WHERE→GROUP BY→HAVING→SELECT→DISTINCT→ORDER BY→LIMIT。分组后SELECT列表受限于分组键或聚合函数

## 易错点

1. **WHERE中不能使用聚合函数**：如WHERE COUNT(*)>5是错误的——聚合函数作用于分组后，不能在分组前的行过滤中使用。这必须用子查询或HAVING实现。

2. **GROUP BY的列和SELECT的列匹配问题**：MySQL的宽松模式导致隐蔽的bug——GROUP BY dept_id 但 SELECT dept_id, salary, name，salary和name只展示每组的第一行（任意顺序），导致数据不一致和不正确查询结果。务必启用ONLY_FULL_GROUP_BY模式（MySQL 5.7+推荐）。

3. **COUNT(DISTINCT column) 与 COUNT(column)的区别**：COUNT(DISTINCT dept) 统计不同的部门数；COUNT(dept)统计部门为NULL以外的总行数；COUNT(*)统计全部行数（包括所有值为NULL的行）。

4. **HAVING与WHERE的优化考量**：尽量把能在WHERE中过滤的条件写在WHERE里而非HAVING里，因为WHERE过滤减少了参与分组的数据量——"谓词下放"的原则。例如HAVING dept='IT'比在HAVING中写得更快处理完成。

## 例题

**例题1**：查各系的男女生人数，只列出学生总人数超过5人的系。写出SQL。

**解答**：
```sql
SELECT sdept, ssex, COUNT(*) AS cnt
FROM Student
GROUP BY sdept, ssex
HAVING COUNT(*) > 5
ORDER BY sdept;
```
分组键是(sdept, ssex)的组合，每个系有男组和女组。HAVING过滤掉人数不超过5的系-性别组合组。

**例题2**：写出SQL查询：统计每门课程的平均分、最高分、最低分，仅展示选课人数≥3的课程，按平均分降序排列。

**解答思路**：按cno分组对grade用聚合函数。
```sql
SELECT cno,
       AVG(grade) AS avg_grade,
       MAX(grade) AS max_grade,
       MIN(grade) AS min_grade,
       COUNT(*) AS student_count
FROM SC
GROUP BY cno
HAVING COUNT(*) >= 3
ORDER BY avg_grade DESC;
```

## 关联页面

[[SQL-SELECT基础]] [[SQL-JOIN]] [[SQL-子查询]] [[SQL-视图]]
