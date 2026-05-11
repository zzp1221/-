---
title: "MapReduce与Spark计算模型"
course: 分布式系统
chapter: 大数据计算
difficulty: INTERMEDIATE
tags: [分布式系统, MapReduce, Spark, RDD, 计算模型]
aliases: [MapReduce, Apache Spark, RDD]
source: "Dean & Ghemawat 2004 (MapReduce); Zaharia et al. 2010 (Spark); Spark官方文档"
updated_at: 2026-05-02
---

## 核心定义

MapReduce(Google, 2004)是大规模分布式数据处理的开创性模型。Map阶段：读入原始数据(k1,v1)→产生中间键值对(k2,v2)→shuffle(按k2分区,合并排序)→Reduce阶段：处理每组(k2,list<v2>)→输出最终结果。Hadoop MapReduce通过HDFS实现数据局部性(data locality)——任务调度到数据所在的节点(colocation)。Spark通过RDD(Resilient Distributed Dataset, 弹性分布式数据集)实现更高效的数据处理——RDD是可容错、可并行操作的只读分区记录集合。

## Spark vs Hadoop

Spark相比Hadoop MapReduce的三大优势：1.)内存计算(in-memory)——中间结果保存在内存中(而非反复写入HDFS)，迭代算法(ML/图算法)性能提升10x-100x 2.)丰富的操作(Transformations: map/filter/join..., Actions: reduce/collect/count——惰性执行) 3.)DAG执行引擎——将整个作业编译为目的图(directed acyclic graph)优化,管道化shuffle-less阶段。DataFrame/Dataset API(SQL-like操作, Catalyst优化器)是RDD的更高层抽象。Shuffle是性能的主要瓶颈(涉及跨节点数据交换——通常也是网络带宽和磁盘IO瓶颈)。

## 关键结论

1. MapReduce的shuffle是性能瓶颈(需要排序)——Spark优化shuffle(不一定排序,通过hash partition) 2. RDD的lineage(沿DAG恢复丢失分区的方案)保证容错——不需要checkpoint(尽管长时间迭代可以checkpoint) 3. Spark的Catalyst优化器使用树形转换规则(类似数据库优化器) 4. shuffle partitions数量是Spark的关键性能参数(默认200 partitions可能不当——随数据规模调整) 5. 数据倾斜(skewed data)是真实世界Spark作业中最常见的性能杀手(热点partition)

## 关联知识点

[[分布式系统-GFS/HDFS分布式文件系统]] [[分布式系统-分布式共识深度(Paxos/Raft对比)]] [[数据库原理-查询优化器深度]]
