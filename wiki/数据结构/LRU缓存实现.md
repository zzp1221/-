---
title: "LRU缓存设计与实现"
course: 数据结构
chapter: 高级数据结构
difficulty: INTERMEDIATE
tags: [数据结构, LRU, 缓存, 哈希链表]
aliases: [LRU Cache]
source: "LeetCode 146; Redis LRU实现; 操作系统"
updated_at: 2026-05-02
---

## 核心定义

LRU(Least Recently Used)缓存淘汰策略：当缓存满时淘汰最久未使用的条目。实现：哈希表+双向链表。哈希表提供O(1)查找，双向链表维护访问顺序。get：查找并移到链表头部。put：插入到头部，若满则删除尾部节点。Python可用collections.OrderedDict。Redis使用近似LRU（采样n个键淘汰其中最久未使用的）。

## 关键结论

1. Java LinkedHashMap可一行实现LRU(accessOrder=true+removeEldestEntry) 2. 真实系统用近似LRU避免维护精确顺序的开销 3. LFU(最不频繁使用)是另一种常见策略

## 关联页面

[[页面置换算法综合]] [[Redis数据结构]] [[哈希表-开放定址法]]
