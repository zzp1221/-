---
title: TDD测试驱动开发
course: 软件工程
chapter: 软件测试
difficulty: INTERMEDIATE
tags: [TDD, 测试驱动开发, Red-Green-Refactor, 单元测试, 重构, ATDD, BDD]
aliases: [Test-Driven Development, 测试驱动开发, 测试先行]
source:
  - Kent Beck《Test-Driven Development: By Example》
updated_at: 2026-05-02

---

## 核心定义

测试驱动开发（TDD, Test-Driven Development）是一种将测试从"事后验证"前移到"事前设计"的软件开发方法论，由 Kent Beck 在极限编程（XP）中推广。TDD 的核心循环是 Red-Green-Refactor：(1) **Red（红）**：先写一个失败（通过不了）的单元测试——定义你要实现的功能的期望行为；(2) **Green（绿）**：以最快最简单的方式写出恰好让测试通过的代码——不追求完美，只求通过；(3) **Refactor（重构）**：在测试全部通过的前提下，优化代码结构——消除重复、提高可读性、应用设计模式。循环不断重复。

TDD 的两条基本法则（Kent Beck）：(1) 除非你有一个失败的自动化测试，否则不要写任何一行生产代码；(2) 先消除重复（即重构）。TDD 不是关于测试本身——它是一种**以测试为驱动的设计方法**（Test-Driven Design），产生的代码天然具备高可测试性、松耦合和清晰的接口。

**ATDD**（Acceptance Test-Driven Development，验收测试驱动开发）：在 TDD 之上扩展到需求层面——在开始编码前先与客户/PO一起定义验收测试标准。验收测试成为"活文档"，定义了功能完成的标准。

**BDD**（Behavior-Driven Development，行为驱动开发）：Dan North 提出的 TDD 演进，使用自然语言（Gherkin 语法的 Given-When-Then）描述行为，使技术团队和业务团队可以共享同一份"规约"。工具：Cucumber、SpecFlow、JBehave。

## 关键结论

- TDD 的精髓在"驱动设计"而非"测试"——测试是副产品，设计是主产品
- TDD 迫使开发者从**使用者视角**思考接口——你写的第一个代码是"调用代码"（测试代码中的 SUT），然后才去实现
- 研究表明 TDD 可减少 40-80% 的生产缺陷密度（缺陷数/代码量），但前期开发时间增加约 15-35%
- 重构是 TDD 不可跳过的一步——跳过重构将积累技术债务
- ATDD/BDD 将 TDD 从"代码层"提升到"业务层"，使验收标准可自动化执行
- TDD 适用性：适合逻辑密集型代码（库、框架、业务逻辑），不适合 UI 布局（视觉性质无法自动化断言）和探索性/原型开发

## 易错点

1. TDD = 先写所有测试再写代码：TDD 是**渐进式**的——一次只写一个测试，让它通过，重构，再写下一个
2. Red 阶段写过于复杂的测试：一个 test case 应该失败仅因为"缺少功能"，而非测试本身有 bug——测试也应保持简单
3. 只写"Happy Path"测试：TDD 同样需要覆盖边界条件和异常路径——负向测试也是 TDD 的组成部分

## 例题

**例题1**：用 TDD 方法开发一个"斐波那契数列"函数 `fib(n)`。展示 Red-Green-Refactor 循环的 2-3 步。

**解答**：
Step 1 (Red): 写测试 `assertEquals(0, fib(0))`。编译失败——`fib` 函数不存在。
Step 1 (Green): 实现 `int fib(int n) { return 0; }`。测试通过。
Step 2 (Red): 添加测试 `assertEquals(1, fib(1))`。测试失败。
Step 2 (Green): 修改为 `return n == 0 ? 0 : 1;`。测试通过。
Step 3 (Red): 添加 `assertEquals(1, fib(2))`。测试失败。
Step 3 (Green): 修改为 `if (n <= 1) return n; return fib(n-1) + fib(n-2);`。测试通过。
Step 3 (Refactor): 无重复代码，无需重构。继续下一步。

**例题2**：BDD 如何帮助弥合"业务-技术"沟通鸿沟？

**解答**：BDD 的 Given-When-Then 格式是自然语言，业务人员可直接阅读和编写（或用工具辅助编写）。例如：
```
Scenario: 成功取款
  Given 账户余额为 1000 元
  When 用户取款 200 元
  Then 账户余额应为 800 元
  And 取款记录应被保存
```
这份规约同时是需求文档、验收标准、和自动化测试。技术团队和业务团队围绕同一份文档协作，消除了传统"需求文档→隔空理解→代码→测试"的信息衰减。

## 关联页面

[[软件测试-单元与集成测试]] [[黑盒白盒测试]] [[敏捷开发-XP]] [[重构]]
