---
title: "网络协议fuzzing"
course: 信息安全
chapter: 安全测试
difficulty: INTERMEDIATE
tags: [信息安全, fuzzing, 协议安全, 漏洞发现]
aliases: [Protocol Fuzzing, AFL, Coverage-Guided Fuzzing]
source: "Zalewski (American Fuzzy Lop); Fioraldi et al. 2020 (AFL++); Sutton et al.《Fuzzing: Brute Force Vulnerability Discovery》"
updated_at: 2026-05-02
---

## 核心定义

Fuzzing(模糊测试)为被测程序提供大量随机或半编译生成的输入以触发异常或崩溃。协议fuzzing(protocol fuzzing)聚焦网络协议的健壮性——构造格式正确但语义异常的协议消息。三种方法：生成式fuzzing(generation-based——根据协议语法描述生成输入——需要格式定义如protobuf)、变异式fuzzing(mutation-based——劫持有效的协议数据流进行比特变异)、灰盒fuzzing(coverage-guided——AFL/AFL++用代码覆盖率引导进化式变异以达到更深程序路径)。LibFuzzer对库API的in-process fuzzing。

## AFL工作原理

AFL(American Fuzzy Lop)是最具影响力的覆盖率导向fuzzer。编译时插桩(basic block transitions——记录每个输入触发的边的集合)将input文件转为高熵->低熵。Fuzzer维护queue(有趣输入)和当前变异输入——每发现触发新边的输入即加入queue用作下一轮变异的种子(进化选择)。AFL利用fork server避免每个输入都经历完整的execve开销。Sanitizers(ASAN/UBSAN)增加内存错误检出率。Fuzzer常需一天到几周连续运行——发现罕见race condition。

## 关键结论

1. Fuzzing是最有效地发现真实世界安全漏洞的方法之一 2. Protocol fuzzing需要理解协议状态——stateless fuzz只有浅层bug,stateful fuzz更深入但更复杂 3. Dumb fuzzer(纯随机)通常无法通过输入格式解析(覆盖率极低) 4. 结合fuzzing与符号执行(如Driller/QSYM)可跨越magic byte/checksum等障碍 5. Google的OSS-Fuzz项目持续fuzz数百个开源项目——已经发现了数十万个安全漏洞

## 关联知识点

[[信息安全-代码安全审计]] [[软件工程-软件测试策略]] [[编译原理-静态分析工具链]]
