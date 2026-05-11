---
title: "列存储与OLAP"
course: 数据库原理
chapter: 存储引擎
difficulty: ADVANCED
tags: [数据库, 列存储, OLAP, 压缩, 数据仓库]
aliases: [Column Store, OLAP, Data Warehouse]
source: "Stonebraker et al. 2005 (C-Store); Abadi et al. 2008 (Column-Stores vs Row-Stores); ClickHouse文档"
updated_at: 2026-05-02
---

## 核心定义

列存储(column store)将每一列的数据独立存储(而非行式存储的每行连续存储)。OLAP(Online Analytical Processing)查询通常扫描全表但只涉及少数列——列存储只需读取涉及的列(减少IO)，且对单列有更好的压缩效果(列内数据域高度重复)。核心压缩编码：字典编码(Dictionary Encoding——将值映射为整数ID)、游程编码(Run-Length——连续相同值：value+count)、Delta编码(存储相邻值的差值)、位图编码(Bitmap——对每个可能值建bit向量)。

## 向量化执行

列存储通常采用向量化执行(vectorized execution)——一次处理整个数据块(如1024行vector)而非逐行处理。这确保CPU的SIMD和循环流水充分发挥。ClickHouse和MonetDB是向量化执行的典型。C-Store的projection结构物化了部分列的预计算——满足频繁查询模式的覆盖索引。列存储压缩效果极好(通常10x-100x缩小)，因为列数据往往重复值多。现代混合系统中，列存储常作为行存储HTAP(Hybrid Transactional/Analytical Processing)的辅助结构。

## 关键结论

1. 列存储不适用于频繁点查询/小范围行查询(因读取整个列但仅需几行) 2. 列存储对聚合计算(sum/avg/count)极高效(只需扫描所需列) 3. Parquet/ORC是开放格式的列存储文件格式(适用于数据湖Hive/Spark) 4. 列存储结合SIMD在分析场景中可达到接近内存带宽极限的性能 5. 列存储的更新(in-place update)昂贵——通常通过追加+合并结构(LSM-like compaction)

## 关联知识点

[[数据库原理-LSM-Tree与LevelDB]] [[数据库原理-查询优化器深度]] [[计算机组成原理-SIMD与向量化]]
