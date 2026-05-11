---
title: "Java深入-构建工具(Maven/Gradle)"
course: Java深入
chapter: 工程构建
difficulty: BASIC
tags: [Java, Maven, Gradle, 构建, 依赖管理]
aliases: [Maven, Gradle, Build Lifecycle]
source: "Maven官方文档; Gradle User Manual; Sonatype《Maven: The Complete Reference》"
updated_at: 2026-05-02
---

## 核心定义

Maven使用声明式XML(pom.xml)描述项目。核心概念：坐标(GAV——groupId/artifactId/version唯一定位一个artifact)、依赖范围(compile/runtime/test/provided/system)、生命周期(clean/default/site——由插件目标goal绑定到phase执行)、传递依赖(nearest wins——基于版本冲突的依赖仲裁)。Maven Central Repository是默认构件库。settings.xml配置仓库认证、代理、镜像。

## Maven vs Gradle

Gradle使用Groovy/Kotlin DSL构建脚本(build.gradle/build.gradle.kts)，提供灵活性和性能。Gradle的构建缓存(up-to-date checks)和增量构建显著超越Maven。依赖解析使用丰富版本声明(动态版本1.+、版本范围[1.0,2.0))。Maven的BOM(Bill of Materials)在dependencyManagement中管理版本(Spring Boot Starter Parent典型)。Gradle的多项目构建(settings.gradle的include)管理大型项目。

## 关键结论

1. maven-enforcer-plugin强制执行依赖收敛(依赖版本冲突检查) 2. 永远不要将credentials放在pom.xml(settings.xml或环境变量) 3. Maven Wrapper(mvnw)和Gradle Wrapper(gradlew)确保CI和开发环境一致性 4. Maven的scope provided用于容器提供的依赖(servlet-api) 5. 发布到Maven Central需要PGP签名、Javadoc、Sources Jar

## 关联知识点

[[Java深入-模块系统JPMS]] [[Go语言-Module与依赖管理]] [[软件工程-持续集成与持续部署]]
