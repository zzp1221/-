---
title: "JavaScript-async/await与生成器"
course: JavaScript/TypeScript
chapter: 异步编程
difficulty: INTERMEDIATE
tags: [JavaScript, async, await, Generator, 异步, 微任务]
aliases: [JavaScript async/await, Async Functions]
source: "ECMA-262 §Async Functions; MDN async function; Jake Archibald《Async functions》blog series"
updated_at: 2026-05-02
---

## 核心定义

async function返回AsyncFunction类型——调用时创建AsyncGenerator对象(底层用Promise包装)。await expression等价于Promise.resolve(expression).then(回调)，暂停async函数执行，将await之后的代码作为microtask入队(PromiseJobs)。引擎实现上，async函数被转换为生成器+自动执行器的组合：Babel/TypeScript的__awaiter辅助函数将async转为switch case状态机+Promise.then链。ES2017原生async优化为直接在字节码层面(而非生成器转换)实现性能改进。async函数的返回值自动包装为Promise.resolve。顶级await(ES2022)允许在ESM模块作用域顶层使用await——模块图加载暂停等待该Promise处理完毕再继续依赖模块。

## 关键结论

1.await暂停async函数但不阻塞线程——其他macrotask/microtask正常调度 2.for await...of消费AsyncIterable(实现[Symbol.asyncIterator]的对象)，常用于流式读取 3.async generator: async function* gen(){yield await data}——返回AsyncGenerator，由for await消费 4.错误处理：await后的rejection可被try/catch捕获——等价.catch 5.性能：过度串行await()应改为await Promise.all([a(),b()])并行执行 6.误解：'await使代码执行变快'——await不提升速度，只是表达异步流程的语法糖 7.注意：async函数中的return value自动包装——与普通函数的return不同 8.意外await非Promise值无性能损失(Promise.resolve同步值直接返回)

## 关联知识点

[[JavaScript-Promise与微任务]] [[JavaScript-事件循环与Job Queue]] [[JavaScript-Iterator与Generator]]
