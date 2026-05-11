---
title: "Java-JVM架构与字节码"
course: Java深入
chapter: JVM
difficulty: ADVANCED
tags: [Java, JVM, 字节码, 类加载, JIT编译]
aliases: [JVM Architecture, Bytecode, Class Loading]
source: "Oracle JVM Specification SE 17; Wikipedia: Java virtual machine"
updated_at: 2026-05-02
---

## 核心定义

JVM(Java Virtual Machine)是运行Java字节码的虚拟机。核心组件：1.)类加载器(ClassLoader)子系统：Bootstrap→Extension→Application→用户自定义，遵循双亲委派模型 2.)运行时数据区：堆(所有线程共享)、方法区/元空间(Metaspace JDK8+)、虚拟机栈(每线程一栈)、PC寄存器、本地方法栈 3.)执行引擎：解释器+JIT编译器(C1/C2/Graal)

## 字节码

.class文件中的每条指令占1字节操作码+0~N操作数。典型指令：aload_0/iload_1(局部变量入栈)、invokevirtual(虚方法调用)、invokespecial(构造器/私有方法)、invokedynamic(动态语言支持JDK7+)。操作数栈+局部变量表架构(stack-based)，与寄存器的x86物理架构形成层次差异。

## 类加载过程

加载(Loading): 从.class文件读取字节流→链接(Linking): 验证(verify)+准备(prepare: 分配静态字段默认值)+解析(resolve: 符号引用→直接引用)→初始化(Initialization): 执行<clinit>静态初始化器。同一个类由不同ClassLoader加载视为不同类。

## 关联知识点

[[Java-GC算法与调优]] [[Java-JIT编译与性能优化]]
