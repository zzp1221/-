---
title: "JavaScript-Proxy与Reflect API"
course: JavaScript/TypeScript
chapter: 元编程
difficulty: ADVANCED
tags: [JavaScript, Proxy, Reflect, 元编程, 拦截, Vue3]
aliases: [JavaScript Proxy, Reflect API, Meta-programming]
source: "ECMA-262 §Proxy; MDN Proxy and Reflect; Vue 3 Reactivity in Depth Guide"
updated_at: 2026-05-02
---

## 核心定义

ECMA-262 §28定义Proxy对象: new Proxy(target, handler)创建目标对象的虚拟包装。handler可拦截13种内部方法(internal methods / 规范操作): [[Get]](get)/[[Set]](set)/[[HasProperty]](has)/[[Delete]](deleteProperty)/[[OwnPropertyKeys]](ownKeys)/[[GetPrototypeOf]]/[[SetPrototypeOf]]/[[IsExtensible]]/[[PreventExtensions]]/[[GetOwnProperty]](getOwnPropertyDescriptor)/[[DefineOwnProperty]](defineProperty)/[[Call]](apply, 针对函数)/[[Construct]](construct, new操作符)。Reflect API提供与proxy handler trap一一对应的默认行为方法——在每个trap中可调用Reflect方法转发到原始行为(如Reflect.get(target,prop,receiver))。Proxy可透明拦截——对使用者不可见(除非使用===与target比较)。

## 关键结论

1.Vue 3的响应式系统核心基于Proxy(替代Vue 2的Object.defineProperty)——可检测属性添加/删除/数组index赋值/Map/Set 2.Reflect的作用：确保[[Get]]/[[Set]]等操作的receiver参数正确传递，维持原型链上this的指向 3.可撤销Proxy(Proxy.revocable): 为临时敏感对象创建代理，在需要时调用revoke()永久关闭所有访问 4.trap的get/set需对invariant检查——如set的返回值必须为truthy且不可报告添加属性的假操作 5.Proxy限制：不适用于内建类型(Set/Map/Date)内部方法需要this绑定到原始对象——用receiver解决 6.Proxy的性能开销：每次操作经过trap(slow path)——热路径不适合大量Proxy 7.Proxy+Reflect可用于：负索引数组、默认属性值(不存在时返回自定义值)、属性访问日志

## 关联知识点

[[JavaScript-Symbol与元编程]] [[JavaScript-Iterator与Generator]] [[Python深入-描述符协议]]
