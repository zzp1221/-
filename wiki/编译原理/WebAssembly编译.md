---
title: WebAssembly编译
course: 编译原理
chapter: 编译目标
difficulty: INTERMEDIATE
tags: [编译原理, WebAssembly, Wasm, 编译目标, 虚拟机]
aliases: [Wasm, WebAssembly, WAT]
source:
  - WebAssembly官方规范（W3C标准）
  - Emscripten文档
  - 《WebAssembly: The Definitive Guide》
updated_at: 2026-05-03
---

## 核心定义

WebAssembly（Wasm）是一种安全、高效、可移植的二进制指令格式，设计为编译目标语言。Wasm不是编程语言，而是像汇编语言一样的低级虚拟指令集。核心特性：(1)基于栈的虚拟机（不是寄存器机）；(2)强类型（i32/i64/f32/f64四种数值类型）；(3)线性内存模型（一块连续的字节数组）；(4)模块化设计（导入/导出函数、表、内存）；(5)沙箱安全（不能直接访问宿主环境）。Wasm的编译流程：C/C++/Rust源码→LLVM IR→Wasm二进制（.wasm文件）。Emscripten工具链将C/C++编译为Wasm。Wasm也可以通过WAT（WebAssembly Text Format）文本表示，便于阅读和调试。Wasm在浏览器中通过JavaScript引擎执行（V8/SpiderMonkey），执行速度接近原生代码。WASI（WebAssembly System Interface）扩展了Wasm的服务端能力，使Wasm可以在浏览器外运行（如Cloudflare Workers、Fastly Compute）。

## 关键结论

- Wasm的设计目标是"编译目标"，不是替代JavaScript，而是补充JavaScript性能不足的场景
- Wasm的线性内存模型与C/C++的内存模型天然匹配，编译效率高
- Wasm的执行性能通常达到原生代码的70-90%，远优于JavaScript的JIT编译
- WASI使Wasm成为跨平台的通用编译目标，类似"容器的下一代"
- WasmGC提案增加了垃圾回收支持，使Java/Go/Kotlin等语言也能高效编译为Wasm

## 易错点

1. Wasm不是JavaScript的替代品：两者互补，Wasm处理计算密集型任务，JavaScript处理DOM和UI
2. Wasm的线性内存是独立的，不能直接访问JavaScript的堆，需要通过导入/导出接口交互
3. Wasm模块加载后是只读的，不能动态修改（需要重新实例化）

## 例题

**例1：** 将一个C语言的快速排序算法编译为Wasm，分析编译过程和执行性能。

**解答：** 编译过程：(1)C源码通过Clang前端生成LLVM IR；(2)LLVM后端优化IR；(3)Emscripten的Wasm后端将IR转为Wasm字节码；(4)生成.wasm文件和JS胶水代码。Wasm字节码示例：`func $qsort (param $arr i32) (param $low i32) (param $high i32) ...`。执行性能：Wasm在V8中通过Liftoff（快速基线编译）或TurboFan（优化编译）执行，快速排序的Wasm版本通常比纯JavaScript版本快2-5倍，接近原生C代码的80-90%性能。瓶颈在于：(1)边界检查（Wasm内存访问需要bounds check）；(2)无法使用SIMD优化（SIMD提案已部分实现）；(3)函数调用开销（Wasm→JS互调有开销）。

## 关联页面

[[字节码与虚拟机]] [[LLVM架构对比]] [[JIT编译技术]]
