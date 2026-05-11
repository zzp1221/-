---
title: "JavaScript-Symbol与元编程"
course: JavaScript/TypeScript
chapter: 元编程
difficulty: ADVANCED
tags: [JavaScript, Symbol, 元编程, Well-known Symbols, Symbol.iterator]
aliases: [JavaScript Symbol, Well-known Symbols, JS Meta-programming]
source: "ECMA-262 §Symbol; MDN Symbol; ExploringJS Ch. Symbols by Dr. Axel Rauschmayer"
updated_at: 2026-05-02
---

## 核心定义

ECMA-262定义Symbol为第七种原始类型(undefined/null/boolean/number/bigint/string/symbol)。Symbol('desc')每次调用返回全局唯一的symbol值(描述仅用于调试toString)。Symbol.for('key')在全局Symbol注册表中查找或创建共享symbol(跨realm/module)。Well-known Symbols(@@xxx)是JavaScript元编程的接口：@@iterator(Symbol.iterator)定义可迭代协议；@@toPrimitive控制对象→原始值转换；@@hasInstance自定义instanceof行为；@@species控制派生对象构造器(Array.map返回的默认用原类型)；@@toStringTag定义Object.prototype.toString的标签；@@isConcatSpreadable控制Array.prototype.concat是否展开对象；@@asyncIterator定义异步迭代协议。这些symbol是语言级的钩子——引擎根据对象是否定义这些symbol触发定制行为。

## 关键结论

1.Symbol作为对象键不会出现在Object.keys/for...in中——可用Object.getOwnPropertySymbols获取(非私有,仅是隐藏) 2.自定义@@toPrimitive: 覆盖默认的valueOf→toString的优先级，接收hint('number'/'string'/'default') 3.为库添加@@iterator可使自定义集合支持for...of和展开运算符 4.Symbol.unscopables让with语句忽略某些属性(但with本身已不推荐) 5.为自定义类定义@@species: static get[Symbol.species](){return this}控制map返回的构造器类型 6.@@match/@@replace/@@search/@@split允许对象参与String.prototype对应方法(如正则替代方案)

## 关联知识点

[[JavaScript-Proxy与Reflect]] [[JavaScript-Iterator与Generator]] [[Python深入-元类编程]]
