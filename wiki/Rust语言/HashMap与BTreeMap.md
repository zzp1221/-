---
title: "Rust语言-HashMap与BTreeMap"
course: Rust语言
chapter: 数据结构
difficulty: BASIC
tags: [Rust, HashMap, BTreeMap, 哈希算法, 集合]
aliases: [Rust HashMap, BTreeMap, Hashing]
source: "Rust标准库std::collections文档; Rust Hashmap源码(swisstable port); Google SwissTable"
updated_at: 2026-05-02
---

## 核心定义

""Rust的HashMap<K,V,S=RandomState>使用Google SwissTable作为底层实现(Go也是)——SIMD加速的开放寻址哈希表。默认哈希器RandomState使用SipHash-1-3(抵抗HashDoS的密码学安全哈希算法,但非加密强度)。如果哈希算法不需要DoS保护可用FxHash(更快的非加密哈希,基于乘法+移位)。BTreeMap<K,V>是B树实现的有序映射——键必须Ord(有序)，所有操作O(log n)。

## 选择指南与操作

""HashMap vs BTreeMap选择：HashMap更快(平均O(1)访问)，但键无序且迭代顺序不确定。BTreeMap支持有序遍历(range查询)、最小/最大查询(first_entry/last_entry)。Entry API优雅处理'存在即更新，不存在即插入'：map.entry(key).or_insert(val)/and_modify(|v| *v+=1)。HashSet/BTreeSet是value为()的Map特化。保留插入顺序可使用indexmap crate。

## 关键结论

""1. HashMap的DefaultHasher每次运行使用随机种子 2. Entry API一次哈希查找完成or_insert/remove 3. .get()返回Option<&V> 4. HashMap保留值不保留键——remove需要完整键所有权 5. Eq trait != PartialEq(浮点NaN场景) 6. BTreeMap实现sorted_map,适合数据库索引类操作

## 关联知识点

""[[Rust语言-迭代器与组合器]] [[Rust语言-所有权与借用]] [[数据结构-哈希表]]
