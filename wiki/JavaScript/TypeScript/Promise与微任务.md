---
title: "JavaScript-Promise与微任务队列"
course: JavaScript/TypeScript
chapter: 异步编程
difficulty: INTERMEDIATE
tags: [JavaScript, Promise, microtask, then, catch, allSettled]
aliases: [JavaScript Promise, Microtask Queue, Promise Combinators]
source: "ECMA-262 §Promise; Promises/A+ specification; MDN Using Promises"
updated_at: 2026-05-02
---

## 核心定义

ECMA-262定义Promise为表示异步操作最终完成或失败的对象——内部[[PromiseState]]为pending/fulfilled/rejected。new Promise((resolve,reject)=>{...})中executor同步执行。.then(onFulfilled,onRejected)返回新Promise(链式调用——实现方法链)。.then回调被放入PromiseJobs队列(即microtask队列)而非调用栈——保证总是在当前execution context完成后异步执行。Promise.resolve(值)/Promise.reject(原因)创建已决议Promise。底层算法：NewPromiseCapability(executor)→CreateResolvingFunctions(promise)→resolve/reject闭包持有promise引用。Promise的thenable识别(Promise.resolve检查[Symbol.species]或.then方法)——用于coerce非Promise值。

## 关键结论

1.Promise.all等待所有resolve(任一reject即整体reject短路)；Promise.allSettled等待全部settled(含失败原因) 2.Promise.race: 任一settled立即返回——适合超时模式；Promise.any: 任一fulfilled即成功(全部rejected才reject) 3.Promise.prototype.finally()无论成功失败都执行(不改变返回值)，后跟.then链继续处理 4.unhandledRejection: 未加.catch的Promise rejection在microtask清空后触发unhandledrejection事件(Node.js process: warning) 5.executor中的同步throw等价于reject——Promise自动捕获异常 6.Promise.resolve(promise)直接返回该promise(不创建新包装)——这是resolve不同于new Promise的关键区别

## 关联知识点

[[JavaScript-事件循环与Job Queue]] [[JavaScript-async/await与生成器]] [[Python深入-asyncio事件循环]]
