---
title: 单元测试与Mock
course: 程序设计
chapter: 测试
difficulty: INTERMEDIATE
tags: [单元测试, Mock, Stub, 测试框架, 测试覆盖, JUnit, pytest, 测试替身, 依赖注入]
aliases: [Unit Testing, Mock, Stub, Test Double, Dependency Injection, TDD]
source:
  - Gerard Meszaros《xUnit Test Patterns》
  - Kent Beck《Test-Driven Development: By Example》
updated_at: 2026-05-02

---

## 核心定义

单元测试（Unit Testing）是验证程序中最小可测试单元（通常是一个函数或方法）行为是否正确的自动化测试。Mock 是测试替身（Test Double）的一种，模拟外部依赖的行为以在隔离环境中测试单元代码。

**单元测试的特征**（FIRST 原则）：
- **F**ast（快）：单个测试在毫秒级完成，整个套件在分钟内完成
- **I**solated（独立）：测试之间不互相依赖，可以以任何顺序运行
- **R**epeatable（可重复）：每次运行结果相同——不依赖外部环境（网络、数据库、时间）
- **S**elf-Validating（自验证）：测试应返回 PASS/FAIL 明确结果，无需人工解释
- **T**imely（及时）：在编写生产代码的同时编写测试（TDD 中是先写测试）

**AAA 模式**（Arrange-Act-Assert）：
1. Arrange：准备测试数据和被测对象状态
2. Act：执行被测试的操作
3. Assert：验证结果是否符合预期

```python
def test_transfer_money():
    # Arrange
    account = BankAccount(balance=100)
    # Act
    result = account.withdraw(30)
    # Assert
    assert result == True
    assert account.balance == 70
```

**测试替身**（Test Double）的种类（Meszaros）：

1. **Stub**（桩）：返回预设固定的响应用于控制测试环境。如 `stub_weather_api` 返回固定温度 25（不验证它是否被调用）。
2. **Mock**（模拟）：类似 Stub 但还验证交互行为——被调用了几次、以什么参数调用。如 `mock_email_service.expects('send').with_args(user, 'welcome')`。
3. **Fake**（虚拟实现）：真实对象的一个有效但简化的轻量实现。如用内存中的 Map 替代真实数据库 `FakeUserRepository`。
4. **Spy**（间谍）：在真实对象基础上记录调用信息（用于事后检查）。区别于 Mock——Spy 通常包装真实对象而非完全替代。
5. **Dummy**（空对象）：仅用于满足参数列表但实际不被使用——`new User(null, null, null)`。

**Mock 的应避免模式**：
- 过度 Mocking——mock 太多依赖导致测试是"mock 的测试"而非"代码逻辑的测试"
- Mock 不匹配实现细节——Mock 的预期与实际实现脱钩，重构导致测试误报失败
- Mock 某个方法后又调用其真实实现（partial mock）——意图混乱

**依赖注入（DI）和可测试性**：依赖注入是实现可 Mock 代码的关键——将依赖从构造函数的参数传入而非在类内部 new 出来。`class OrderService(orderRepository: OrderRepository)` 可在测试中注入 FakeOrderRepository。

**各语言测试框架**：
- Java：JUnit 5, Mockito, AssertJ, TestNG
- Python：pytest, unittest, mock (标准库)
- JavaScript/TypeScript：Jest, Vitest, Mocha, Chai, Sinon.js
- Go：testing 包（标准）, testify
- Rust：内置 `#[test]`, `cfg(test)`, mockall/proptest

**测试覆盖率**（Coverage）：衡量测试覆盖的生产代码比例。行覆盖（Line）、分支覆盖（Branch）、路径覆盖（Path）、条件覆盖（Condition/Decision）——行覆盖最容易度量但也是最弱的，达到了 100% 行覆盖不等于充分测试。重点应是"高风险高复杂度的核心逻辑"达到高覆盖，而非追求覆盖率指标本身。

**属性测试**（Property-Based Testing / QuickCheck）：生成大量随机输入验证函数的不变式属性——`for all valid inputs, f(x, y) = f(y, x)`。比手写用例更可能发现边界 bug。工具：Haskell QuickCheck, Python Hypothesis, Java jqwik, Rust proptest。

## 关键结论

- 单元测试的目标是快速反馈——而非覆盖所有可能的 bug。集成测试和端到端测试覆盖单元测试难以覆盖的场景
- Test Double 的选择："Mock 行为验证，Stub 状态验证"——过度使用 Mock 会出现测试耦合实现细节的问题
- 可测试性影响设计——若代码难以测试（无法注入依赖），应反思设计（高耦合、违反 DIP）
- DI 是"可测试性"的最佳实践——构造函数注入优于字段注入

## 易错点

1. 测试之间共享可变状态——全局变量、数据库未回滚导致测试顺序依赖（Flaky Tests）
2. Mock 最终类或静态方法——难以 mock 则提示设计需改进（面向接口而非具体实现）
3. 测试通过但 assert 未真正验证——误写 `assertTrue(true)` 或忘记加 assert（Jest 的 `expect` 忘记 `.toXxx` 返回未断言的 Promise）
4. 过度 mock 导致测试只测了 mock 配置——mock 配置与真实依赖不同步，代码正确但测试通过后生产环境失败

## 例题

**例题1**：为以下函数写单元测试——使用 Stub 而非真实 API 调用：

```python
def is_prime(n: int) -> bool:
    if n < 2: return False
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0: return False
    return True
```

**解答**：
```python
import pytest
@pytest.mark.parametrize("n,expected", [
    (1, False), (2, True), (3, True), (4, False),
    (5, True), (9, False), (11, True), (25, False),
    (97, True), (10**9 + 7, True)
])
def test_is_prime(n, expected):
    assert is_prime(n) == expected
```
参数化测试（`pytest.mark.parametrize`）——测试多个输入而无需编写重复代码。

**例题2**：何时使用 Fake vs Mock 替换数据库依赖？

**解答**：
Fake（内存数据库 / List Repository）：当需要测试多步数据流——"保存用户 → 检索用户 → 更新属性 → 再次检索"。Fake 可以维护状态并返回正确的累积结果。集成测试比重高时用 Fake。
Mock（Mockito/Patch）：当需要验证特定的方法调用——"save 方法被调用了两次；第二次带有正确的更新后的对象"。Mock 可精确验证交互次数和参数。单元测试比重高时用 Mock。
误区：Mock 了 `findById` 返回固定的 `User`，然后测试中调用 `save(user)`、再 `findById` 期望返回更新后的——Mock 无法反映"保存后再查询"的语义（第二次 Mock 与第一次返回相同）。需要 Fake 来真实模拟存储。

## 关联页面

[[TDD测试驱动开发]] [[软件测试-单元与集成测试]] [[异常处理]] [[设计原则-SOLID]]
