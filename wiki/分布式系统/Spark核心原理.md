---
title: Spark核心原理
course: 分布式系统
chapter: 分布式计算
difficulty: INTERMEDIATE
tags: [Spark, RDD, DAG, 内存计算, 分布式计算]
aliases: [Apache Spark, Spark, RDD, Resilient Distributed Dataset]
source:
  - "Spark: Cluster Computing with Working Sets, Zaharia et al. (2010)"
  - "Resilient Distributed Datasets: A Fault-Tolerant Abstraction for In-Memory Cluster Computing, Zaharia et al. (2012)"
  - "Apache Spark Documentation"
updated_at: 2026-05-03
---

## 核心定义

Apache Spark是UC Berkeley AMPLab于2009年开发的分布式计算框架，于2014年成为Apache顶级项目。Spark的核心创新是**弹性分布式数据集（RDD, Resilient Distributed Dataset）**——一种只读的、不可变的、可并行操作的数据抽象。

**RDD的特性**：
- **分区（Partition）**：数据分布在集群的不同节点上
- **惰性求值（Lazy Evaluation）**：Transformation操作不会立即执行，只有遇到Action操作时才触发计算
- **血统（Lineage）**：记录RDD的生成路径，用于故障恢复——丢失的分区可以通过重算血统来恢复
- **缓存（Cache/Persist）**：可以将RDD缓存到内存中，避免重复计算

**DAG（有向无环图）调度**：Spark将一系列Transformation操作编译为DAG，DAG Scheduler将DAG划分为**Stage**（以Shuffle为边界），Task Scheduler将Stage中的任务调度到Executor上执行。

**两类操作**：
- **Transformation**：如 `map`、`filter`、`groupByKey`、`join`，返回新的RDD
- **Action**：如 `count`、`collect`、`saveAsTextFile`，触发实际计算并返回结果

**容错机制**：RDD的容错基于**血统重算**——如果某个分区丢失，Spark根据血统信息重新计算该分区，而不是使用检查点。对于宽依赖（Shuffle），可以使用checkpoint来避免重算链过长。

## 关键结论

- Spark通过**内存计算**避免了MapReduce的磁盘IO，迭代计算性能提升10-100倍
- RDD的**血统（Lineage）**是容错的基础——相比检查点机制，血统更轻量且不需要数据复制
- **窄依赖**（如map、filter）不需要Shuffle，可以在一个Stage内流水线执行；**宽依赖**（如groupByKey、join）需要Shuffle，是Stage的边界
- Spark的核心组件：Spark SQL（结构化查询）、Spark Streaming（微批流处理）、MLlib（机器学习）、GraphX（图计算）
- **数据倾斜（Data Skew）**是Spark性能调优的常见问题——某些分区的数据量远大于其他分区

## 易错点

1. **误解惰性求值**：Transformation不会立即执行，只有Action才会触发计算。这意味着如果RDD没有被缓存，每次Action都会从头重算
2. **滥用`collect()`**：`collect()`将所有数据拉到Driver端，如果数据量大，会导致Driver内存溢出。应该使用`take()`、`first()`等限制返回量
3. **忽视窄依赖和宽依赖的区别**：窄依赖可以在一个Stage内并行执行，宽依赖需要Shuffle（涉及磁盘IO和网络传输）。优化的关键是减少Shuffle

## 例题

**题目**：一个Spark作业处理100GB的日志数据，流程如下：
```python
logs = sc.textFile("hdfs:///logs/100gb")
errors = logs.filter(lambda line: "ERROR" in line)
counts = errors.map(lambda line: (line.split()[0], 1)).reduceByKey(lambda a, b: a + b)
counts.saveAsTextFile("hdfs:///output")
```

请分析：（1）DAG中有几个Stage？（2）如果errors RDD只占1GB，是否需要缓存？

**解答**：

**（1）Stage分析**：

操作链：`textFile` → `filter` → `map` → `reduceByKey` → `saveAsTextFile`

- `textFile`：读取HDFS（窄依赖）
- `filter`：窄依赖（每个分区独立过滤）
- `map`：窄依赖（每个分区独立映射）
- `reduceByKey`：**宽依赖**（需要Shuffle，按key重新分区）
- `saveAsTextFile`：Action

因此DAG被划分为**2个Stage**：
- Stage 1：`textFile` → `filter` → `map`（窄依赖，流水线执行）
- Stage 2：`reduceByKey` → `saveAsTextFile`（Shuffle后的操作）

**（2）是否需要缓存errors RDD**：

分析：
- 100GB数据经过filter后只剩1GB（1%的ERROR日志）
- 如果不缓存，`reduceByKey`触发时，Spark会从头重算：读取100GB → 过滤 → map → reduceByKey
- 如果缓存errors RDD（1GB），只需要读取1GB缓存数据 → map → reduceByKey

**建议缓存**：
```python
errors = logs.filter(lambda line: "ERROR" in line).cache()  # 缓存1GB
counts = errors.map(lambda line: (line.split()[0], 1)).reduceByKey(lambda a, b: a + b)
```

节省的IO：100GB - 1GB = 99GB，远大于缓存1GB的内存开销。

## 关联页面

[[MapReduce编程模型]] [[流计算与Flink]] [[批流一体架构]] [[GFS与HDFS]] [[数据分片与哈希取模]]
