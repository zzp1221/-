---
title: "JIT（Just-In-Time）编译技术"
course: 编译原理
chapter: 编译器综述
difficulty: ADVANCED
tags: [编译原理, JIT, 动态编译, Java, JavaScript]
aliases: [Just-In-Time Compilation]
source: "Java HotSpot Performance Engine; V8 Design Documents; Modern Compiler Implementation (Appel)"
updated_at: 2026-05-02
---

## 核心定义

JIT在运行时将字节码/脚本转换为本地机器码。分层编译(Tiered Compilation)：interpreter(启动快)→Baseline JIT(简单编译，无优化)→Optimizing JIT(热点代码深度优化，用profile数据)。HotSpot JVM使用C1(Client)和C2(Server/用Sea of Nodes IR做激进的优化)。V8的Crankshaft→TurboFan→Sparkplug/Maglev，通过内联缓存(Inline Cache)和隐藏类(Hidden Class)优化JS动态特性。

## 关键结论

1. JIT根据运行时profiling做推测优化(需要bailout/deoptimization路径) 2. OSR(On-Stack Replacement)将正在运行的解释执行替换为编译代码 3. AOT vs JIT：AOT启动快但无profiling，JIT可做profile引导的投机优化

## 关联页面

[[GCC与LLVM架构对比]] [[字节码与虚拟机]] [[代码优化技术综述]]
