---
title: "JavaScript-Map/Set/WeakMap/WeakSet"
course: JavaScript/TypeScript
chapter: 集合类型
difficulty: BASIC
tags: [JavaScript, Map, Set, WeakMap, WeakSet, ES6]
aliases: [JavaScript Map, WeakMap, ES6 Collections]
source: "ECMA-262 §Map/Set/WeakMap/WeakSet; MDN Keyed Collections; V8 blog: ES6 Collections"
updated_at: 2026-05-02
---

## 核心定义

ES6引入四类集合Map/Set/WeakMap/WeakSet，解决Object仅支持字符串/Symbol键的限制。Map: 键值对集合，任意值(包括对象/NaN/-0)作为键，插入顺序迭代(entries/keys/values)。Set: 唯一值集合，SameValueZero算法比较(===但NaN等于自身，-0等于+0)。底层实现：V8中Map/Set基于确定性哈希表(OrderedHashTable)，平均O(1)插入/删除/查找，N个条目内存约N×(8+8+16)字节。WeakMap: 键必须是对象(不允许原始类型)，键为弱引用——键对象被GC时对应条目自动移除，不可迭代、无size属性(因为GC行为不确定)。WeakSet: 对象弱引用集合——add只接受对象。WeakRef和FinalizationRegistry(ES2021)是更基础层弱引用机制。

## 关键结论

1.Map vs Object: Map保留插入顺序、任意类型键、优化频繁增删(size属性O(1) vs Object.keys O(n)) 2.WeakMap的核心用例：关联私有数据到DOM元素(HTML/SVG/DOM节点)→节点移除时自动清理 3.WeakMap实现私有属性: const privates=new WeakMap(); class Foo{constructor(){privates.set(this,{...})}} 4.Set的操作: 去重/交集/并集/差集——ES2025+将提供原生Set方法(.intersection/.union/.difference/.symmetricDifference) 5.WeakRef允许观察对象何时被GC(deref()返回undefined)——FinalizationRegistry注册GC后回调——但行为不确定不建议业务依赖 6.Map的迭代顺序与插入顺序一致(区别Object的无序/插入顺序) 7.WeakMap不能用于遍历/计数(count)——GC的不可预测性意味着内容会随时改变

## 关联知识点

[[JavaScript-内存管理与内存泄漏]] [[JavaScript-Iterator与Generator]] [[JavaScript-Symbol与元编程]]
