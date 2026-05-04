---
title: SQL JOIN连接查询
course: 数据库原理
chapter: SQL
difficulty: INTERMEDIATE
tags: [SQL, JOIN, INNER JOIN, LEFT JOIN, RIGHT JOIN, FULL JOIN, CROSS JOIN, 连接查询]
aliases: [SQL JOIN, INNER JOIN, OUTER JOIN, LEFT JOIN, RIGHT JOIN, CROSS JOIN]
source:
  - 王珊《数据库系统概论》第5版
updated_at: 2026-05-02

---

## 核心定义

JOIN是SQL中用于将多个表中的数据按照指定的关联条件组合成一个结果集的操作。SQL支持多种JOIN类型：（1）INNER JOIN（内连接）——仅返回在两个表中都满足连接条件的匹配行，所有不匹配的行被丢弃；（2）LEFT [OUTER] JOIN（左外连接）——返回左表（LEFT JOIN左侧的表）的全部行，右表中不匹配的列用NULL填充；（3）RIGHT [OUTER] JOIN（右外连接）——返回右表的全部行；（4）FULL [OUTER] JOIN（全外连接）——返回左右两表的所有行，不匹配的填NULL。（5）CROSS JOIN（交叉连接）——返回两表的笛卡尔积（所有可能的行对组合）。JOIN的连接条件在ON子句中指定（通常为等值条件，如ON A.dept_id = B.dept_id），USING(dept_id)语法是ON的简写形式（要求两个表有同名的列且语义相同）。自然连接NATURAL JOIN自动按所有同名同义列等值连接并消除重复列。JOIN是关系数据库中"将分散在不同表中的数据进行关联"的最主要机制——通过JOIN连接外键对应的主键来还原关系模型中的实体-联系。

## 关键结论

- 内连接 INNER JOIN的最常见形式：FROM table1 t1 INNER JOIN table2 t2 ON t1.key = t2.fkey。结果是两表匹配行的水平拼接集合。内连接等价于：FROM t1,t2 WHERE t1.key = t2.fkey — 但显式JOIN是标准的现代风格。多表连接可链式串联
- 左外连接 LEFT JOIN的典型用例："列出所有客户及其订单（即使某些客户从无订单）"——左表Customer的所有行保留，Orders表的无匹配行用NULL填充。左连接中如果在ON中没有匹配项但依然希望右侧表信息展示则为NULL——这就是悬浮元组的处理
- ON和WHERE在JOIN中过滤条件位置的区别：在LEFT JOIN中，ON中的条件在"连接时"过滤右表行（ON条件排除的行将不在连接匹配中但左表行仍保留——NULL化）；WHERE条件在"连接后"过滤结果行。如果将本该放ON的右表过滤条件放到了WHERE中，LEFT JOIN的语义将被破坏——可能导致LEFT JOIN实际回退为INNER JOIN
- USING语法与ON的区别：USING(col)等价于ON t1.col = t2.col，但结果中col只出现一次（等值去重）。USING要求列名在两个表中完全相同且语义一致
- JOIN的执行计划与优化：JOIN是DBMS查询处理中最核心的优化点——优化器选择三种物理算法执行JOIN：(a)嵌套循环连接(Nested Loop Join)——适合小表驱动大表且连接列有索引；(b)哈希连接(Hash Join)——适合等值连接且两表较大，一表建立哈希表另一表探测；(c)排序合并连接(Merge Join)——适合等值连接且两表已排序（如索引提供排序结果）

## 易错点

1. **LEFT JOIN的过滤条件放错位置**：这在前面"关键结论"第3条已说明。具体而言SELECT * FROM A LEFT JOIN B ON A.id=B.aid AND B.status='active'——返回A全部行，B.status='active'作为匹配条件（匹配不到active状态时B列填NULL）。而SELECT * FROM A LEFT JOIN B ON A.id=B.aid WHERE B.status='active'——WHERE在连接后执行，将B.status为NULL或非active的行滤掉，效果等同于INNER JOIN（因为NULL被WHERE排除）。

2. **多表JOIN的笛卡尔积爆炸**：若N个表连接没有指定正确的ON条件，DBMS生成所有行的笛卡尔积——3个10万行的表产生1e15行结果集，数据库崩溃或查询超时。每个JOIN必须有充分的ON/NATURAL/USING连接条件防止无意笛卡尔积。

3. **JOIN方向性不等于SQL中列的顺序**：LEFT JOIN a ON ... LEFT JOIN b ON ... 是依次左连接；WHERE条件在全部连接完成后应用。连接树的写法影响执行计划——调整驱动表的放置顺序（左表作为"探查表(inner table)"）可能会大幅度影响嵌套循环连接的性能。

4. **全外连接在MySQL中不支持**：MySQL没有FULL OUTER JOIN语法，需要用LEFT JOIN UNION RIGHT JOIN模拟实现。

## 例题

**例题1**：三表连接查询——列出每个学生(Student)的姓名、所选的每一门课程名称(Course)以及成绩(SC)。要求没有选课的学生也出现在结果中（课程名和成绩填空）。

**解答**：
```sql
SELECT S.sname, C.cname, SC.grade
FROM Student S
LEFT JOIN SC ON S.sno = SC.sno
LEFT JOIN Course C ON SC.cno = C.cno;
```
先用Student LEFT JOIN SC保留所有学生（含未选课的），再LEFT JOIN Course将课程信息补上。未选课学生的SC列(包括SC.cno)均为NULL，SC.cno=NULL与Course无匹配，所以C.cname和SC.grade为NULL。

**例题2**：内连接和外连接在什么场景下应使用不同的策略？举例说明LEFT JOIN误用导致数据量膨胀的问题。

**解答思路**：内连接适用于"必须双方配对"的场景（如订单必须有对应客户——几乎总是双向存在的）。外连接适用"主实体可能存在无关联从属"的场景（如员工可以不归属任何部门）。LEFT JOIN 滥用：如果使用两个LEFT JOIN链式连接而两个右表相互独立且存在多关联关系可能会使结果行数远超预期。如 A LEFT JOIN B ON A.id=B.aid LEFT JOIN C ON A.id=C.aid——假设A有两行，每行各有两个B匹配和两个C匹配——结果是8行（4+4），多对多关系下膨胀很大。需用子查询独立统计数据再LEFT JOIN合并，或预先GROUP BY按唯一键聚成一端再JOIN。

## 关联页面

[[关系代数-连接]] [[SQL-SELECT基础]] [[SQL-子查询]] [[索引优化]]
