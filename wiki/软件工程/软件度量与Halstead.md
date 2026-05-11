---
title: "软件度量与Halstead"
course: 软件工程
chapter: 软件度量
difficulty: INTERMEDIATE
tags: [软件工程, 软件度量, Halstead, 圈复杂度, 度量]
aliases: [Software Metrics, Halstead Complexity, Cyclomatic Complexity]
source: "Halstead 1977 (Elements of Software Science); McCabe 1976 (Cyclomatic Complexity); Fenton & Bieman《Software Metrics》"
updated_at: 2026-05-02
---

## 核心定义

软件度量(software metrics)量化软件质量、复杂度和可维护性。Halstead度量集包括：程序词汇量(η——η1=不同操作符数, η2=不同操作数数)、程序长度(N——N1=总操作符数, N2=总操作数数)、程序体积(V=N*log2(η1+η2)信息论bits)、难度(D=V/D'),工作量(E=D*V)和预测bug数(B=V/3000)。McCabe圈复杂度(Cyclomatic Complexity): C=E-N+2P(其中E=边,N=节点,P=连通分量+1)——计算程序control flow graph的独立路径数。

## 实践应用

度量在code review和改进过程中的应用：1.)架设度量门(metric thresholds)——如圈复杂度>15触发审查(函数太复杂) 2.)追踪趋势(随时间看度量变化)而非单一数值 3.)度量不是绝对好坏判断——仅作为争议触发器(canary)。Line of Code(LOC)虽粗略但能指示模块相对规模。LCOM(Lack of COhesion of Methods)指示类的内聚性。Chidamber and Kemerer(CK)指标集衡量OO软件(DIT,depth of inheritance tree; CBO,coupling between objects)。现代工具SonarQube和radon/mccabe实现了这些度量。

## 关键结论

1. One metric is no metric——单个度量不能作为决策依据(使用度量集) 2. 度量只度量某一方面——不能替代human judgement(度量提供信息,非决策) 3. 高复杂度可能导致低coverage测试不充分(识别需要重构的候选人) 4. LOC成为bug估计的基础(~5-50/千行代码取决于组织成熟度) 5. 度量基准(benchmark)因语言和领域而异(比较不能跨语言——比较要在相同域)

## 关联知识点

[[软件工程-代码审查与质量保证]] [[软件工程-软件测试策略]] [[软件工程-持续集成与持续部署]]
