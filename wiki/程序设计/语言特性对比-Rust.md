---
title: 语言特性对比-Rust
course: 程序设计
chapter: 编程语言对比
difficulty: ADVANCED
tags: [Rust, 所有权, 借用, 生命期, 内存安全, Trait, 零成本抽象, 模式匹配, Cargo]
aliases: [Rust Language, Ownership, Borrowing, Lifetime, Memory Safety, Trait]
source:
  - Steve Klabnik & Carol Nichols《The Rust Programming Language》
  - Jim Blandy et al.《Programming Rust》
updated_at: 2026-05-02

---

## 核心定义

Rust 由 Mozilla Research 的 Graydon Hoare 发起、2015 年发布 1.0 版本，是系统编程语言中首个在不牺牲性能的前提下实现内存安全和线程安全的语言——无 GC、无运行时、无未定义行为（在 safe Rust 内）。Rust 连续多年在 Stack Overflow 开发者调查中获得"最受喜爱的语言"称号。

**Rust 的独特卖点**：达到 C/C++ 级别的性能零开销抽象 + 编译时保证的内存安全 + 现代语言的开发体验。

**核心特征**：

**所有权系统**（Ownership）：Rust 实现内存安全不需要 GC 的核心机制——每个值有唯一的所有者（owner），所有者在作用域结束时自动释放（drop）。所有权可被转移（move）——旧所有者不能再访问该值。所有权规则：同一时刻任意值要么有多个不可变引用，要么有唯一可变引用（不能同时存在）。

**借用**（Borrowing）：通过引用 `&T`（不可变借用）和 `&mut T`（可变借用）在不获得所有权的情况下使用值。借用规则在编译时由借用检查器（Borrow Checker, "Borrowck"）验证——"引用必须始终有效"（不能有悬空引用）。
```rust
let s1 = String::from("hello");
let s2 = s1;          // s1 的所有权被移动到 s2，s1 不再有效
// println!("{}", s1); // 编译错误！
let len = calculate_length(&s2); // 借出 s2
println!("{}", s2);   // s2 仍有效——借用已归还
```

**生命期**（Lifetime）：引用的有效作用域——标注用于编译器验证引用关系的正确性（尤其当多个引用交互时）。编译器在大多数情况下自动推断生命期（生命期省略规则），仅在不够明确时要求标注。

**代数数据类型 + 模式匹配**：
- `enum` —— 带数据的枚举，比 C/C++ 的 union 安全（类型系统保证总是匹配正确的变体）
- `Option<T>`（None 或 Some(value)）—— 替代 null（"十亿美元错误"）
- `Result<T, E>`（Ok(value) 或 Err(error)）—— 替代异常
- `match` 表达式 —— 穷尽性检查：编译器确保所有可能的模式都被覆盖

**Trait**：Rust 的多态和代码复用机制——类似于 Haskell 的 Typeclass 或 Java 的 Interface（但能力更丰富）。Trait 定义共享的行为，可为任意类型实现。Trait 支持默认方法实现（Java 接口的 default 方法更广范）。`derive` 属性可自动生成常见 trait 实现（`Debug`, `Clone`, `Copy`, `PartialEq`, `Hash`）。

**零成本抽象**（Zero-Cost Abstractions）：高级语言特性不引入运行时开销。迭代器链经编译器内联优化后与手写的 C 循环一样快。泛型单态化（Monomorphization）——为每具体类型的泛型函数生成独立代码（无运行时虚函数调用）。

**Cargo** 是 Rust 的构建系统和包管理器——`Cargo.toml` 声明依赖，`cargo build/run/test/bench` 执行构建/运行/测试/基准。集成 `rustfmt`（格式化）、`clippy`（lint）、`rustdoc`（文档生成）。`cargo test` 可并发运行单元测试、集成测试、文档测试——Rust 项目开发体验的标杆。

**Rust 安全模式**：Rust 代码分为 Safe Rust（编译器保证内存/线程安全）和 Unsafe Rust（可选地跳出安全规则做底层操作——解引用原始指针、调用 unsafe 外部函数等）。unsafe 代码应封装在安全的抽象内（如标准库的 `Vec<T>` 内部用 unsafe 做原始内存管理但对外暴露安全 API）。

**适用场景**：系统编程（操作系统 Redox、嵌入式、设备驱动）、WebAssembly、高性能 Web 后端（Actix-web/Axum）、区块链基础设施（Solana、Polkadot）、CLI 工具（bat, ripgrep, fd, zoxide）、数据库/搜索引擎（Meilisearch, SurrealDB）。

## 关键结论

- Rust 的编译器严格但回报巨大——"与编译器战斗"换来"运行时几乎不发生错误"
- 借用检查器的规则一开始令人沮丧——但随时间推移开发者会内化所有权模式的思维
- Rust 的错误信息是标杆——编译器给出精确的错误位置、原因、甚至是修复建议
- Trait 系统 + 泛型提供了类似 OOP 的代码复用但没有继承的耦合
- Unsafe Rust 是"我用生命担保这是安全的"——负责遵守编译器在 Safe Rust 中自动保证的不变量

## 易错点

1. 所有权与借用的基本混淆——移动后使用、引用的值生命期不够长
2. 生命期标注语法 `'a` 混淆方向——`fn foo<'a>(x: &'a str) -> &'a str` 表示返回的借用不超出输入 x 的生命期
3. 字符串类型繁多：`&str`（字符串切片/借用）、`String`（拥有所有权的可增字符串）、`OsStr`（平台原生）、`CStr`（C 兼容）等
4. `Rc<RefCell<T>>` 用于需要多个所有者的内部可变性——但这不是 Rust 的默认，需要显式构造并在运行时期检查借用规则（panic 若同时存在可变和不可变借用）

## 例题

**例题1**：为什么以下代码不能通过编译？如何修复？

```rust
let mut v = vec![1, 2, 3];
let first = &v[0];
v.push(4);
println!("{}", first);
```

**解答**：`first` 是 v 的不可变借用，`v.push(4)` 需要可变借用——同时存在可变和不可变借用违反 Rust 规则。即使 `push` 可能触发 vector 扩容（重新分配内存），`first` 指向的旧地址可能失效产生悬空引用。修复：调整顺序——先完成 push 再取引用，或先在借用独立作用域内用完 `first` 再 push（借用规则自动释放不可变借用）。

**例题2**：用 Rust 实现泛型的二分搜索函数 `binary_search`，要求使用 Trait 约束。

**解答**：
```rust
fn binary_search<T: Ord>(arr: &[T], target: &T) -> Option<usize> {
    let (mut lo, mut hi) = (0, arr.len());
    while lo < hi {
        let mid = lo + (hi - lo) / 2;
        match arr[mid].cmp(target) {
            std::cmp::Ordering::Less => lo = mid + 1,
            std::cmp::Ordering::Greater => hi = mid,
            std::cmp::Ordering::Equal => return Some(mid),
        }
    }
    None
}
```
Trait 约束 `T: Ord` 要求类型 T 必须实现全序比较（类似 Java/C# 的泛型 `where T: IComparable`），标准库的 `Ord` 为大部分内置类型自动实现。

## 关联页面

[[内存管理]] [[类型系统]] [[并发编程]] [[编译型vs解释型语言]]
