---
title: 设计原则-SOLID
course: 程序设计
chapter: 设计原则
difficulty: INTERMEDIATE
tags: [SOLID, 单一职责, 开闭原则, 里氏替换, 接口隔离, 依赖反转, 设计原则, 面向对象]
aliases: [SOLID Principles, Single Responsibility, Open-Closed, Liskov Substitution]
source:
  - Robert C. Martin《Clean Architecture》
  - Bertrand Meyer《Object-Oriented Software Construction》
updated_at: 2026-05-02

---

## 核心定义

SOLID 是面向对象编程和设计的五个基本原则的缩写，由 Robert C. Martin（Uncle Bob）在 2000 年代推广。遵循 SOLID 原则可使软件系统更易维护、更易扩展、更易理解、更易重构。

### S - 单一职责原则（SRP, Single Responsibility Principle）

**定义**：一个类应该只有一个发生变化的原因。另一种表述："将有且仅有一个原因引起类变化的职责捆绑在一起"。

每个类应该专注于做一件事——也只做好这件事。违反了 SRP 的类（"上帝类"）什么都做，任何需求的微小变化都可能触及它，修改风险极大。

```java
// 违反 SRP：一个类处理员工数据、计算薪酬、生成报表
class Employee {
    void save() { /* DB */ }
    double calculatePay() { /* 薪酬 */ }
    void generateReport() { /* 报表 */ }
}
// 遵守 SRP
class Employee { /* 纯数据 */ }
class PayCalculator { double calculatePay(Employee e); }
class EmployeeRepository { void save(Employee e); }
class ReportGenerator { void generate(Employee e); }
```

### O - 开闭原则（OCP, Open/Closed Principle）

**定义**：软件实体（类、模块、函数）对扩展开放，对修改关闭。即可以通过扩展（新增代码而非修改已有代码）来应对新需求。

关键是"修改关闭"——一旦一个类经过测试且稳定，不应再修改它（修改可能引入新 bug）。

实现方式：多态 + 策略模式——通过新增具体实现类扩展行为，无需修改使用抽象接口的客户端。

```java
// 违反 OCP：新增图形类型需修改此方法
double calculateArea(Shape s) {
    if (s.type == CIRCLE) return PI * s.r * s.r;
    else if (s.type == RECTANGLE) return s.w * s.h;
}
// 遵守 OCP：Shape 接口 + 各实现类
interface Shape { double area(); }
class Circle implements Shape { double area() { return PI * r * r; } }
class Rectangle implements Shape { double area() { return w * h; } }
```

### L - 里氏替换原则（LSP, Liskov Substitution Principle）

**定义**：子类型必须能够完全替代其基类型——使用基类引用的代码在不知道具体子类类型的情况下，子类出现时程序行为不应改变。

Barbara Liskov 在 1987 年形式化："若对每个类型 S 的对象 o₁ 和类型 T 的对象 o₂，对所有针对 T 定义的程序 P，当 o₂ 被 o₁ 替换后 P 的行为不变，则 S 是 T 的子类型。"

违反 LSP 的典型例子：正方形继承长方形——Rectangle 设定宽高独立改变，但 Square 的 setWidth 隐式改变了高度。调用方依赖"setWidth 不改变高度"时 Square 产生意外行为。

```java
// 违反 LSP
class Rectangle { int width, height; void setWidth(int w) { width = w; } }
class Square extends Rectangle {
    @Override void setWidth(int w) { super.setWidth(w); super.setHeight(w); }
}
```

### I - 接口隔离原则（ISP, Interface Segregation Principle）

**定义**：不应强迫类依赖它不需要的接口方法。客户端不应依赖它们不使用的方法。

"胖接口"（Fat Interface）迫使实现类为无关方法提供空实现或抛异常——增加耦合和混淆。

