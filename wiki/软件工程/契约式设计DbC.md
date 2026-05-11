---
title: "契约式设计DbC"
course: 软件工程
chapter: 软件设计
difficulty: INTERMEDIATE
tags: [软件工程, DbC, 契约式设计, 断言, Eiffel]
aliases: [Design by Contract, DbC, Precondition/Postcondition/Invariant]
source: "Meyer 1988《Object-Oriented Software Construction》; Eiffel文档; Java Modeling Language (JML)"
updated_at: 2026-05-02
---

## 核心定义

契约式设计(DbC/Design by Contract)是Meyer1988提出的命名式设计哲学。每个软件组件有明确的契约：前置条件(precondition)——调用者必须满足的条件(若违反,被调用方不负责任)；后置条件(postcondition)——被调用方在完成后必须保证的条件(若违反,调用方可拒绝接受)；类不变式(class invariant)——通过所有public操作始终保持的条件(操作前后不变式保持)。DbC将'接口即契约'的精神强化到方法论核心：如果前置满足而后置违反——唯一职责在被调用方存在bug。

## 实现与实践

Eiffel语言原生支持require(pre)/ensure(post — 可引用old变量检查变化后关系)/invariant关键字。在C++/Java中通过断言(assert)模拟——但无语言级支持削弱了契约的文档化效果。iContract/JML(Java Modeling Language)增加了语法糖但仍需额外工具。Kotlin的contract{}是有限DbC——允许函数内声明对调用者的某些保证(如callsInPlace)。Rust的类型系统(特别是trait bounds)可以部分表达pre/post conditions(在编译期)。Dafny/SPARK通过证明自动验证契约完备性。

## 关键结论

1. 前置条件!=输入验证——前置应可在调用前检查而不消耗额外资源 2. Liskov替换原则是DbC在继承中的契约表达——子类只能弱化前置、强化后置(持续保持超类契约) 3. 公共方法的所有断言允许在client检查断言的启用(而非在private内部代码) 4. 契约不仅仅是断言——更是形式的文档说明和责任分配 5. Z/VDM(B method)提升到完整的形式化验证级别

## 关联知识点

[[软件工程-形式化方法与模型检测]] [[软件工程-设计模式]] [[离散数学-模态逻辑]]
