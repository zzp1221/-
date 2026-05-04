---
title: SQL子查询与相关子查询
course: 数据库原理
chapter: SQL
difficulty: ADVANCED
tags: [SQL, 子查询, 相关子查询, EXISTS, IN, ANY, ALL, 嵌套查询]
aliases: [Subquery, Correlated Subquery, EXISTS, IN, ANY, ALL, Nested Query]
source:
  - 王珊《数据库系统概论》第5版
updated_at: 2026-05-02

---

## 核心定义

子查询（Subquery / Nested Query）是嵌套在另一个查询（外部查询）内部的SELECT语句，用于为外部查询提供计算中间结果。SQL中子查询可以出现在WHERE子句、FROM子句（派生表）、SELECT子句以及HAVING子句中。根据子查询与外部查询的依赖关系和执行方式，分为：（1）非相关子查询（Uncorrelated Subquery）——子查询独立于外部查询，仅执行一次，返回单值或集合供外部查询使用；（2）相关子查询（Correlated Subquery）——子查询中引用了外部查询的列，子查询对外部查询的每一行都要重新计算一次（在概念上循环执行）。子查询可以返回标量值（单行单列——用在WHERE age > (SELECT AVG(age) FROM ...)）、行集（多行单列——配合IN/NOT IN运算符）或表（多行多列——用在FROM子句或EXISTS中）。子查询常与谓词配合：IN（检查值是否在子查询结果集中）、EXISTS（检查子查询是否返回行时使用）、ANY/SOME（至少满足子查询结果中的某个值）、ALL（满足子查询结果的每一个值）。

## 关键结论

- 非相关子查询的执行方式：DBMS先单独执行子查询（仅一次），将子查询结果（标量/集合）作为外部查询的常量参数，效率较高。例如：SELECT * FROM SC WHERE grade > (SELECT AVG(grade) FROM SC) ——先执行子查询得到平均分值，再用该值过滤外部行——子查询仅在开始时执行一次
- 相关子查询的执行方式：子查询包含对外部查询列的引用，外部查询的每一行都要代入子查询重新执行。例如：SELECT sno,sname FROM Student S WHERE EXISTS (SELECT * FROM SC WHERE SC.sno = S.sno AND cno='C01') ——对Student中每一位学生的sno，子查询检查该生是否有选课C01。对外部查询的n行复杂度为O(n×m)。优化器可能会将相关子查询重写为JOIN
- EXISTS和IN的对比及等价性：对于完备非NULL的情况，EXISTS (SELECT * FROM B WHERE B.key = A.key) 等价于 A.key IN (SELECT B.key FROM B)。两者的重大区别在于NULL的处理——NOT IN在子查询结果中有NULL时会出现"全不返回"的意想不到效果（见*易错点*），而NOT EXISTS不受NULL影响。通常推荐用EXISTS代替IN以规避NULL陷阱
- ALL和ANY/SOME运算符：> ALL (子查询)——大于子查询所有结果值（等价于 > (SELECT MAX(...))）。> ANY (子查询)——大于子查询中至少一个值（等价于 > (SELECT MIN(...))）。通过ALL和ANY可以简洁实现MIN/MAX语义而不需要手动加聚合函数
- 派生表(Derived Table)子查询：FROM子查询（在FROM中的子查询）必须赋予别名。SELECT * FROM (SELECT dept_id, AVG(sal) AS avg_sal FROM Emp GROUP BY dept_id) AS dept_avg WHERE avg_sal > 5000 ——子查询为临时表再用外层过滤器，非常便于多步逻辑分解

## 易错点

1. **NOT IN + NULL = 结果全空**：当SELECT * FROM A WHERE A.col NOT IN (SELECT B.col FROM B) 的子查询结果集中包含NULL值，则NOT IN退化为FALSE（UNKNOWN），整个外部查询结果为空。因为 X NOT IN (1, 2, NULL) 对应 X<>1 AND X<>2 AND X<>NULL，X<>NULL对任何X（包括NULL）都返回UNKNOWN→被WHERE过滤掉。NOT EXISTS正确工作且推荐替代IN/NOT IN。

2. **子查询中的SELECT * 或SELECT 1**：在EXISTS子查询中，SELECT子句实际不返回数据（只检查是否有行存在），写SELECT *或SELECT 1效果相同。EXIST的优化器会用半连接(Semi-Join)算法——找到第一行即返回并停止扫描。

3. **标量子查询必须返回单行单列**：在WHERE中写col > (子查询)，子查询必须返回恰好一行一列——如果返回多行，出错（"子查询返回多于1行"）；如果返回零行，标量子查询为NULL——而col > NULL结果是UNKNOWN等同于FALSE。

4. **相关子查询的性能**：对所有外部查询的行逐行执行子查询在数据量大时性能极差。应由存在查询重写器将其转换为等价的JOIN/半JOIN操作批量处理，相关子查询不是最高效的实现方式——能用JOIN完成的避免用相关子查询。

## 例题

**例题1**：写出SQL查询没有选修C02课程的学生的姓名和所在系。

**解答**：
```sql
-- 方法一：NOT EXISTS（推荐）
SELECT sname, sdept FROM Student S
WHERE NOT EXISTS (
    SELECT * FROM SC WHERE SC.sno = S.sno AND cno = 'C02'
);

-- 方法二：NOT IN（小心NULL）
SELECT sname, sdept FROM Student
WHERE sno NOT IN (
    SELECT sno FROM SC WHERE cno = 'C02'
);
-- 注意方法二：子查询结果中的sno是凭唯一标识不会有NULL
-- 所以两种方法结果相同。
```

**例题2**：查询选修了全部课程的学生学号，用EXISTS逻辑等价表示。

**解答思路**：等价于“不存在一门课这个学生没选”。
```sql
SELECT sno FROM Student S
WHERE NOT EXISTS (
    SELECT * FROM Course C
    WHERE NOT EXISTS (
        SELECT * FROM SC
        WHERE SC.sno = S.sno AND SC.cno = C.cno
    )
);
```
外循环为对每个学生S，内NOT EXISTS——"不存在这样一门课，该学生没有这门课的学习记录"等价于全部课都有学籍，即为所选学生。再交给外NOT EXISTS取反。实际标准型SQL等价关系是 `sno : ∀cno (SC含(sno,cno))` → `NOT ∃ cno (SC不含(sno,cno))`。

## 关联页面

[[SQL-SELECT基础]] [[SQL-JOIN]] [[SQL-GROUP BY-HAVING]] [[关系代数-除]]