```java
// 违反 ISP
interface Worker { void work(); void eat(); void sleep(); }
class Robot implements Worker {
    void work() { /* 正常 */ }
    void eat() { throw new UnsupportedOperationException(); }
    void sleep() { throw new UnsupportedOperationException(); }
}
// 遵守 ISP：拆分接口
interface Workable { void work(); }
interface Eatable { void eat(); }
interface Sleepable { void sleep(); }
class Robot implements Workable { void work() { /* 仅此 */ } }
```

### D - 依赖反转原则（DIP, Dependency Inversion Principle）

**定义**：高层模块不应依赖低层模块——两者都应依赖抽象。抽象不应依赖细节——细节应依赖抽象。

传统的分层架构中高层依赖低层（Service → Repository → Database），导致低层变更影响高层。DIP 逆转了这个依赖方向：通过接口让低层依赖于高层定义的抽象（接口由高层定义，低层实现）。

```java
// 违反 DIP：高层直接依赖低层
class NotificationService {
    private EmailSender emailSender = new EmailSender();  // 具体实现
    void notify(String msg) { emailSender.send(msg); }
}
// 遵守 DIP：两者依赖抽象
interface MessageSender { void send(String msg); }
class EmailSender implements MessageSender { /* ... */ }
class NotificationService {
    private MessageSender sender;
    NotificationService(MessageSender sender) { this.sender = sender; }  // 依赖注入
    void notify(String msg) { sender.send(msg); }
}
```

## 关键结论

- SOLID 是"原则"而非"规则"——适用时需要判断，不要教条。小项目过度遵循 SRP 可能产生过多类
- OCP 的核心是"如果修改已有稳定代码，可能引入新 bug"——因此优先通过扩展而非修改来添加新功能
- LSP 说"is-a"关系不是用继承的充分条件——还要行为上可替换。"正方形 is-a 长方形"数学上正确，程序上错误
- DIP 和依赖注入（DI）/控制反转（IoC）高度关联——DI 是实现 DIP 的一种方式

## 易错点

1. SRP"一个类只有一个责任"——"责任"是指"变化的原因"而非"做一件事"。如只修改与 CEO 相关的逻辑 vs 只修改与 CFO 相关的逻辑是两个责任
2. DIP 不是"任何时候任何地方都用接口"——对稳定领域（如 String、标准库）直接依赖是合理的
3. 把 ISP 理解为"每个接口只能有一个方法"——极端 ISP 导致接口爆炸。合理的度："接口使用者不需要的方法不应该被暴露"

## 例题

**例题1**：分析以下代码违反了哪些 SOLID 原则并重构：

```java
class ReportService {
    void generatePDFReport(List<Data> data) {
        // 1. 连接 MySQL 数据库
        Connection conn = DriverManager.getConnection("jdbc:mysql://...");
        // 2. 用 data 计算报表值
        double total = data.stream().mapToDouble(Data::getAmount).sum();
        // 3. 生成 PDF
        PdfWriter writer = new PdfWriter("report.pdf");
        // ...
    }
}
```

**解答**：违反：(a) SRP——同一个类负责数据库连接、计算逻辑、PDF 生成三个职责；(b) DIP——直接依赖具体的 MySQL、PDF 实现（无抽象）。重构：拆分为 `DatabaseRepository`（数据访问接口）、`ReportCalculator`（计算逻辑）、`PdfGenerator`（实现 `ReportGenerator` 接口）。通过依赖注入组合三个组件。

**例题2**：给出 LSP 的另一个经典反例（非正方形-长方形）。

**解答**：鸟-企鹅问题。
```java
class Bird {
    void fly() { /* 鸟类飞行实现 */ }
}
class Penguin extends Bird {
    @Override void fly() { throw new UnsupportedOperationException("企鹅不会飞"); }
}
```
客户端代码 `bird.fly()` 在 `bird` 实际是 Penguin 时炸了——Penguin 削弱了 Bird 的 fly 行为契约。重构：去掉 Bird 的 `fly()`，改为 `FlyingBird extends Bird { void fly(); }`、`FlightlessBird extends Bird`。

## 关联页面

[[设计原则-DRY-KISS-YAGNI]] [[面向对象编程]] [[接口与抽象类]] [[继承与多态]]
