---
title: "Rust语言-cargo与依赖管理"
course: Rust语言
chapter: 工程构建
difficulty: BASIC
tags: [Rust, cargo, Cargo.toml, features, 依赖管理]
aliases: [Cargo, Dependencies, Workspaces, Features]
source: "The Cargo Book; Rust官方文档: Cargo; RFC 2953 (features v2)"
updated_at: 2026-05-02
---

## 核心定义

""Cargo是Rust的构建系统和包管理器。Cargo.toml定义项目元数据和依赖(语义版本控制SemVer——^1.2.3表示>=1.2.3且<2.0.0)。Cargo.lock锁定精确版本(库不提交lock忽略,二进制应提交lock文件)。cargo build --release启用优化。cargo check快速验证编译(不生成二进制)。RUSTFLAGS环境变量传递额外编译器参数。cargo doc --open生成并打开文档。

## Features与Workspace

""Cargo features实现条件编译和可选依赖(在Cargo.toml的[features]段定义)。Feature依赖树通过cfg(feature='xxx')和#[cfg(feature='xxx')]在代码中条件启用。default features通过default-features=false禁用。Workspace管理多crate：Cargo.toml[workspace]段列出成员。工作区共享一个顶层target目录和Cargo.lock。patch段替换依赖源(ex:替换为本地路径或git仓库)。

## 关键结论

""1. 库不应提交Cargo.lock(应被忽略) 2. Feature additive原则——feature应纯增加功能而非改变行为 3. cargo tree查看依赖树 4. cargo audit检查安全漏洞 5. cargo vendor创建离线依赖缓存 6. crates.io的readme和categories提升可发现性

## 关联知识点

""[[Rust语言-模块与Crate组织]] [[Go语言-Module与依赖管理]] [[软件工程-版本控制与Git]]
