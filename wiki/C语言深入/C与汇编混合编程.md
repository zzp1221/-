---
title: "C语言-C与汇编混合编程"
course: C语言深入
chapter: 系统编程
difficulty: ADVANCED
tags: [C语言, 汇编, 调用约定, 栈帧, ABI]
aliases: [C and Assembly, Calling Convention, Stack Frame]
source: "x86-64 System V ABI; AMD64 Architecture Programmer's Manual; Agner Fog calling convention"
updated_at: 2026-05-02
---

## 核心定义

""C与汇编混合编程基于ABI约定。x86-64 System V ABI规定：前6个整数/指针参数在rdi/rsi/rdx/rcx/r8/r9寄存器中传递，前8个SSE浮点参数在xmm0-7中，余下参数入栈(从右到左)。返回值：整数/指针在rax(64位内)和rdx(辅助)，浮点在xmm0。调用者保存(caller-saved)寄存器：rax/rcx/rdx/rsi/rdi/r8-r11(函数可随意修改)。被调用者保存(callee-saved)：rbx/rbp/r12-r15(函数必须恢复原值)。

## 栈帧与入口

""函数入口前序(prologue)：push rbp; mov rbp, rsp; sub rsp, N——保存旧栈帧指针,建立新帧,分配局部变量空间。返回前序(epilogue): leave(=mov rsp,rbp; pop rbp); ret。红色区域(Red Zone)——x86-64 ABI中rsp以下128字节无需显式分配即可使用(信号处理器不被中断时)。确保栈在CALL前16字节对齐(ABI要求)。ret指令从栈弹出返回地址并跳转。可以通过asm在内联中手工构造栈帧。

## 关键结论

""1. 从不假设调用约定的细节在不同编译器间一致(Windows x64使用不同的ABI) 2. 汇编代码中访问C全局变量通过符号引用(声明extern) 3. position-independent code(PIC)使用GOT间接引用全局符号 4. 混合编程需要完整的寄存器clobber列表 5. unwind tables(.eh_frame)实现C++异常处理穿越汇编代码

## 关联知识点

""[[C语言深入-内联汇编]] [[C语言深入-链接器与ABI详解]] [[C语言深入-跨平台移植要点]]
