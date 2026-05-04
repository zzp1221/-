---
title: "静态单赋值形式（SSA）"
course: 编译原理
chapter: 中间代码生成
difficulty: ADVANCED
tags: [编译原理, SSA, 中间表示, 编译器优化, φ函数]
aliases: [Static Single Assignment]
source: "Efficiently Computing Static Single Assignment Form (Cytron 1991); LLVM SSA文档"
updated_at: 2026-05-02
---

## 核心定义

SSA是IR的一种形式，每个变量在程序中恰好被赋值一次。当控制流合并时使用φ函数选择来自不同路径的值。将非SSA转为SSA需要：1.插入φ节点(在支配边界的汇合点) 2.变量重命名(version number)。支配边界精确确定φ节点插入位置。离开SSA时需要消除φ节点(用move指令替代)。

## 关键结论

1. SSA使use-def链变得显式(每个值只有一个定义) 2. 稀疏条件常量传播(SCCP)、全局值编号(GVN)等优化在SSA上更简单高效 3. SSA代价是插入大量φ和临时变量增加了IR体积

## 关联页面

[[三地址码与中间表示IR]] [[代码优化综合]] [[支配树]]
