---
title: "JavaScript-ES模块vs CommonJS"
course: JavaScript/TypeScript
chapter: 模块系统
difficulty: INTERMEDIATE
tags: [JavaScript, ESM, CommonJS, import, require, Tree Shaking]
aliases: [ES Modules, CommonJS vs ESM, JavaScript Modules]
source: "ECMA-262 §Modules; Node.js docs: ECMAScript Modules; TC39 modules proposals"
updated_at: 2026-05-02
---

## 核心定义

ES模块(ECMA-262 §Modules)使用import/export声明式语法。导入：import defaultExport from 'mod'(默认导入)、import {named} from 'mod'(命名导入)、import * as ns from 'mod'(命名空间导入)。导出：export default expr(每个模块一个默认导出)、export const x=1(命名导出)、export {a as b}(重新导出)。ES模块是静态结构——import/export声明必须在模块最顶层(不能在if/函数中)，模块指定符必须是字符串字面量。这使编译器可静态分析模块依赖图，实现tree-shaking(消除未使用代码)。动态导入import(specifier)返回Promise，返回模块命名空间对象，在运行时异步加载。CommonJS用require()/module.exports——同步加载，运行时解析，值是导出对象的拷贝。

## 关键结论

1.ESM绑定是live binding(实时绑定)：导入方看到导出方的当前值(如果导出变量改变，导入方可见)；CJS是值的快照拷贝 2.循环依赖：CJS中未完成的模块导出可能不完整(部分属性undefined)；ESM通过live binding优雅处理 3.Node.js双模块系统：.mjs=总是ESM，.cjs=总是CJS；package.json设置 type:module 默认ESM 4.ESM自动启用strict mode；CJS不是严格的——这是常见的行为差异来源 5.WASI/Deno原生ESM；Node.js在ESM中不可用__dirname/__filename——用import.meta.url+fileURLToPath 6.ESM的import.meta提供模块元信息(.url=文件路径，.resolve=resolve指定符)

## 关联知识点

[[JavaScript-V8引擎执行模型]] [[TypeScript-类型系统]] [[Python深入-import系统]]
