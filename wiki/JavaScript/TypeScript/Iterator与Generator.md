---
title: "JavaScript-Iterator与Generator协议"
course: JavaScript/TypeScript
chapter: 迭代协议
difficulty: INTERMEDIATE
tags: [JavaScript, Iterator, Generator, Symbol.iterator, yield*]
aliases: [JavaScript Iterator, Generator Protocol, Iterable]
source: "ECMA-262 §Iteration; MDN Iterators and generators; ExploringJS by Dr. Axel Rauschmayer"
updated_at: 2026-05-02
---

## 核心定义

ECMA-262定义两个独立协议：可迭代协议(Iterable)——对象实现[Symbol.iterator]方法返回迭代器；迭代器协议(Iterator)——对象实现next()方法返回{value, done}结果对象。所有内建可迭代类型：Array、String、Map、Set、TypedArray、arguments对象、NodeList、generator对象。function*声明生成器函数——调用返回Generator对象(同时实现Iterable和Iterator协议)，每次yield暂停并产出{value, done:false}，return时产出{value, done:true}。yield*委托另一个可迭代对象的所有值——等价于for(const val of iterable) yield val但带有双向通信通道(send/throw/return传播到委托的迭代器)。

## 关键结论

1.for...of循环内部调用iterator[Symbol.iterator]()获取迭代器然后消费 2.展开运算符(...)、解构([a,b]=arr)、Array.from()、new Map(iterable)均基于迭代器协议 3.生成器的.throw(err)和.return(value)方法: throw在yield点引发异常；return提前终止生成器(设置done:true) 4.可迭代的范围表达式(fx*): function* range(start,end) { for(let i=start;i<end;i++) yield i } 5.异步迭代器[Symbol.asyncIterator]返回{value,done}包装在Promise中——for await...of消费 6.惰性求值：生成器实现管道模式(fx* pipeline)——每个步骤仅当消费时才计算，内存友好 7.无限迭代器：自然数序列、斐波那契——生成器完美表达

## 关联知识点

[[JavaScript-async/await与生成器]] [[Python深入-生成器与协程]] [[JavaScript-Map/Set/WeakMap/WeakSet]]
