---
title: SQL SELECT查询基础
course: 数据库原理
chapter: SQL
difficulty: BASIC
tags: [SQL, SELECT, WHERE, ORDER BY, LIMIT, DISTINCT, 别名]
aliases: [SQL SELECT, WHERE Clause, ORDER BY, LIMIT, DISTINCT]
source:
  - 王珊《数据库系统概论》第5版
updated_at: 2026-05-02

---

## 核心定义

SELECT语句是SQL中最核心也最常用的数据查询语句，用于从数据库中检索满足条件的数据。完整的SELECT语句语法结构为：SELECT [ALL|DISTINCT] <目标列表达式列表> FROM <表名或视图名列表> [ WHERE <条件表达式> ] [ GROUP BY <分组列> [ HAVING <分组过滤条件> ] ] [ ORDER BY <排序列> [ ASC|DESC ] ] [ LIMIT <行数> [ OFFSET <偏移量> ] ]。各子句的执行逻辑顺序（非书写顺序）为：FROM（确定数据来源）→ WHERE（行过滤）→ GROUP BY（分组）→ HAVING（分组过滤）→ SELECT（选择/计算列）→ DISTINCT（去重）→ ORDER BY（排序）→ LIMIT（截取行数）。理解这个逻辑顺序是正确写出复杂SELECT查询的关键。SELECT不仅可以查询单表的列，还可以进行计算（算术表达式、函数调用）以及多层嵌套子查询。DISTINCT关键字用于从结果集中去除重复行，ALL是默认行为（返回所有行不自动去重）。ORDER BY支持升序ASC和降序DESC排序，可以使用列的别名或序号进行排序。LIMIT（及OFFSET）用于分页查询（如每页20条记录）。

## 关键结论

- SELECT语法结构中的常见要素：(1)列别名——SELECT column AS alias_name 或 SELECT column alias_name（省略AS关键字）；当列表达式是计算字段且不易理解时必须加别名；(2)WHERE条件中的常用运算符——比较运算符（=, <>, <, >, <=, >=）、范围谓词BETWEEN值1 AND 值2（闭区间）、集合成员测试IN(值1, 值2, ...) 或 NOT IN、字符串匹配LIKE '模式'（%零或多个任意字符、_单个任意字符）、NULL值检查IS NULL/IS NOT NULL、逻辑连接AND/OR/NOT（注意AND优先级高于OR，不想歧义需用括号）
- 算术表达式和函数：SELECT中可以包含加(+)、减(-)、乘(*)、除(/)等算术运算和各种DBMS内置函数（字符串函数如CONCAT、SUBSTRING、LENGTH；日期函数如NOW、DATE_FORMAT、DATEDIFF；数值函数如ROUND、ABS、CEIL/FLOOR；类型转换CAST/CONVERT）。表达式可借助列别名和未来外层查询引用
- 多表查询（FROM子查询/表列表）：FROM子句中列出多个表用逗号分隔，结果取这些表的笛卡尔积（所有组合）。如果不是有意要笛卡尔积（极少情况），必须加WHERE连接条件来限制（等值条件），这构成了早期的隐式内连接写法——已被显式JOIN语法取代
- DISTINCT作用于整个SELECT列表：SELECT DISTINCT col1, col2 的结果是(col1, col2)组合的去重，不是单列或某列的去重。DISTINCT原理上需要对结果进行排序或哈希操作——有性能代价
- ORDER BY可以使用列在SELECT中的序号（如ORDER BY 2表示按第二列排序），但为代码可读性和稳定性应优先使用别名或列原名

## 易错点

1. **WHERE和HAVING的区别**：WHERE作用于分组前（原始行级过滤），HAVING作用于分组后（分组结果集过滤）。WHERE中不能使用聚合函数（COUNT/SUM/AVG/MAX/MIN），而HAVING可以且主要用于聚合条件过滤，但GROUP BY的分组列可以在HAVING中间接引用。

2. **NULL值的三值逻辑**：任何与NULL的比较结果都是UNKNOWN（不是TRUE也不是FALSE），包括NULL = NULL返回UNKNOWN而非TRUE（NULL不等于NULL，需要用IS NULL检查）。在WHERE中UNKNOWN被当作FALSE对待，条件不成立。更隐蔽的陷阱是NOT IN中包含NULL——当子查询结果集中有NULL值时，整个NOT IN的效果可能退化为空（因为x NOT IN (1, 2, NULL)等价于 x<>1 AND x<>2 AND x<>NULL，第三个总是UNKNOWN → 整体为FALSE/UNKNOWN）。

3. **LIMIT的分页坑**：LIMIT m OFFSET n（从第n+1行开始取m行）。当n很大时（如OFFSET 100000 LIMIT 20），DBMS需扫描前100020行然后丢掉前100000行返回最后20行——开销很大。大数据分页用''基于游标的分页"更好（记下上一页最后一行ID，下次用WHERE id > last_id LIMIT 20）。

4. **SELECT * 在生产环境的使用**：SELECT * 自动返回所有列——方便但存在隐患：表加了新列可能影响应用层（如接收了意外的数据类型）和性能（拉取不必要的大字段）。生产环境建议显式列出所需字段（也有助于查询计划器做更优优化）。

## 例题

**例题1**：写出SQL查询，从Student表中查询计算机系(CS)年龄在18-22之间且名字不带"张"字的男学生学号和姓名，按年龄降序排列，限制前5条。

**解答**：
```sql
SELECT sno, sname
FROM Student
WHERE sdept = 'CS'
  AND sage BETWEEN 18 AND 22
  AND ssex = '男'
  AND sname NOT LIKE '张%'
ORDER BY sage DESC
LIMIT 5;
```

**例题2**：已知订单表Orders(order_id, customer_id, order_date, amount)。写出SQL统计2023年度每位客户的订单总额(用别名total_amount)，并只列出订单总额超过5000元的客户，按总额降序排序。

**解答思路**：需要GROUP BY按customer_id分组并SUM(amount)计算总额，HAVING过滤掉额>5000。
```sql
SELECT customer_id, SUM(amount) AS total_amount
FROM Orders
WHERE order_date BETWEEN '2023-01-01' AND '2023-12-31'
GROUP BY customer_id
HAVING SUM(amount) > 5000
ORDER BY total_amount DESC;
```
注意：HAVING中必须写聚合函数SUM(amount)，不能直接引用SELECT中的列别名total_amount（虽然某些DBMS如MySQL允许HAVING使用SELECT别名，但SQL标准禁止）。

## 关联页面

[[SQL-JOIN]] [[SQL-GROUP BY-HAVING]] [[SQL-子查询]] [[SQL-UNION]] [[SQL-DML]]
