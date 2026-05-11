---
title: "C语言-setjmp/longjmp与异常处理"
course: C语言深入
chapter: 错误处理
difficulty: ADVANCED
tags: [C语言, setjmp, longjmp, 跳转, 异常]
aliases: [Non-local Jumps, setjmp/longjmp]
source: "C11 Standard §7.13; APUE §7.10; CERT C ERR04-C"
updated_at: 2026-05-02
---

## 核心定义

""setjmp/longjmp提供非局部跳转(non-local goto)能力：setjmp(jmp_buf env)在调用点保存当前执行环境(寄存器、栈指针、程序计数器)，返回0。longjmp(env, val)恢复保存的环境使setjmp重新"返回"值为val。典型的异常模拟模式——在深层调用栈中检测到错误时跳长距离返回到已保存的安全点。jmp_buf通常是平台相关的寄存器保存区数组。

## 陷阱与限制

""1.)longjmp后自动变量的值不确定(若在setjmp和longjmp间被修改)——volatile可缓解 2.)longjmp不触发栈展开——不会调用对象的析构函数(C无析构但资源泄漏风险高) 3.)信号处理器中调用longjmp不够安全——使用siglongjmp 4.)longjmp激活的跳转不能返回到已退出的函数。现代C代码越来越少使用，倾向于使用返回值链或errno——但交互式解释器和coroutine实现仍有使用。

## 关键结论

""1. setjmp/longjmp是C的goto on steroids 2. 不推荐在C++中使用(绕过析构函数) 3. Ruby、Lua等语言的协程/异常由setjmp实现 4. POSIX规定longjmp在信号处理器中必须配合sigsetjmp/siglongjmp 5. 性能：setjmp约15-30ns(寄存器保存),longjmp类似

## 关联知识点

""[[C语言深入-信号处理与异步安全]] [[C语言深入-错误处理errno]] [[C语言深入-递归与尾递归]]
