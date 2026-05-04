---
title: "SQL执行计划分析（EXPLAIN）"
course: 数据库原理
chapter: 索引与查询优化
difficulty: INTERMEDIATE
tags: [数据库, EXPLAIN, 执行计划, 查询优化]
aliases: [EXPLAIN, Query Plan]
source: "PostgreSQL/MySQL官方文档; SQL Performance Explained (Winand)"
updated_at: 2026-05-02
---

## 核心定义

EXPLAIN展示查询的执行计划。各字段含义：id(执行顺序)、select_type(SIMPLE/PRIMARY/SUBQUERY/DERIVED)、type(访问类型从优到劣：system>const>eq_ref>ref>range>index>ALL)、possible_keys(可用索引)、key(实际使用索引)、rows(估计扫描行数)、Extra(Using index/Using filesort/Using temporary/Using where)。Using filesort需额外排序，Using temporary需临时表——性能隐患。

## 关键结论

1. type=ALL(全表扫描)在大表上必须优化 2. Using filesort可添加覆盖索引避免 3. Using index(覆盖索引)是最优的Extra 4. 执行计划是估算，实际用EXPLAIN ANALYZE看真实耗时

## 关联页面

[[索引设计方法论]] [[查询优化]] [[B+树与InnoDB索引]]
