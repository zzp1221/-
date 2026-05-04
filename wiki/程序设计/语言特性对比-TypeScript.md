---
title: 语言特性对比-TypeScript
course: 程序设计
chapter: 编程语言对比
difficulty: INTERMEDIATE
tags: [TypeScript, JavaScript, 渐进类型, 类型推断, 联合类型, 类型守卫, 接口, 泛型, Node.js]
aliases: [TypeScript, JavaScript Superset, Gradual Typing, Union Types, Type Guards]
source:
  - Boris Cherny《Programming TypeScript》
  - TypeScript Handbook (Microsoft)
updated_at: 2026-05-02

---

## 核心定义

TypeScript 由 Anders Hejlsberg（C# 的创造者）在 Microsoft 于 2012 年发布，是 JavaScript 的**类型超级集**——所有合法的 JavaScript 代码都是合法的 TypeScript 代码。TypeScript 编译为纯 JavaScript，运行在任何 JS 宿主环境（浏览器、Node.js、Deno、Bun）。TypeScript 的使命是将类型系统强加于动态的 JavaScript，兼具编译时安全与 JS 生态的完全兼容。

**核心特征**：
- **静态类型系统**（可选的渐进式——从 `any` 松散到 `strict` 严格可逐步升级）
- **类型推断**：无需显式类型注解在大多数常见情况下推断类型
- **面向对象**：类、接口、泛型、抽象类、访问修饰符——比 JavaScript 的 OOP 更正规
- **JS 生态兼容**：所有 JavaScript 库都能在 TypeScript 中用——通过 DefinitelyTyped 社区维护的类型定义（`@types/*`）
- **现代 JS 特性** + 类型：ES Next 提案可先行在 TS 中使用等待浏览器支持

**TypeScript 独有的类型特性**：
1. **联合类型**（Union Types）：`string | number` 表示值可以是两者之一。需要类型守卫（Type Guard）来缩小类型。
2. **交叉类型**（Intersection Types）：`A & B` 表示同时具有 A 和 B 的成员。
3. **字面量类型**（Literal Types）：`"success" | "error" | "loading"`——更精确的联合。
4. **判别联合**（Discriminated Unions）：结合字面量和联合——"Tagged Union / Algebraic Data Type" 在 TypeScript 的体现。如 `type Shape = {kind: "circle"; radius: number} | {kind: "rectangle"; w: number; h: number}`，`switch(shape.kind)` 自动推断分支类型。
5. **类型守卫**（Type Guard）：`typeof x === "string"` 在 if 块内 TypeScript 将 x 降低为 string 类型。
6. **映射类型**（Mapped Types）：`type Readonly<T> = { readonly [K in keyof T]: T[K] }`——在类型层面变换已有类型。
7. **条件类型**（Conditional Types）：`T extends U ? X : Y`，类型级别的三元算子——用于泛型逻辑。
8. **模板字面量类型**（Template Literal Types）：``type EventName = `on${Capitalize<string>}` `` → `"onClick" | "onChange"`。
9. **keyof 和索引访问类型**：`type PointKeys = keyof Point` → `"x" | "y"`。

**配置**（`tsconfig.json`）：通过 flags 调整严格程度——`strict`（开启所有严格检查）、`noImplicitAny`（隐式 any 警告）、`strictNullChecks`（区分 T 和 T | null 处理 null 安全性）、`noUncheckedIndexedAccess`（索引后可能 undefined）。

**适用场景**：任何大型 JavaScript 项目——前端（React, Vue, Svelte）、后端（Node.js/Express/NestJS）、全栈（Next.js, Remix）、跨平台（React Native, Electron）、Deno（内置 TS 支持）、Bun（原生 TS）。

## 关键结论

- TypeScript 是"结构类型"——两个类型如果成员相同即兼容（即便没有显式 `implements` 声明），这对应了 JS 的鸭子类型
- 严格模式是 TypeScript 的核心价值——宽松的 TS 不能捕获多少 bug
- TypeScript 的类型系统是图灵完备的——类型层面的复杂逻辑（递归类型、条件类型）可能使 `tsc` 编译缓慢或 IDE 卡顿
- AnyScript 是使用 TS 的最差方式——到处 `any` 放弃了类型安全但承担了类型注解的语法负担
- 编译产出的 JavaScript 不包含任何运行时类型检查——类型仅在编译时存在

## 易错点

1. TypeScript 在运行时不存在——编译后类型被擦除，运行时无法进行 `instanceof Interface` 检查
2. `any` 是可传染的——操作涉及 `any` 后结果也变成 `any`（`let x: any = ...; let y: number = x;` 不会报错）
3. `as` 类型断言不是运行时强制转换——`let x = y as number` 如果 y 是 string 不会在运行时转为 number
4. `enum` 存在 JavaScript 的诟病——默认产生含反向映射的 IIFE 代码，推荐 `const enum`（编译时内联）或字符串联合替代

## 例题

**例题1**：实现类型安全的 `groupBy` 函数：

```typescript
function groupBy<T, K extends PropertyKey>(
    arr: T[], keyFn: (item: T) => K
): Record<K, T[]> {
    const result = {} as Record<K, T[]>;
    for (const item of arr) {
        const key = keyFn(item);
        (result[key] ??= []).push(item);
    }
    return result;
}
// 使用
const grouped = groupBy(users, u => u.role);  // Record<string, User[]>
```

**例题2**：解释 TypeScript 的 `infer` 关键字及用途。

**解答**：`infer` 用于在条件类型中推断（声明）类型变量——仅在条件类型的 `extends` 子句中使用。
```typescript
type ReturnOf<T> = T extends (...args: any[]) => infer R ? R : never;
type Fn = (x: number) => string;
type R = ReturnOf<Fn>;  // string (推断 R = string)
```
`infer` 也可用于选择性地取出类型的参数：`type FirstArg<T> = T extends (first: infer F, ...rest: any[]) => any ? F : never;`。

## 关联页面

[[静态类型vs动态类型]] [[类型系统]] [[面向对象编程]] [[函数式编程]]
