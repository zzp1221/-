---
title: "C语言-sanitizer工具链"
course: C语言深入
chapter: 调试与测试
difficulty: ADVANCED
tags: [C语言, ASAN, UBSAN, TSAN, sanitizer]
aliases: [AddressSanitizer, UndefinedBehaviorSanitizer, ThreadSanitizer]
source: "LLVM Compiler documentation; Google Sanitizers Wiki; GCC Instrumentation Options"
updated_at: 2026-05-02
---

## 核心定义

""Sanitizer是编译器提供的运行时检测工具。AddressSanitizer(ASAN, -fsanitize=address)——检测堆/栈/全局内存越界、use-after-free、double-free、内存泄漏(需要LSan)。使用shadow memory(影子内存)：每8字节应用内存有1字节影子内存记录访问状态。开销：~2x执行时间、~20%内存。UndefinedBehaviorSanitizer(UBSAN, -fsanitize=undefined)——检测有符号整数溢出、除零、空指针解引用、越界数组索引、非法类型转换。

## TSAN与其他工具

""ThreadSanitizer(TSAN, -fsanitize=thread)——检测数据竞争(data race)、互斥锁误用。基于happens-before关系分析。开销：~5-15x运行速度、~5-10x内存。MemorySanitizer(MSAN, -fsanitize=memory,仅Linux)——检测未初始化内存的读取(ASAN不检测这个问题)。LeakSanitizer(LSAN)——检测内存泄漏(通常与ASAN集成)。sanitizer可以同时启用多个但可能冲突(ASAN+TSAN不可同时)。GCC version 4.8+均支持。

## 关键结论

""1. sanitizer是C/C++最重要的调试工具——覆盖各类内存错误 2. ASAN应与测试套件一起运行(detect heap buffer overflow) 3. UBSAN发现看似'work'但UB的代码(如shift>bitwidth) 4. TSAN可能检测到程序逻辑正确但仍存在的数据竞争 5. 生产环境非特殊场景不应使用sanitizer(安全与性能成本) 6. 可设置ASAN_OPTIONS=abort_on_error=1在检测到错误时崩溃

## 关联知识点

""[[C语言深入-指针算术与内存模型]] [[C语言深入-编译优化选项]] [[软件工程-软件调试技术]]
