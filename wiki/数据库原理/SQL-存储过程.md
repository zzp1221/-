---
title: SQL存储过程
course: 数据库原理
chapter: SQL
difficulty: INTERMEDIATE
tags: [SQL, 存储过程, 函数, 参数, 流程控制, 异常处理]
aliases: [Stored Procedure, SQL Function, IN OUT INOUT Parameters]
source:
  - 王珊《数据库系统概论》第5版
updated_at: 2026-05-02

---

## 核心定义

存储过程（Stored Procedure）是一组预先编译好并存储在数据库服务器上的SQL语句与过程式逻辑的集合，可以接受输入参数、执行业务逻辑并返回输出参数或结果集。存储过程是第一代的数据库编程手段，它允许在数据库服务端运行时处理复杂的业务逻辑，而不需要在应用程序中进行多次网络往返。存储过程支持过程式编程元素：变量声明、条件判断（IF-THEN-ELSE）、循环（WHILE/LOOP/REPEAT）、异常处理（异常块/条件处理DECLARE EXIT/CONTINUE HANDLER）和游标(CURSOR)遍历查询结果的行逐行处理。通过CALL procedure_name(params)调用存储过程。存储过程的优点：(a)减少网络流量——将多次SQL往返合并为单次服务器调用处理全部逻辑；(b)提高性能——语句预编译并可能缓存在数据库的查询计划缓存中；(c)安全性/封装——应用程序不需要直接访问基础表，通过受控的存储过程接口执行操作；(d)模块化——存储过程作为可复用的功能单元，与触发器配合实现业务逻辑。缺点：(a)与特定DBMS耦合（SQL方言不可移植）；(b)调试和版本控制困难；(c)与ORM框架和应用层逻辑协作不灵活。

## 关键结论

- 存储过程的参数模式：IN（输入参数，调用者传值进过程）、OUT（输出参数，过程赋值后返回给调用者——MySQL中用@变量接收）、INOUT（输入输出双向参数）。MySQL中结果集可由SELECT直接返回（隐式结果集）
- 流程控制语句（MySQL/PL/SQL风格）：IF-THEN-ELSEIF-ELSE-END IF；CASE WHEN...THEN...ELSE...END CASE；循环——WHILE...DO...END WHILE / REPEAT...UNTIL...END REPEAT / LOOP...LEAVE...END LOOP；ITERATE（继续循环）/ LEAVE（退出循环）控制循环流
- 游标（Cursor）的声明和使用：当存储过程需要对SELECT结果按行处理时，声明游标DECLARE cur CURSOR FOR SELECT ...，然后OPEN cur打开游标，循环FETCH cur INTO var1,var2逐行获取数据，处理完后CLOSE cur关闭游标。游标使用后用HANDLER处理NOT FOUND异常以结束循环
- 异常处理（MySQL Handler）：DECLARE CONTINUE/EXIT HANDLER FOR condition_value statement; condition_value可以是SQLSTATE、MySQL错误号、NOT FOUND/SQLEXCEPTION/SQLWARNING等。配合游标FETCH结束后触发CONTINUE HANDLER来标记循环退出
- 存储过程的作用域和事务：存储过程可在调用者的事务上下文内执行——AUTOCOMMIT=0时可与调用者共享事务（过程和调用者在同一个提交/回滚范围内）。存储过程内部可自己开始新的事务但通常不建议嵌套事务

## 易错点

1. **DELIMITER的改变（MySQL特有）**：MySQL使用分号作为语句分隔符，但存储过程体内部有多条以分号分隔的语句。如果在创建存储过程时使用默认的分隔符，会在第一个分号处截断导致语法错误。需要用DELIMITER // 命令临时改变分隔符，存储过程定义完后改回 DELIMITER ; 。PostgreSQL使用$$或特定的函数体引号($BODY$）不再遇此问题。

2. **游标的性能代价**：基于行的逐行处理（RBAR - Row By Agonizing Row）比集合(Set-Based)操作慢数百倍。能用集合操作（INSERT ... SELECT、UPDATE WHERE、JOIN处理）就不要用游标逐行——这是SQL处理的黄金规则。存储过程中如果大量使用游标，说明设计逻辑需要反思。

3. **存储过程中变量名与列名的冲突**：当存储过程的变量名与查询列名相同时，MySQL会优先匹配变量名（导致查询失效）。防止措施：变量命名使用前缀（如v_variablename）与列名区分避免歧义。

4. **存储过程的DECLARE顺序**：MySQL要求所有DECLARE语句（变量声明、游标定义、HANDLER异常处理器）必须集中放在存储过程体最前部（BEGIN后第一行位置），在普通SQL语句之前。顺序是：DECLARE variables → DECLARE cursors → DECLARE handlers → 其他。

## 例题

**例题1**：创建存储过程，输入学号，返回该学生已选课程的总学分和平均成绩。

**解答**：
```sql
DELIMITER //
CREATE PROCEDURE GetStudentSummary(IN p_sno CHAR(8), OUT p_total_credit INT, OUT p_avg_grade DECIMAL(5,1))
BEGIN
    SELECT COALESCE(SUM(credit), 0), COALESCE(AVG(grade), 0)
    INTO p_total_credit, p_avg_grade
    FROM SC JOIN Course ON SC.cno = Course.cno
    WHERE sno = p_sno;
END //
DELIMITER ;

-- 调用存储过程
CALL GetStudentSummary('20210001', @credit, @avg);
SELECT @credit AS total_credit, @avg AS avg_grade;
```

**例题2**：写存储过程AutoAssignCounselor，自动为没有导师的学生分配导师（导师限制为职称为教授且指导学生数最少的）。

**解答思路**：用游标遍历没有导师的学生(Counselor为NULL)，对每个学生计算每个教授当前指导学生数量(分组计数)，选择指导数量最少的教授分配。
```sql
DELIMITER //
CREATE PROCEDURE AutoAssignCounselor()
BEGIN
    DECLARE done INT DEFAULT 0;
    DECLARE v_sno CHAR(8);
    DECLARE cur CURSOR FOR SELECT sno FROM Student WHERE counselor_id IS NULL;
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = 1;
    
    OPEN cur;
    read_loop: LOOP
        FETCH cur INTO v_sno;
        IF done THEN LEAVE read_loop; END IF;
        
        UPDATE Student
        SET counselor_id = (
            SELECT prof_id FROM Professor
            WHERE title = '教授'
            GROUP BY prof_id
            ORDER BY (
                SELECT COUNT(*) FROM Student
                WHERE counselor_id = Professor.prof_id
            ) ASC
            LIMIT 1
        )
        WHERE sno = v_sno;
    END LOOP;
    CLOSE cur;
END //
DELIMITER ;
```

## 关联页面

[[SQL-触发器]] [[SQL-视图]] [[SQL-DML]] [[事务-ACID]]
