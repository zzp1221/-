---
title: SQL触发器
course: 数据库原理
chapter: SQL
difficulty: ADVANCED
tags: [SQL, 触发器, TRIGGER, BEFORE, AFTER, INSTEAD OF, 审计日志]
aliases: [Trigger, BEFORE Trigger, AFTER Trigger, INSTEAD OF Trigger, Audit Log]
source:
  - 王珊《数据库系统概论》第5版
updated_at: 2026-05-02

---

## 核心定义

触发器（Trigger）是一种特殊的存储过程，它不需要被显式调用，而是在预定义的事件（INSERT、UPDATE、DELETE操作）发生时由DBMS自动执行。触发器与特定的表相关联，对该表执行触发事件时触发器自动触发。触发器由三个核心组件组成：（1）触发事件（INSERT/UPDATE/DELETE，特定列更新时更具体的OF column_name）；（2）触发时机（BEFORE在操作前执行——可用来验证/修改即将插入/更新的数据；AFTER在操作后执行——可用来记录日志/更新缓存/级联更新其他表；INSTEAD OF替代操作——用在视图上替代原始操作执行替代逻辑）；（3）触发动作（触发体——SQL块/PROCEDURE，在触发时机正确时执行的操作）。触发器的粒度可以是FOR EACH ROW（行级触发器，每影响一行触发一次）或FOR EACH STATEMENT（语句级触发器，每个触发语句触发一次——MySQL不支持此粒度）。触发器主要用于实现复杂完整性约束（跨表业务规则验证）、审计日志（记录所有数据变更历史）、物化数据的自动维护（计数器/汇总表更新）以及级联操作（同步关联表数据）。

## 关键结论

- 行级触发器（FOR EACH ROW）中可访问OLD和NEW伪记录：在INSERT触发器中只有NEW（新的行值），在DELETE触发器中只有OLD（被删除的行旧值），在UPDATE触发器中两者均可访问（OLD=旧行值，NEW=新行值）。触发器可以在BEFORE触发器中修改NEW列的值（SET NEW.column = expr），从而在插入/更新前置拦截或修改数据
- 触发器的常见应用模式：(a)审计日志——AFTER INSERT/UPDATE/DELETE触发，将旧数据或新数据或差异记录到audit_log表中；(b)自动维护修改时间——BEFORE INSERT/UPDATE触发器SET NEW.updated_at = NOW()自动更新时间戳；(c)维持聚合缓存——在父表的计数器列（如部门表.dept_emp_count）受子表插入/删除影响时，AFTER触发器更新父表计数器；(d)复杂业务规则——如"员工的工资不能超过其直接主管工资的120%"，在BEFORE INSERT/UPDATE中做关联表检查
- 级联触发器执行顺序：同一表中的触发器按BEFORE→行操作→AFTER顺序执行。同一事件和时机的多个触发器，MySQL中按创建顺序执行。一个触发器的执行可能级联引发其他表的触发器（连环触发），需注意防止无穷递归
- 触发器的缺点与滥用：(a)隐蔽的逻辑——开发人员修改代码时未料到背后有触发器，可能导致意外行为和数据变化；(b)性能影响——行级触发器中的开销乘以影响行数，大表DML操作变慢；(c)调试困难——触发器内部的错误难以捕获和跟踪；(d)难以测试。现在有趋势将触发器逻辑迁移到应用层或使用事件队列
- 触发器的DBMS方言差异：MySQL使用FOR EACH ROW语法且每表同事件同时间只能有一个触发器；PostgreSQL支持FOR EACH STATEMENT和条件触发器(WHEN condition)；Oracle支持复合触发器，可定义多个时间点的联合触发器

## 易错点

1. **触发器中不能对触发表进行直接修改**：在MySQL中，不能在触发器内部对该触发器所依附的表直接执行INSERT/UPDATE/DELETE——否则导致触发器递归无限执行（MySQL会出现"Can't update table 'xxx' in stored function/trigger"错误）。需要对触发表做更新时需通过NEW伪记录赋值完成（BEFORE触发器中）。

2. **触发器的NEW值在BEFORE中可以修改，在AFTER中不可修改**：AFTER触发器中修改NEW列没有意义因为行已经插入/更新完成。如果需要修改即将写入的数据，应使用BEFORE触发器。

3. **触发器逻辑与应用程序代码的重复**：如果应用程序代码中已有业务数据验证，而触发器中又重复这些验证但逻辑有微妙差异——产生不一致的错误行为。好的实践：将业务规则仅在一处定义（触发器中、应用程序中或数据库约束中清晰划分职责）。

4. **原子批量操作时的触发器代价**：触发器对每行都触发——处理数百万行的批量UPDATE/INSERT会触发数百万次触发器执行而极慢。因此不建议对大型批量操作的表使用行级触发器。

## 例题

**例题1**：设计审计触发器，记录对Students表的所有INSERT、UPDATE、DELETE操作到audit_log表中（记录操作时间、操作类型、学号、旧值新值）。

**解答**：
```sql
CREATE TABLE audit_log (
    id INT AUTO_INCREMENT PRIMARY KEY,
    operation CHAR(1),  -- I/U/D
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    sno CHAR(8),
    old_name VARCHAR(20),
    new_name VARCHAR(20)
);

DELIMITER //
CREATE TRIGGER trg_student_audit_insert
AFTER INSERT ON Student
FOR EACH ROW
BEGIN
    INSERT INTO audit_log(operation, sno, new_name)
    VALUES ('I', NEW.sno, NEW.sname);
END //

CREATE TRIGGER trg_student_audit_update
AFTER UPDATE ON Student
FOR EACH ROW
BEGIN
    INSERT INTO audit_log(operation, sno, old_name, new_name)
    VALUES ('U', NEW.sno, OLD.sname, NEW.sname);
END //

CREATE TRIGGER trg_student_audit_delete
AFTER DELETE ON Student
FOR EACH ROW
BEGIN
    INSERT INTO audit_log(operation, sno, old_name)
    VALUES ('D', OLD.sno, OLD.sname);
END //
DELIMITER ;
```

**例题2**：防止递归更新——设计触发器实现"当某课程的学分被修改时，如果该学分>6，自动调整为6"。分析这段触发器有无递归风险。

**解答思路**：
```sql
CREATE TRIGGER trg_max_credit
BEFORE UPDATE ON Course
FOR EACH ROW
BEGIN
    IF NEW.credit > 6 THEN
        SET NEW.credit = 6;
    END IF;
END;
```
此触发器为BEFORE触发——在行写入前修改数据，直接在NEW上赋值，**不会递归调用自身**，因为修改NEW.credit不会再次触发BEFORE UPDATE。危险的情况是如果写成了UPDATE Course SET credit=6 WHERE...这样会触发同一个表又执行UPDATE导致又调用这个触发器形成无限递归。

## 关联页面

[[SQL-存储过程]] [[SQL-视图]] [[完整性约束]] [[事务-ACID]]
