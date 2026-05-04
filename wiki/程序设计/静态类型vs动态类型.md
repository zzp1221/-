---
title: 静态类型vs动态类型
course: 程序设计
chapter: 类型系统
difficulty: BASIC
tags: [静态类型, 动态类型, 渐进类型, 类型安全, 类型推断, TypeScript, mypy, 鸭子类型, 名义类型]
aliases: [Static Typing, Dynamic Typing, Gradual Typing, Duck Typing, Nominal Typing]
source:
  - Benjamin C. Pierce《Types and Programming Languages》
  - Robert W. Sebesta《Concepts of Programming Languages》
updated_at: 2026-05-02

---

## 核心定义

静态类型（Static Typing）和动态类型（Dynamic Typing）是编程语言类型检查时机的不同策略。静态类型在编译时确定和检查类型，动态类型在运行时检查类型。两种策略代表了类型安全性和开发灵活性之间的权衡。

### 静态类型

类型是变量或表达式的固有属性——在编译时绑定且在变量生命周期内不变。编译器利用类型信息做类型检查和优化。

**优势**：
- 编译时捕获类型错误——不用运行到代码行就能发现
- IDE 支持——代码补全、重构、跳转定义无歧义（编译器有精确的类型图）
- 运行时无类型检查开销——编译后可丢弃类型信息
- 文档价值——函数签名 `(int, string) → User` 成为自文档

**劣势**：
- 代码量更多——需要类型注解（现代语言通过类型推断消减）
- 某些动态模式需要更高阶的类型系统（泛型、Higher-Kinded Types）才能表达

**子类别**：
- **显式类型**（Manifest Typing）：开发者必须声明类型（Java, C# 大部分, C++ `int x;`）
- **类型推断**（Type Inference）：编译器可从上下文中推断大部分变量类型（Haskell, Rust, OCaml, TypeScript, Scala）。Hindley-Milner 类型推断可完全免去类型注解

### 动态类型

类型是值的属性而非变量——同一变量可先后持有不同类型的值。类型检查在运行时发生——操作实际作用于值时。

**优势**：
- 灵活性——无需前期定义类型结构即可编写代码（原型、脚本）
- 代码表达力——元编程、鸭子类型、运行时创建类型（无需类型体操）
- 开发速度快——无类型编译步骤，修改即运行

**劣势**：
- 运行时类型错误——拼写错误的属性、传递错误的类型都在运行时暴露（可能在生产环境）
- IDE 支持较弱——无法确定变量的可用方法和属性
- 性能开销——运行时类型检查和动态分派

**代表语言**：Python, Ruby, JavaScript, PHP, Lua

### 鸭子类型（Duck Typing）

动态类型的标志性哲学："如果它走起来像鸭子，叫起来像鸭子，那它就是鸭子。"——即不检查对象的明确类型，而检查对象是否有特定方法或属性。Python/Ruby/JavaScript 广泛使用鸭子类型。

```python
def print_all(iterable):
    for item in iterable:    # 不要求 iterable 是特定类型，只需支持迭代协议
        print(item)
# 可接受 list, tuple, set, generator, 或任何自定义的 __iter__ 类
```

### 名义类型、结构类型、鸭子类型

- **名义类型**（Nominal Typing）：类型由名称和定义唯一决定——`class Dog` 和 `class Cat` 即使有相同特征也不会被视为兼容（Java/C#/Rust）
- **结构类型**（Structural Typing）：类型由结构决定——若 A 有 B 所需的所有成员，则 A 兼容 B（TypeScript 的接口、Go 的接口、Scala 的结构类型）
- **鸭子类型**：运行时决定——不事先声明关系，依赖方法/属性的存在性

### 渐进类型（Gradual Typing）

折中方案：在动态类型语言中选择性地添加静态类型注解——可精确注解关键部分而保留其他部分的灵活性。TypeScript（JS 的超集）、Python 3.5+ 的 type hints + mypy、Ruby 3+ 的 RBS、PHP 7+ 的类型声明。TypeScript 是渐进类型最成功的实现——开发者可在项目级别通过 `tsconfig.json` 的 `strict` 模式逐步迁移到完全的类型安全。

**类型检查策略的比较**：

| 意图 | 静态 | 动态 |
|------|------|------|
| 何时发现错误 | 编译时 | 运行时 |
| 变更成本 | 较繁琐（更新多个文件类型） | 较简单 |
| 原型速度 | 较慢 | 快 |
| 重构安全性 | 编译器保证（显式/推断） | 依赖测试覆盖 |
| 大型项目适合度 | 高 | 中（需大量测试） |

## 关键结论

- 静态/动态不是完全对立的——大多数现代动态语言都支持可选的类型注解（渐进类型）
- 类型系统是"错误发现时间"与"开发速度"的权衡——将错误从运行时前移到编译时
- Haskell 证明了：静态类型不意味着"必须写大量类型声明"——类型推断让代码看起来几乎与动态类型一样简洁
- 动态类型的"快速"是在小规模/短期项目中真实存在的，但在大规模/长期项目中，缺少编译时安全网导致的调试和维护成本远超写类型注解的时间

## 易错点

1. "静态类型语言一定比动态类型语言慢" —— 错误：C/Rust/Go 是静态类型，运行速度超出所有动态类型语言
2. "动态类型 = 没有类型" —— 错误：动态类型的值是强类型的（Python 的 `"1" + 1` 报 TypeError），类型信息存储在值上随运行时检测
3. 将 Python 类型 hint 当成运行时会强制——类型提示仅用于静态检查器（mypy）、IDE，运行时完全忽略（Python 是动态强类型，不会在运行时报错类型不匹配）

## 例题

**例题1**：什么是"表达力 vs 安全性"在类型系统中的体现？给出示例。

**解答**：类型系统越丰富可表达的不变量越多（安全性），但编写代码需要更多注解（可能降低表达力短期的灵活性）。例如 Rust 的生命期系统可保证无悬挂指针（安全性），但需要注明 `'a` 生命期参数使函数签名复杂（`fn find<'a>(haystack: &'a str, needle: &str) -> Option<&'a str>`）。相比之下 C 允许自由传递任何指针（表达力灵活）但容易产生悬挂指针（安全性弱）。这里的权衡不是"谁好"而是"谁适合特定场景"。

**例题2**：将以下 Python 动态代码改写为 TypeScript 渐进类型：

```python
def process(data):
    result = []
    for item in data:
        result.append({"id": item["id"], "name": item["name"].upper()})
    return result
```

**解答**：
```typescript
interface InputItem { id: number; name: string; }
interface OutputItem { id: number; name: string; }

function process(data: InputItem[]): OutputItem[] {
    return data.map(item => ({ id: item.id, name: item.name.toUpperCase() }));
}
```
TypeScript 的类型注解允许编译时检查 `item["id"]` 和 `item["name"]` 确实存在且类型正确——拼写错误（如 `item["naem"]`）在编译时即被发现，而 Python 版本需运行时才会报 KeyError。

## 关联页面

[[类型系统]] [[泛型编程]] [[编译型vs解释型语言]] [[程序设计概述]]
