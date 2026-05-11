---
title: "JIT编译原理"
course: 编译原理
chapter: 运行时编译
difficulty: ADVANCED
tags: [编译原理, JIT, 即时编译, JVM, V8]
aliases: [Just-In-Time Compilation, JIT, Adaptive Compilation]
source: "OpenJDK HotSpot源码; V8 Blog: How V8 measures real-world performance; Aycock 2003 (JIT survey)"
updated_at: 2026-05-02
---

## 核心定义

JIT(Just-In-Time,即时编译)在运行时将字节码或中间代码编译为原生机器码——结合了解释执行的灵活性与AOT编译的性能。触发编译的条件：方法调用计数(热点阈值)、循环迭代计数(OSR,On-Stack Replacement——将解释执行的循环体中途替换为编译版本)。分层编译(tiered compilation)在快速编译+基础优化(代码热)和慢编译+激进优化(真正热点)之间平衡。Deoptimization——当JIT基于乐观假设(如类型固定)生成的代码假设被打破时回退到解释模式。

## 编译器技术比较

HotSpot(JVM)使用模板解释器(template interpreter——通过宏汇编为每个字节码生成机器码片段)，C1(快速编译+基本优化)和C2(基于sea-of-nodes IR的重型优化)。V8(Chrome/Node.js)使用Ignition(字节码解释器)+TurboFan(多级优化JIT)。V8之前使用Crankshaft和Full-Codegen但已被淘汰。LuaJIT的trace compiler(追踪编译器)——在运行时记录热路径的执行轨迹生成专门化代码(只需优化被执行的路径，不用处理整个函数)。Inline caching缓存类型分发结果——也是JIT技术的一种。

## 关键结论

1. JIT的预热成本(warm-up costs)在实验对比中不可忽略——稳态性能分析需要排除预热 2. 去优化(deopt)的粒度影响——不能太粗(roll-back path太大)也不能太细(检查开销大) 3. AOT+JIT混合(PGO驱动)正在成为趋势(Graal Native Image/PGO、OpenJDK Leyden项目) 4. JIT使得profile-guided optimization在运行时自动完成(动态profiling) 5. JIT使Java/C#虚拟机性能接近(有时超过)C/C++静态编译

## 关联知识点

[[编译原理-LLVM IR与优化Pass]] [[编译原理-字节码虚拟机设计]] [[Java深入-JIT编译与热点]]
