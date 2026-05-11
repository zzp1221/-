---
title: "Java深入-注解处理与APT"
course: Java深入
chapter: 元编程
difficulty: INTERMEDIATE
tags: [Java, 注解, APT, Lombok, 编译期处理]
aliases: [Annotation Processing, APT, Lombok]
source: "JSR 269 (Pluggable Annotation Processing API); Lombok官方文档; Java注解处理器指南"
updated_at: 2026-05-02
---

## 核心定义

Java注解处理器(Annotation Processing Tool, APT)是在javac编译期运行的插件。通过实现javax.annotation.processing.AbstractProcessor，在编译的特定轮次(round)扫描注解生成额外的Java源文件。处理器通过ServiceLoader注册(META-INF/services/javax.annotation.processing.Processor)。lombok走的是非标准API(通过ECJ/javac内部API直接修改AST，允许修改已有类)。

## 实战场景

典型APT应用：1.)Dagger 2(编译期依赖注入) 2.)AutoValue/Immutables(自动生成value type) 3.)MapStruct(基于接口的映射代码生成) 4.)Room(编译期SQL验证) 5.)Butter Knife(R.id绑定，已被ViewBinding取代)。Annotation不能修改已有代码——Lombok通过侵入编译器内部实现(非标准)。APT生成的源码在.generated_sources目录，javac自动编译它们。

## 关键结论

1. APT仅能生成新文件——不能修改现有类(除Lombok的hack) 2. 处理轮次(delta rounds)限制——第n轮只能看到第n-1轮及之前生成的文件 3. processingEnv.getFiler()创建源文件，processingEnv.getMessager()报告错误 4. @SupportedAnnotationTypes和@SupportedSourceVersion标注处理器 5. Gradle/Kotlin KAPT将注解处理适配到Kotlin编译

## 关联知识点

[[Java深入-反射与动态代理]] [[Java深入-设计模式实战]] [[编译原理-语法树与中间表示]]
