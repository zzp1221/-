---
title: 并发模型对比-线程vs协程vsActor
course: 程序设计
chapter: 并发与并行
difficulty: ADVANCED
tags: [线程, 协程, Actor模型, CSP, 并发模型, 事件驱动, 反应式, 异步, Go, Erlang]
aliases: [Concurrency Models, Thread vs Coroutine vs Actor, CSP, Reactive]
source:
  - Joe Armstrong《Making Reliable Distributed Systems in the Presence of Software Errors》(Erlang Thesis)
  - Carl Hewitt《Actor Model of Computation》
  - C.A.R. Hoare《Communicating Sequential Processes》
updated_at: 2026-05-02

---

## 核心定义

并发模型规定了程序如何组织和管理多个同时进行的计算任务。主流模型包括共享内存线程（Shared-Memory Threads）、协程（Coroutines）、Actor 和 CSP。不同模型在资源效率、编程难度、安全性、调试等方面各有优劣。

### 1. 操作系统线程（OS Threads）

线程是操作系统内核管理的抽象——每个线程拥有独立栈和寄存器上下文，由 OS 抢占式调度。CPU 通过时分复用（Time Slicing）在多个线程间快速切换。

**特点**：
- 抢占式调度——OS 可随时暂停线程（无需它的合作），保证公平性
- 真正的并行——在多核上多线程同时执行
- 重量级——创建/切换线程涉及内核态上下文切换（保存/恢复寄存器、刷新 TLB 等，~1-10μs），栈占用数 MB
- 共享所有进程内存（数据竞争风险）——需锁/原子操作保护共享状态
- 代表语言：Java (`Thread`), C (`pthread`), C++ (`std::thread`), C# (`Task` 在 OS 线程上多路复用)

### 2. 协程（Coroutines）

协程是能暂停和恢复执行的计算单元——不依赖 OS 调度，由程序显式控制或由语言运行时管理切换点。协程共享同一 OS 线程或复用小线程池。

**特点**：
- 协作式调度——仅在 await / yield / 阻塞 I/O 时自愿让出控制权，不会被抢占（不会被中断）
- 轻量级——协程栈仅数 KB 起步（按需增长），切换是用户态直接跳转, ~10-100ns 级别
- 创建成本极低——可创建百万级别的协程（Go 的 goroutine、Kotlin 的协程、Python 的 asyncio Task）
- 本质上非真正并行——一个 OS 线程上的协程串行执行（但可通过多线程 + 协程实现并行）
- 代表：
  - **async/await**（Python, JavaScript, Rust, C#）：在 await 处函数转换为状态机 yield back 到事件循环
  - **Goroutine**（Go）：Go 运行时的 M:N 调度器将 goroutine 多路复用到 OS 线程上。Goroutine 是抢占式的（Go 1.14+ 异步抢占——防止无限循环 goroutine 阻塞调度器），但比线程轻量得多
  - **Loom 虚拟线程**（Java 21+）：JVM 级别的虚拟线程（M:N 模型）——同步阻塞代码自动挂载/卸载虚拟线程到载体线程上

### 3. Actor 模型（Actor Model, Carl Hewitt 1973）

Actor 是并发的基本单元——每个 Actor 拥有私有状态、一个邮箱（Mailbox）和一个消息处理逻辑。Actor 之间不共享状态，仅通过**异步消息传递**通信。

**特征**：
- 不共享——消除了数据竞争（每个 Actor 的私有状态无外部访问）
- 消息驱动——接收消息后：处理消息 → 发送消息给其他 Actor → 创建新 Actor
- 异步——发送消息后立即返回（非阻塞），接收方在其准备好的时候处理
- 位置透明——Actor 可以存在于同一进程或将分布式存于其他节点（Erlang 的分布式透明性）
- 容错——父 Actor 可监管子 Actor 的失败和恢复规则（监管策略：one-for-one, one-for-all），构成 Erlang/Elixir 的核心可靠性（Let it crash philosophy）

