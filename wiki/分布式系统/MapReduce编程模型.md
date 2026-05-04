---
title: MapReduce编程模型
course: 分布式系统
chapter: 分布式计算
difficulty: INTERMEDIATE
tags: [MapReduce, 分布式计算, Map, Reduce, Shuffle, 批处理]
aliases: [MapReduce, Map-Reduce, 分布式计算模型]
source:
  - "MapReduce: Simplified Data Processing on Large Clusters, Dean & Ghemawat (2004)"
  - "Designing Data-Intensive Applications, Martin Kleppmann, Chapter 10"
  - "Hadoop MapReduce Tutorial, Apache Hadoop Documentation"
updated_at: 2026-05-03
---

## 核心定义

MapReduce是Google于2004年发表的分布式计算编程模型，由Jeffrey Dean和Sanjay Ghemawat提出。它将复杂的分布式计算抽象为两个简单的函数：**Map**和**Reduce**，使不熟悉分布式编程的开发者也能处理大规模数据。

**核心流程**：

1. **Input Split**：输入数据被分割为多个分片（split），每个分片由一个Map任务处理
2. **Map阶段**：Map函数接收一个键值对 `(key1, value1)`，输出一组中间键值对 `[(key2, value2)]`
3. **Shuffle & Sort**：框架自动将相同key的中间结果聚合到一起，并按key排序
4. **Reduce阶段**：Reduce函数接收一个key和该key对应的所有value的列表 `(key2, [value2])`，输出最终结果 `[(key3, value3)]`

**容错机制**：
- **Task失败**：Master检测到Worker失败后，重新调度该Worker上的所有Map和Reduce任务
- **Map任务的幂等性**：Map任务可以安全重试，因为输出存储在GFS/HDFS中
- **Reduce任务的容错**：Reduce输出写入GFS/HDFS，失败后可以重试

**局限性**：
- 每次MapReduce作业需要读写磁盘（中间结果写入HDFS），延迟高
- 不适合迭代计算（如机器学习算法）和交互式查询
- 编程模型简单，但表达复杂逻辑时代码冗长

## 关键结论

- MapReduce的核心贡献是**编程模型的简化**——将分布式计算的复杂性（并行化、容错、负载均衡）封装在框架中
- **Shuffle阶段**是MapReduce的性能瓶颈——数据需要通过网络传输并排序
- MapReduce的容错基于**重试（retry）**而非检查点——Map/Reduce任务是确定性的，重试即可
- MapReduce的**数据本地性（data locality）**优化：将计算调度到数据所在的节点，减少网络传输
- Hadoop MapReduce是MapReduce的开源实现，但已被Spark取代（Spark通过内存计算避免了磁盘IO）

## 易错点

1. **混淆Map和Reduce的输出**：Map输出的是中间键值对，Reduce输出的是最终结果。Map的输出经过Shuffle后才到达Reduce
2. **忽视Shuffle的开销**：Shuffle涉及磁盘IO、网络传输和排序，是MapReduce性能的主要瓶颈。优化Shuffle（如Combiner）是性能调优的关键
3. **误认为MapReduce适合所有场景**：MapReduce不适合迭代计算（每次迭代都要读写磁盘）和实时查询（延迟高）

## 例题

**题目**：使用MapReduce统计一个大型文本文件中每个单词的出现次数（WordCount）。请写出Map和Reduce函数的伪代码，并说明Shuffle阶段的作用。

**解答**：

**Map函数**：
```
def map(key, value):
    # key: 文档偏移量, value: 文档内容（一行文本）
    for word in value.split():
        emit(word, 1)
```

**Reduce函数**：
```
def reduce(key, values):
    # key: 单词, values: [1, 1, 1, ...]
    total = 0
    for count in values:
        total += count
    emit(key, total)
```

**Shuffle阶段的作用**：

假设Map阶段产生了以下中间结果：
- Map1: (hello, 1), (world, 1), (hello, 1)
- Map2: (hello, 1), (foo, 1), (world, 1)

Shuffle阶段自动完成：
1. **Partition**：按key的哈希值将中间结果分配到不同的Reduce任务
2. **Sort**：每个Reduce任务按key排序
3. **Group**：将相同key的value聚合为列表

Shuffle后每个Reduce任务的输入：
- Reduce1: (foo, [1])
- Reduce2: (hello, [1, 1, 1])
- Reduce3: (world, [1, 1])

**优化**：可以在Map端添加**Combiner**，提前进行局部聚合：
- Map1的Combiner: (hello, 2), (world, 1)
- 这减少了Shuffle阶段的网络传输量

## 关联页面

[[Spark核心原理]] [[GFS与HDFS]] [[流计算与Flink]] [[批流一体架构]] [[Bigtable与HBase]]
