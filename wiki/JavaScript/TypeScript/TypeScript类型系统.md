---
title: "TypeScript-类型系统"
course: JavaScript/TypeScript
chapter: 类型系统
difficulty: INTERMEDIATE
tags: [TypeScript, 类型系统, Structural Typing, Conditional Types, infer]
aliases: [TypeScript Type System, Structural Subtyping, TS Types]
source: "TypeScript Handbook; TypeScript Compiler docs (microsoft/TypeScript); TypeScript Deep Dive (Basarat)"
updated_at: 2026-05-02
---

## 核心定义

TypeScript是JavaScript的超集，提供渐进式(opt-in)结构化类型系统。核心构造：联合类型(A|B, 值具有任意一方的形状); 交叉类型(A&B, 值同时满足两方); 字面量类型('a'|2, 精确值类型); 条件类型(T extends U?X:Y, 类型级别的if/else); 映射类型({[K in keyof T]: Transformed}, 对T的每个属性做变换); 模板字面量类型(`prefix-${string}`, 字符串级别的联合类型)。结构化子类型：是否兼容不依赖继承声明，只比较结构——{x:number,y:number}可替代{x:number}。类型推导系统基于Hindley-Milner思想的变体，支持：变量类型推导、返回类型推导、泛型约束推导。编译后所有类型注解被完全擦除(对运行时无影响)。

## 关键结论

1.any禁用类型检查(危险——不应从any派生)；unknown安全——使用前必须类型收窄(typeof/instanceof/in) 2.never表示不可能值——用于穷尽性检查(default: const _exhaustive:never=x) 3.infer在条件类型内提取类型信息：type Returned<T>= T extends ((...args:any[])=>infer R)?R: never 4.keyof T返回T的所有键的联合类型；typeof获取值的类型——typeof window→Window类型 5.tsconfig strict模式包含：noImplicitAny/strictNullChecks/strictFunctionTypes等严格检查 6.声明合并：同名interface自动合并；namespace与class可合并以扩展功能 7.const assertion(as const)使类型收窄到最具体——对象转为readonly nested literal

## 关联知识点

[[TypeScript-装饰器与Reflect Metadata]] [[Python深入-类型注解与mypy]] [[JavaScript-ES模块vs CommonJS]]
