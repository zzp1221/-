---
title: "Java深入-模块系统JPMS"
course: Java深入
chapter: 语言特性
difficulty: INTERMEDIATE
tags: [Java, JPMS, 模块, Jigsaw, module-info]
aliases: [Java Platform Module System, Project Jigsaw, module-info]
source: "JSR 376 (Java Platform Module System); Oracle: Java 9 Modularity; Nicolai Parlog《The Java Module System》"
updated_at: 2026-05-02
---

## 核心定义

Java模块系统(JPMS, Project Jigsaw, Java 9+)通过模块描述文件(module-info.java)定义模块：module com.example { requires java.sql; exports com.example.api; opens com.example.dto to jackson.databind; provides Service with Impl; uses Service; }。requires声明依赖，exports公开包(默认所有包隐藏)，opens允许深度反射访问。模块路径(module path)取代classpath的扁平可见性——通过强封装实现可靠性。

## 模块层次

模块分为：命名模块(named module——有module-info)、自动模块(automatic module——无module-info的Jar，推导名源自Manifest或文件名)、未命名模块(unnamed module——classpath上的所有类,可访问所有命名模块但被所有模块反向访问)。JDK本身被拆分成约70个模块(java.base是根模块——所有模块自动requires它)。模块化增强了安全性(内部API不再可访问除非opens)。

## 关键结论

1. java.base导出java.lang/java.util等基本包——隐式requires 2. requires static表示编译时依赖(运行时可选——类似Maven optional) 3. requires transitive传递依赖到使用方(类似Maven compile scope) 4. --add-exports/--add-opens命令行参数在模块系统边界打洞 5. 遗留代码可逐步迁移——先放在classpath上(未命名模块)

## 关联知识点

[[Java深入-反射与动态代理]] [[Java深入-类加载器与双亲委派]] [[软件工程-软件架构设计]]
