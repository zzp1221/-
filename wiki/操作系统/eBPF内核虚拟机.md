---
title: "eBPF内核虚拟机"
course: 操作系统
chapter: 内核扩展
difficulty: ADVANCED
tags: [操作系统, eBPF, 内核, 虚拟机, 可观测性]
aliases: [Extended Berkeley Packet Filter, BPF, Kernel VM]
source: "Linux kernel Documentation/bpf; Brendan Gregg《BPF Performance Tools》; Cilium eBPF文档"
updated_at: 2026-05-02
---

## 核心定义

eBPF(extended Berkeley Packet Filter)是Linux内核中的通用虚拟机，允许用户空间程序在内核态安全运行沙箱化代码。BPF程序被编译为eBPF指令集(RISC-like 64位VM)，经过验证器(verifier)保证安全性(无死循环、无越界内存访问、有限复杂度)后JIT编译为原生指令。挂钩点(hook)通过BPF程序类型定义：kprobe/kretprobe(内核函数入口/出口)、tracepoint(内核静态插桩点)、XDP(网络驱动层)、cgroup hook等。

## 应用与生态

eBPF应用领域：1.)可观测性——BCC/bpftrace工具(Greg Kroah-Hartman)、Pixie/parca持续profiling 2.)网络安全——Cilium的eBPF-based容器网络(替代iptables/ipvs) 通过BPF maps在用户空间和内核间交换数据(hash map/array/ring buffer)。CO-RE(Compile Once, Run Everywhere)——使用BTF(BPF Type Format)使pre-compiled BPF程序可跨内核版本运行(无需为每个内核编译)。Linux安全模块(LSM)BPF挂钩强制安全策略。

## 关键结论

1. eBPF被视作Linux内核最有意义的创新之一(类比JavaScript在浏览器中的角色) 2. 验证器约100k+行代码——保证BPF程序不会破坏内核稳定性 3. eBPF指令集最多100万条指令(复杂程序仍受限) 4. bpf_loop辅助可帮助实现有限循环(防止长暂停) 5. eBPF的可编程性令内核变得前所未有地可观测与可扩展

## 关联知识点

[[操作系统-容器隔离(cgroups/namespace)深度]] [[计算机网络-内核旁路DPDK/XDP]] [[编译原理-虚拟机与字节码]]
