---
title: 语言特性对比-Java
course: 程序设计
chapter: 编程语言对比
difficulty: INTERMEDIATE
tags: [Java, JVM, 面向对象, 垃圾回收, 平台无关, 企业级, Spring, JDK]
aliases: [Java Language, JVM, OOP, Garbage Collection, Platform Independence]
source:
  - James Gosling et al.《The Java Language Specification》
  - Joshua Bloch《Effective Java》
updated_at: 2026-05-02

---

## 核心定义

Java 由 James Gosling 在 Sun Microsystems 于 1995 年发布，口号 "Write Once, Run Anywhere" 表达了其跨平台哲学。Java 是全球使用最广泛的后端企业语言之一，驱动了大量银行、电商、大数据系统。Java 的设计哲学："简单的、面向对象的、分布式的、解释的、健壮的、安全的、架构中立的、可移植的、高性能的、多线程的、动态的语言"。

**核心特征**：
- **严格面向对象**（除了基本类型 int/char 等）：一切在类中定义，单继承类 + 多实现接口
- **JVM 虚拟机**：编译为字节码（`.class`），运行在 Java 虚拟机（JVM）上——JVM 提供内存管理（GC）、JIT 编译、安全沙箱、平台抽象
- **垃圾回收**（GC）：不需要手动内存管理，JVM 自动回收不可达对象
- **强静态类型**：类型在编译时声明和检查，泛型在编译后擦除（类型擦除）
- **多线程内置**：`java.lang.Thread`、`synchronized` 关键字、`java.util.concurrent` 包（Doug Lea 的并发大师之作）
- **受检异常**（Checked Exception）：方法签名中必须声明可能抛出的异常——调用方必须 catch 或声明（争议最大的 Java 特性）

**Java 生态**：Maven/Gradle（构建工具）、Spring Framework/Spring Boot（企业开发事实标准）、JUnit（测试）、Hibernate/JPA（ORM）、Apache Kafka/Hadoop/Spark（大数据）、Android SDK（移动开发，虽 Kotlin 渐渐替代）。

**Java 版本演进**：
- Java 5 (2004)：泛型、枚举、注解、增强 for、自动装箱
- Java 8 (2014)：Lambda、Stream API、Optional、CompletableFuture（函数式风格的里程碑版本）
- Java 11 (2018)：LTS，模块化系统（Jigsaw）稳定
- Java 17 (2021)：LTS，密封类（Sealed Classes）、模式匹配（Preview）、Records
- Java 21 (2023)：LTS，虚拟线程（Virtual Threads, Project Loom 正式落地）、模式匹配 for switch、Record Patterns
- Java 24 (2025)：流收集器改进、作用域值（Scoped Values）、结构化并发（Preview 增强）

**虚拟线程**（Virtual Threads, Java 21+）：革命性地改变了 Java 的并发模型——将现有的线程模型（OS 线程 = Java 线程）变为 M:N 模型：大量虚拟线程复用少量 OS 线程（载体线程）。阻塞 I/O 调用时虚拟线程自动挂载/卸载到不同载体线程上——可以廉价地创建百万级线程, 消除了 Future/Callback 的异步代码复杂性。编写同步代码获得异步性能。

**GC 的发展**：Serial GC（单线程，小应用）→ Parallel GC（多线程高吞吐）→ CMS（低延迟）→ G1 (Garbage First，大堆低停顿，默认 GC from Java 9) → ZGC (亚毫秒级暂停，TB 级堆) → Shenandoah (Red Hat, 并发紧凑)。GC 的演进使 Java 的延迟从最小秒级降至微秒级。

## 关键结论

- Java 的价值在于生态而非语言本身——Spring、Hadoop、Kafka、Elasticsearch 等庞大的开源库生态
- JVM 已不仅是 Java 的虚拟机——Kotlin、Scala、Groovy、Clojure 都运行在 JVM 上，共享其生态和优化
- Project Loom（虚拟线程）是 Java 最重要的现代变革——可能消除异步代码的大部分痛点
- "Java 很慢"是过时的刻板印象——JIT 预热后的性能可与 C++ 一较高下（但内存占用较高）

## 易错点

1. `==` 比较对象引用而非值——`String ==` 通常错误（要用 `equals()`），由于字符串驻留有时巧合相等
2. 泛型类型擦除——`List<String>` 和 `List<Integer>` 在运行时是同一类，无法 `instanceof List<String>`
3. 受检异常被静默消化——`catch (Exception e) {}` 隐藏真实错误，应至少记录日志或重新抛出
4. `SimpleDateFormat` 的线程不安全性——被广泛误用在多线程中，应使用 `DateTimeFormatter` (Java 8+)

## 例题

**例题1**：比较 Java 的 `synchronized` 隐式锁和 `ReentrantLock` 显式锁的使用场景。

**解答**：
synchronized：简单、自动释放、不可中断、无超时、无公平策略——适用于大多数简单同步场景。
ReentrantLock：灵活——可中断的锁获取（`lockInterruptibly`）、带超时（`tryLock(timeout)`）、公平锁（FIFO）、Condition 支持多个等待队列、可查询锁状态。适用：需要超时放弃的场景、生产者-消费者分离有不同的等待条件、需要调试/监控锁争用的系统。
Java 21 虚拟线程中 `ReentrantLock` 被调整为虚拟线程友好——`synchronized` 仍然钉在 OS 线程上使用，建议虚拟线程中用 `ReentrantLock` 替代 `synchronized`。

**例题2**：用 Java 8 Stream 处理数据：给定 `List<Order>`，计算每个用户的总消费额，仅保留 > 100 的用户，按金额降序排列。

**解答**：
```java
Map<String, Double> result = orders.stream()
    .collect(Collectors.groupingBy(Order::getUserId,
             Collectors.summingDouble(Order::getAmount)))
    .entrySet().stream()
    .filter(e -> e.getValue() > 100)
    .sorted(Map.Entry.<String, Double>comparingByValue().reversed())
    .collect(Collectors.toMap(Map.Entry::getKey, Map.Entry::getValue,
              (a, b) -> a, LinkedHashMap::new));
```

## 关联页面

[[面向对象编程]] [[类型系统]] [[并发编程]] [[内存管理]] [[编译型vs解释型语言]]
