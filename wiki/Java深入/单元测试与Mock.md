---
title: "Java深入-单元测试与Mock"
course: Java深入
chapter: 工程质量
difficulty: BASIC
tags: [Java, JUnit, Mockito, 单元测试, TDD]
aliases: [JUnit, Mockito, Java Testing]
source: "JUnit 5 User Guide; Mockito官方文档; Meszaros《xUnit Test Patterns》"
updated_at: 2026-05-02
---

## 核心定义

JUnit 5是Java主流测试框架。核心注解：@Test标记测试方法、@BeforeEach/@AfterEach(每个测试前后)、@BeforeAll/@AfterAll(所有测试前后,必须static)、@DisplayName(人类可读的测试名)、@ParameterizedTest(参数化测试配合@ValueSource/@CsvSource)、@RepeatedTest(重复测试)。断言：assertEquals/assertTrue/assertThrows/assertTimeout/asserAll。Mockito提供模拟(mocking)对象：Mockito.mock()创建伪对象,when().thenReturn()预设行为,verify()检查调用。

## 测试最佳实践

FIRST原则：Fast(快速)、Independent(独立)、Repeatable(可重复)、Self-validating(自验证)、Timely(及时编写)。测试金字塔：单元测试(大量,快,不依赖外部)→集成测试(中等,依赖DB/IO)→端到端测试(少量,全链路,慢脆)。单元测试验证行为而非方法——测试公共API的逻辑而非每个setter。测试命名：shouldExpectedBehavior_whenCondition()。mock只在被测试单元有外部协作者时使用——mock自己类型的测试是反模式。

## 关键结论

1. 不要mock你不拥有的类型(用test double的wrapper或fake) 2. ArgumentCaptor在需要验证传递给mock的参数中的值 3. thenReturn vs thenAnswer——后者提供动态响应(根据输入计算返回值) 4. @InjectMocks自动注入mock依赖(Spring的@MockBean替代) 5. 每个测试只验证一个行为(单一断言虽好但非铁律——简洁>绝对) 6. 测试覆盖率(行覆盖率/分支覆盖率)达到80%合格

## 关联知识点

[[Java深入-设计模式实战]] [[Go语言-测试与基准测试]] [[软件工程-软件测试策略]]
