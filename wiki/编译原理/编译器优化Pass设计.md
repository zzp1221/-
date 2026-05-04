---
title: 编译器优化Pass设计
course: 编译原理
chapter: 代码优化
difficulty: ADVANCED
tags: [编译原理, 优化Pass, LLVM, IR, 编译优化]
aliases: [Pass, Optimization Pass, 编译优化Pass]
source:
  - LLVM官方文档（Writing an LLVM Pass）
  - 《编译器设计与实现》
  - GCC内部文档
updated_at: 2026-05-03
---

## 核心定义

编译器优化Pass是对中间表示（IR）进行特定优化变换的独立模块。LLVM的Pass框架将优化组织为一系列Pass的流水线（Pass Pipeline），每个Pass遍历IR并进行特定变换。Pass分为两类：分析Pass（Analysis Pass）只读取IR并计算信息（如支配树、活跃变量分析），不修改IR；变换Pass（Transform Pass）修改IR并产生优化后的IR。LLVM Pass管理器（New Pass Manager）负责调度Pass的执行顺序，支持Pass依赖管理（分析Pass的结果可被变换Pass使用，IR变化后分析结果失效需重新计算）。常见优化Pass：(1)函数内联（InlinePass）：将小函数体展开到调用点；(2)死代码消除（DCEPass）：删除不影响程序输出的代码；(3)循环不变量外提（LICMPass）：将循环内不变的计算移到循环外；(4)公共子表达式消除（CSEPass）：合并重复计算；(5)尾调用优化（TailCallPass）：将尾递归转为循环。优化级别：-O0（无优化）、-O1（基本优化）、-O2（标准优化）、-O3（激进优化）、-Os（优化大小）。

## 关键结论

- 优化Pass的顺序很重要：某些优化会暴露新的优化机会（如内联后可以做更多DCE）
- 分析Pass的结果在IR被修改后自动失效，需要重新计算（Pass管理器自动处理）
- LLVM的Pass是模块化的，可以独立测试、组合使用
- 过度优化可能导致编译时间显著增加，需要在优化效果和编译时间之间权衡
- Profile-Guided Optimization（PGO）利用运行时数据指导优化决策，效果显著

## 易错点

1. 优化Pass不是越多越好：Pass之间可能相互干扰，过度优化可能导致代码膨胀
2. -O3不总是比-O2快：某些-O3的激进优化（如循环展开）可能增加代码大小导致缓存不命中
3. 内联不是万能的：过度内联导致代码膨胀，LLVM有内联阈值控制

## 例题

**例1：** 分析以下C代码经过-O2优化后的变换：`for(int i=0; i<n; i++) { x = a+b; arr[i] = x; }`

**解答：** Pass 1（循环不变量外提LICM）：`x = a+b`不依赖循环变量i，提到循环外→`x=a+b; for(i=0;i<n;i++) arr[i]=x;`。Pass 2（强度削减）：`arr[i]`的地址计算从乘法变为加法→`p=arr; for(i=0;i<n;i++) {*p=x; p++;}`。Pass 3（循环展开Loop Unrolling）：展开4次减少循环开销→`p=arr; for(i=0;i<n;i+=4){p[0]=x;p[1]=x;p[2]=x;p[3]=x;p+=4;}`（需处理余数）。Pass 4（向量化SLP/Loop Vectorize）：使用SIMD指令一次写入4个元素→`vec=x,x,x,x; for(...) store vec; p+=4;`。最终代码性能可能提升4-8倍。

## 关联页面

[[代码优化技术综述]] [[数据流分析]] [[循环优化]]