代表：**Erlang/Elixir**（AKA 电话交换机语言的并发模型）、**Akka**（JVM 上的 Actor 库）、**Orleans**（Microsoft 虚拟 Actor 框架）。

### 4. CSP 模型（Communicating Sequential Processes）

CSP 由 Tony Hoare 于 1978 年形式化——进程通过无缓冲的**通道**（Channel）同步通信。与 Actor 的区别：CSP 的通信是同步的（发送方等待接收方准备就绪），Actor 的消息是异步发送和入队。

Go 受 CSP 影响——goroutine 通过 channel 通信，"不通过共享内存通信，而通过通信共享内存"。Rust 的 `std::sync::mpsc` 也是受 CSP 影响。

### 对比总结

| 维度 | OS Threads | Coroutines (async) | Goroutines | Actor (Erlang) | CSP (Go) |
|------|-----------|-------------------|-----------|----------------|----------|
| 创建成本 | 高 (~1MB 栈) | 低 (几KB) | 低 (2KB) | 低 (几百字) | 低 |
| 调度 | 抢占式 (OS) | 协作式 (await) | 抢占+协作混合 | 抢占式 (VM) | 抢占+协作 |
| 百万并发 | 不可行 | 可 (async) | 可 | 可 | 可 |
| 通信 | 共享内存+锁 | 共享内存 (lock-free) | Channel+共享 | 消息传递 | Channel |
| 数据竞争 | 高风险 | 中风险 | 低风险 | 无 (不共享) | 低风险 |
| 典型语言 | C, C++, Java | Python, JS | Go | Erlang, Elixir | Go, Rust(std) |

## 关键结论

- 协程解决的是"高并发 I/O"——用很小内存处理大量同时存在的连接
- 线程解决的是"真正并行 CPU 计算"——多核同时执行
- Actor 模型解决的是"分布容错"——构建自我修复的持续在线系统
- Go 的并发模型 = CSP 通道 + 轻量级抢占协程 + M:N 调度的一体化集成——这也是 Go 成功的关键
- 没有单一种模型适应所有场景——现代复杂系统通常是多模型混合

## 易错点

1. 协程提高的是并发（同时处理多任务）不是并行（多核同时执行）
2. Go goroutine 不是纯协作式——Go 1.14+ 通过信号实现轻量抢占（避免无限循环 hang），不要依赖协作式行为
3. Actor 的异步消息传递可能导致消息顺序非确定性——在分布式场景中两个消息的接收顺序可能不同

## 例题

**例题1**：比较 goroutine + channel 和 asyncio 对 CPU 密集型操作的处理方式。

**解答**：Goroutine 由 Go 运行时调度器在多个 OS 线程上执行——足够多核 goroutine 可真正并行。CPU 密集型 goroutine 被公平分配 CPU 时间。asyncio 基于单线程事件循环——CPU 密集型函数会阻塞事件循环使所有协程暂停。Python 的解决方案：CPU 密集操作应放在 `asyncio.to_thread`（线程池）或 `ProcessPoolExecutor`（进程池）中执行，让事件循环继续运行。

**例题2**：描述 Erlang 监督树（Supervision Tree）的容错策略和设计哲学。

**解答**：Erlang 倡导"让它崩溃"（Let It Crash）哲学——不防御式地处理每个可能的错误（过度 try-catch），而让进程自然崩溃并由监督者（Supervisor）根据既定策略恢复。监督树结构：
- Worker 进程：执行实际工作，出错则崩溃
- Supervisor 进程：监控子进程的崩溃，按策略恢复：
  - `one_for_one`：仅重启崩溃的子进程
  - `one_for_all`：重启所有子进程（相关联性）
  - `rest_for_one`：重启崩溃子进程和其后启动的所有子进程
- 监督者可自有监督者（上层 Supervisor），形成树状层次。最顶层是 Root Supervisor，保证系统"始终在可预期状态"。

## 关联页面

[[并发编程]] [[异步编程]] [[内存管理]] [[函数式编程]]
