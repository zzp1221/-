---
title: SQL集合操作-UNION
course: 数据库原理
chapter: SQL
difficulty: INTERMEDIATE
tags: [SQL, UNION, UNION ALL, INTERSECT, EXCEPT, 集合操作]
aliases: [UNION, UNION ALL, INTERSECT, EXCEPT, Set Operations]
source:
  - 王珊《数据库系统概论》第5版
updated_at: 2026-05-02

---

## 核心定义

集合操作是SQL中将两个或多个具有相同结构（列数相同、对应列数据类型兼容）的SELECT查询结果集进行集合运算的机制。SQL支持三种标准集合操作：（1）UNION——求并集，合并两个查询结果并自动去除重复行；（2）INTERSECT——求交集，返回同时出现在两个查询结果中的行；（3）EXCEPT（Oracle中为MINUS）——求差集，返回出现在第一个查询但不在第二个查询结果中的行。此外，UNION ALL是UNION的变种——合并两个查询结果但保留所有重复行（不做去重操作），性能远优于UNION（因为省去了去重的排序或哈希开销）。集合操作是SQL中表达"并/交/差"语义的主要工具，在数据合并、报表整合和不兼容结构的同构化后合并等场景中广泛应用。集合操作的两个SELECT语句之间的列数必须相同，且对应列的数据类型可比较（兼容/可隐式转换）。结果集的列名由第一个SELECT语句的列名决定。

## 关键结论

- UNION vs UNION ALL的核心区别：UNION = SELECT结果集合并 + 去重（等价于UNION ALL + DISTINCT），UNION ALL = 纯合并无去重。因为去重需要排序或哈希，性能差距显著——当确定两结果集不存在重复行时（或允许重复），应使用UNION ALL
- INTERSECT的行为：求两个集合的交集——某行同时出现在两个结果中时才返回。可用于"查询既选修了C01又选修了C02课程的学生名单"等复杂交集需求。MySQL不支持INTERSECT语法（可用INNER JOIN替代）
- EXCEPT/MINUS的语义：返回"在第一个查询中但在第二个查询中不存在"的行——实现差集操作。适用于"选修了C01但没有选C02的学生"等差集需求。MySQL不支持EXCEPT（可用LEFT JOIN + IS NULL或NOT EXISTS替代）
- 多集合操作与ORDER BY：ORDER BY只能出现在整个集合操作语句的最后，对所有集合操作的整体结果排序——不能对集合操作中单个SELECT做独立排序。如果想对单个SELECT做排序可将其作为子查询加ROW_NUMBER/排序后子查询再UNION
- 集合操作的列对应方式：按位置对应而非按名称对应。第一个SELECT的第1列与第二个SELECT的第1列对应，第2列与第2列对应...列名全部来自第一个SELECT

## 易错点

1. **UNION 自动去除ALL功能**：UNION是默认去重的（不同于SELECT ALL）。很多人忽略了这点并以为UNION只是简单合并——实际上它在后台执行了"排序/哈希→去重"操作，增加了额外的性能成本。

2. **集合操作要求列数相同/类型兼容**：两个SELECT的列数必须完全相同。如果第一个表有5列而第二个只有4列就会出错——但可以通过用NULL填充补齐缺失列：SELECT col1, col2, NULL AS col3 FROM table2。

3. **INTERSECT和INNER JOIN不完全等价**：INNER JOIN在一个有重复行且在配对变量多时会增加行数（连接膨胀），而INTERSECT是纯集合交集——两边的行进行匹配去重。不能简单互换。

4. **MySQL不支持INTERSECT和EXCEPT**：MySQL 8.0+只支持UNION和UNION ALL，不支持INTERSECT和EXCEPT。需要改写为INNER JOIN + DISTINCT 或 NOT EXISTS + DISTINCT 或 LEFT JOIN + IS NULL。

## 例题

**例题1**：查询同时选修了C01和C02课程的学生学号。

**解答**：
```sql
-- 方法一：INTERSECT (PostgreSQL/Oracle/SQL Server)
SELECT sno FROM SC WHERE cno = 'C01'
INTERSECT
SELECT sno FROM SC WHERE cno = 'C02';

-- 方法二：INNER JOIN（MySQL兼容）
SELECT DISTINCT a.sno
FROM SC a INNER JOIN SC b ON a.sno = b.sno
WHERE a.cno = 'C01' AND b.cno = 'C02';

-- 方法三：子查询+IN（MySQL通用）
SELECT DISTINCT sno FROM SC
WHERE cno = 'C01' AND sno IN (SELECT sno FROM SC WHERE cno = 'C02');
```

**例题2**：两个库合并——将员工表EMP2022和EMP2023合并成一个全员工列表（自动去重保留唯一记录），按部门排序。

**解答思路**：使用UNION去重合并两个SELECT计算层，在外层ORDER BY排序。
```sql
SELECT emp_id, name, dept_id FROM EMP2022
UNION
SELECT emp_id, name, dept_id FROM EMP2023
ORDER BY dept_id, emp_id;
```
注意：UNION已去除两个表中相同 emp_id 和 name全相同的行。如肯定无重复可用UNION ALL。

## 关联页面

[[SQL-SELECT基础]] [[SQL-JOIN]] [[关系代数-选择投影]] [[关系代数-连接]]
