---
title: "Java深入-JIT编译与热点"
course: Java深入
chapter: JVM
difficulty: ADVANCED
tags: [Java, JIT, HotSpot, C1/C2, 编译优化]
aliases: [JIT Compilation, HotSpot, Tiered Compilation]
source: "OpenJDK HotSpot Runtime documentation; Oracle: Java Just-In-Time compilation; 周志明《深入理解Java虚拟机》Ch 11"
updated_at: 2026-05-02
---

## 核心定义

Java程序从解释执行开始，HotSpot JVM监控热点代码并JIT编译为原生代码。分层编译(tiered compilation)有5个级别——Level 0(解释器)、Level 1-3(C1编译器,带profiling)、Level 4(C2编译器,激进优化)。编译触发基于两个计数器：方法调用计数器+回边计数器(循环迭代)。热点代码经过profiling积累类型分布和分支概率数据后再被C2编译(Profile-Guided Optimization)。

## C1 vs C2编译器

C1(Client Compiler)——快速编译，较少激进优化(简单内联、寄存器分配、基本窥孔优化)，较慢的生成代码但快速的编译时间——适合客户端应用。C2(Server Compiler)——缓慢编译，更全面的优化：代数简化、逃逸分析(栈上分配+同步消除+标量替换)、虚方法调用去虚拟化(CHA, Class Hierarchy Analysis)、循环展开/向量化、范围检查消除。Graal(GraalVM的JIT, Java编写)正逐渐替代C2。

## 关键结论

1. 预热效应(warm-up)——JVM启动后前N次调用慢(解释/JIT编译中)但稳态极快 2. 去优化(deoptimization)——当C2基于不正确的profiling做出的优化假设被打破时回退到解释 3. -XX:+PrintCompilation查看编译事件 4. -XX:CompileThreshold调整触发阈值 5. OSR(On-Stack Replacement)在循环中途将解释的代码替换为编译的代码 6. 内联是最重要的JIT优化(消除调用开销并启用更多优化)

## 关联知识点

[[Java深入-JVM架构与字节码]] [[Java深入-类加载器与双亲委派]] [[编译原理-代码优化]]
