---
title: "Go语言-Map内部实现"
course: Go语言
chapter: 数据结构
difficulty: INTERMEDIATE
tags: [Go语言, map, hmap, 哈希表, bucket]
aliases: [Go Map Internals, hmap, Hash Map]
source: "Go runtime源码 map.go; Go Blog: Go maps in action; Effective Go"
updated_at: 2026-05-02
---

## 核心定义

""Go map是基于哈希表的关联容器。底层结构hmap包含：count(元素数量)、B(桶数量的log_2, 共2^B个桶)、buckets(桶数组指针)、hash0(哈希种子,每次运行随机生成防止hash DoS攻击)。桶(bucket)存储8个键值对(top hash+key+value)，通过overflow指针链接溢出桶。超过6.5的平均负载因子(load factor)触发扩容。

## 哈希冲突与扩容

""Go使用链表法(separate chaining)解决哈希冲突：每个桶的8个位置满后创建overflow bucket并链接。扩容分两阶段：1. 增量扩容(gradual grow):翻倍B,数据逐步从旧桶迁移到新桶(每次mapassign/mapaccess迁移1-2个桶) 2. 等量扩容(same-size grow):溢出桶过多时清理(不翻倍,重新哈希分布)。hash seed随机化每进程不同防止DoS。

## 关键结论

""1. map不是并发安全的——并发读写会panic(通过race检测) 2. 遍历顺序随机化(mapiterinit的随机start offset) 3. map的key必须可比较(==),slice/map/function不行 4. 删除不缩容——map只能增长,delete只标记删除 5. nil map可以读但不能写

## 关联知识点

""[[Go语言-Slice内部实现]] [[Go语言-sync包深入]] [[数据结构-哈希表]]
