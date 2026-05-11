---
title: "C语言-可变参数与stdarg"
course: C语言深入
chapter: 语言特性
difficulty: INTERMEDIATE
tags: [C语言, 可变参数, stdarg, va_list, variadic]
aliases: [C Variadic Functions, va_list, stdarg.h]
source: "C11 Standard §7.16; K&R 2nd ed §7.3; GCC Manual: Variable Argument Macros"
updated_at: 2026-05-02
---

## 核心定义

""可变参数函数(如printf)通过<stdarg.h>的宏实现。声明：int func(int cnt, ...)(至少一个固定参数)。函数内：va_list ap; va_start(ap, last_named_param)初始化；va_arg(ap, type)提取下一个参数(类型必须与实际匹配否则UB); va_end(ap)清理；va_copy用于保存/复制va_list状态。可变参数调用约定(cdecl)：参数从右向左入栈，调用者负责清理(支持可变参数)。

## 实现机制与陷阱

""在x86-64 ABI中，前6个整型参数通过寄存器传递(rdi/rsi/rdx/rcx/r8/r9)，前8个浮点参数通过xmm0-7。可变参数通过寄存器保存区(register save area)和栈同时传递——编译器生成代码将所有整数和浮点寄存器dump到栈上的固定偏移。printf的实现需解析格式串以推断参数类型。类型不匹配(va_arg(ap, long)从int)导致数据错位。va_arg(ap, float)提升为double(默认参数提升)。

## 关键结论

""1. 可变参数宏__VA_ARGS__提供宏级别的可变参数 2. va_copy是C99新增——不可直接赋值va_list 3. 不可在longjmp后访问已跳过的va_list 4. C23引入va_start的简化形式(void省略last param) 5. 可变参数类型检查无编译器保证——使用format属性(__attribute__((format)))辅助

## 关联知识点

""[[C语言深入-预处理器宏与条件编译]] [[C语言深入-错误处理errno]] [[C语言深入-链接器与ABI详解]]
