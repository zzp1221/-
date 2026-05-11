---
title: "TypeScript-装饰器与Reflect Metadata"
course: JavaScript/TypeScript
chapter: 装饰器
difficulty: INTERMEDIATE
tags: [TypeScript, 装饰器, Decorator, Reflect Metadata, TC39, NestJS]
aliases: [TypeScript Decorators, Reflect Metadata, TC39 Decorators Proposal]
source: "TC39 Decorators Proposal (Stage 3, 2024); TypeScript Handbook: Decorators; reflect-metadata package (Polyfill)"
updated_at: 2026-05-02
---

## 核心定义

TC39装饰器提案(Stage 3, 2024)定义装饰器为：type Decorator = (target, context) => { ... init, extra }。五种装饰器：Class/ClassMethod/ClassGetter/ClassSetter/ClassAutoAccessor/ClassField。context参数提供：kind(装饰类型)、name(成员名)、isStatic、isPrivate、addInitializer(注册init回调)→在类实例化或类定义完成时调用initializer链。装饰器在类定义时执行一次，不是在实例化时——实现了编译期横切关注点。TypeScript的experimentalDecorators使用旧版TC39提案(Stage 2)语法，与新版不完全兼容。reflect-metadata是ES7提议的polyfill——提供Reflect.defineMetadata(k,v,target)/Reflect.getMetadata(k,target)，在编译期通过emitDecoratorMetadata自动注入design:type/design:paramtypes/design:returntype元数据键。

## 关键结论

1.装饰器vs高阶函数：装饰器在类定义时执行可访问类上下文(可修改原型/静态成员)，高阶函数在调用时执行 2.context.addInitializer(cb)支持异步初始化——若回调返回Promise，实例化等待完成 3.design:开头的元数据由TypeScript compiler自动注入(emitDecoratorMetadata:true) 4.装饰器在框架中的应用：Angular(@Component/@NgModule)、NestJS(@Controller/@Module)、InversifyJS(IoC容器绑定) 5.参数装饰器(@Param/@Body)是TypeScript特有，未进入TC39标准 6.装饰器组合顺序：多个装饰器从下向上执行(与Python相同)；各装饰器初始化的addInitializer也是FILO 7.与Python装饰器对比：Python装饰器可以直接替换函数/类，JS装饰器通过init/finisher方法修改目标

## 关联知识点

[[TypeScript-类型系统]] [[Python深入-装饰器进阶]] [[JavaScript-Proxy与Reflect]]
