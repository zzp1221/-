---
title: 设计原则-DRY-KISS-YAGNI
course: 程序设计
chapter: 设计原则
difficulty: BASIC
tags: [DRY, KISS, YAGNI, 设计原则, 代码复用, 简单性原则, 过度设计, 代码重复]
aliases: [DRY Principle, KISS, YAGNI, Don't Repeat Yourself, Keep It Simple]
source:
  - Andrew Hunt & David Thomas《The Pragmatic Programmer》
  - Robert C. Martin《Clean Code》
updated_at: 2026-05-02

---

## 核心定义

DRY、KISS、YAGNI 是软件工程中三个最核心的设计原则，与 SOLID 互补——如果说 SOLID 关注"如何组织代码"，那么 DRY/KISS/YAGNI 关注"代码应该是什么样的"。

### DRY - 不要重复自己（Don't Repeat Yourself）

**定义**（《The Pragmatic Programmer》, Hunt & Thomas）："每一条知识在系统中必须有单一、不模糊的权威表示。"

DRY 针对的不是"代码重复"而是**知识/概念重复**。两块代码看起来文本相同但代表不同知识——它们不是重复；两块代码看起来不同但代表相同的知识——它们是 DRY 违规。

**DRY 的维度**：
- 算法重复：相同的逻辑在多个地方实现 → 提取为函数
- 数据定义重复：多个系统间重复定义相同的数据结构 → 单一来源（Single Source of Truth）
- 文档/注释重复：代码和注释说同一件事但注释过时 → 消除无必要注释（代码自解释）
- 需求/规格重复：SRS 和测试用例重复定义相同需求 → 可执行规格（BDD）

**DRY vs 重复代码**：
```python
# 看起来是重复代码但不是 DRY 违规——它们代表不同的知识
def validate_username(name):
    if len(name) < 3: raise ValueError("Username too short")
def validate_password(pwd):
    if len(pwd) < 8: raise ValueError("Password too short")
# 业务规则不同（3 vs 8），变化原因不同——强行合并反而违反 SRP
```

**WET**（Write Everything Twice / Waste Everyone's Time）是 DRY 的反面。Rule of Three（三法则）：一段代码重复出现第三次时才提取抽象——过早抽象比重复更有害。

### KISS - 保持简单傻瓜（Keep It Simple, Stupid）

**定义**：简单性是设计的目标——避免不必要的复杂性。系统应足够简单到让开发人员（包括未来的你）能够快速理解。

Kelly Johnson（洛克希德臭鼬工厂）提出此原则为工程设计原则。在软件工程中的体现：
- 使用最简单的可满足需求的技术——不需要最新最复杂的框架
- 代码的读者比作者多——为可读性优化
- 如果精妙的技术只有你能理解，那就是不必要地复杂

**简单性的标准**：新开发者能否在 10 分钟内理解这个模块的作用？如果可以，那可能是 KISS；如果不能，可能有不必要的复杂性。

**KISS 的敌人**：
- 过度使用设计模式——用工厂模式为 2 个 if-else 处理不值得
- 过早优化——为"可能的性能需求"牺牲可读性
- 过度设计——为"将来可能有"的功能搭架子

### YAGNI - 你不会需要它（You Aren't Gonna Need It）

**定义**（Extreme Programming 实践）：不要在"可能需要"的基础上添加功能、代码、接口——直到你真的需要它时才添加。

YAGNI 是针对"过早设计"（Premature Design）的防御——为假设的需求编写代码有多个隐性成本：(a) 编写、测试、文档当前不需要的代码浪费时间；(b) 额外代码增加系统复杂性和维护负担；(c) 假设的需求可能与实际未来的需求不同（但废弃代码却遗留了）。

```java
// YAGNI 违规
interface UserRepository {
    User findById(Long id);
    List<User> findByEmail(String email);          // 现在就需要
    List<User> findAllByRoleInRegion(...);          // "以后可能需要"
    User findByPhoneAndVerificationCode(...);       // "某天可能"
    Page<User> searchWithFullText(String query);    // "将来规划"
}
// 遵守 YAGNI：先实现现在需要的，实际需要时再加
interface UserRepository {
    User findById(Long id);
    List<User> findByEmail(String email);
}
```

**YAGNI vs 扩展点**：有成本的可扩展性设计（预留接口、插件系统）应基于实际证据——"以前至少有过三次类似变化才预留扩展点"（Rule of Three）。但有时零成本扩展（如遵循 OCP 的接口设计）可以提前设计。

**YAGNI 的边界**：不适用"安全关键系统"（如航天、医疗设备）——这些系统对未来的故障模式有精确分析和设计要求，不能"等需要时再加"。

## 关键结论

- DRY 不是说"代码块完全一样就合并"——抽象应基于语义（变化的原因）而非巧合的文本相似
- KISS 不是"写得简单"——它是"设计得简单"，对复杂的问题简单方案不总能存在（需要团队能力识别可简化的部分）
- YAGNI 是最被误解的原则——它不是拒绝前瞻性设计，而是拒绝基于"猜测"的复杂性
- 三者的共同点：降低系统复杂性、提升可维护性、减少浪费
- Rule of Three 是平衡过度抽象和重复的实用经验法则

## 易错点

1. 过度 DRY 导致高耦合——"把每一次重复都抽象导致所有不相关的事务都绑在一起"
2. 将重复代码视为 DRY 违规，忽略了"重复类型但不同语义"的情况——提取后发现模块间通过一个抽象产生了不希望有的耦合
3. KISS 被误用为"不学习新技术"的借口——KISS 意思是"用合适的工具做合适的事"，不是"只用你知道的工具"
4. YAGNI 忽视核心架构——如安全性、合规性这些不是"以后能加"的，必须前期规划

## 例题

**例题1**：判断以下改动是应用了 DRY 还是过度 DRY：
原始代码：订单创建时发送两个格式略有不同的确认邮件——`sendEmailToCustomer(order)` 和 `sendEmailToAdmin(order)`（两个独立函数）。
"优化"：提取一个 `sendEmail(order, recipient_type)` 函数，在类型参数内区分不同格式。

**解答**：这是过度 DRY。虽然"两个函数看起来很像"但它们代表不同的知识——客户确认邮件关注体验（温和用语、营销链接），管理员通知关注运营信息（金额、库存）。两个邮件的变化原因是互不关联的——将两者合并为同一个函数耦合了独立的业务逻辑。Rule of Three：相同变化出现了三次以上才提取。

**例题2**：评估以下场景——架构师决定在第一个版本加入消息队列、读写分离、分库分表、DDD，而软件当前只有 10 个用户。违反了哪些原则？

**解答**：违反了 YAGNI 和 KISS。(a) 10 用户的 MVP 单数据库实例已足够；(b) 大量基础设施代码增加系统复杂性（KISS 违规）；(c) 团队的生产力被淹没在"未来可能"的架构复杂度中而忽略了交付真正的业务价值；(d) 分库分表、消息队列都有运维成本和认知负担；(e) 当业务发展到真正需要时再添加这些复杂度即可（以当前架构的模块化/接口化设计也是较低成本的扩展点预留）。

## 关联页面

[[设计原则-SOLID]] [[模块化与内聚耦合]] [[程序设计概述]]
