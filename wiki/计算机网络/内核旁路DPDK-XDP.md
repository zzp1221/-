---
title: "内核旁路DPDK/XDP"
course: 计算机网络
chapter: 高性能网络
difficulty: ADVANCED
tags: [计算机网络, DPDK, XDP, 内核旁路, 高性能]
aliases: [DPDK, XDP, Kernel Bypass, eXpress Data Path]
source: "DPDK官方文档; Linux kernel XDP文档; Cilium's BPF and XDP Reference Guide"
updated_at: 2026-05-02
---

## 核心定义

内核旁路(kernel bypass)是高性能网络的关键技术——网络包直接由用户空间程序处理而不经过内核网络协议栈。DPDK(Data Plane Development Kit, Intel主导)提供用户空间的poll-mode驱动(PMD)——持续轮询网卡RX队列替代中断驱动的收包。XDP(eXpress Data Path)是Linux内核中的eBPF挂钩点，在数据包到达网络栈之前(i40e驱动的RX队列之后, skb之前)处理，实现了接近内核旁路的性能而无需专用用户态驱动。

## DPDK vs XDP

DPDK：完整用户空间TCP/IP栈(如mTCP/TLDK/f-stack)，应用程序直接操作物理NIC(Hugepages内存映射网卡DMA区,排除内核),NUMA-aware内存分配。单核可处理100+Mpps。未通过标准socket——应用需要专门为DPDK编写。XDP：运行在内核中(无上下文切换)，但利用eBPF提供的安全保障。支持XDP_DROP/XDP_TX/XDP_REDIRECT/XDP_PASS动作。AF_XDP socket提供接近DPDK的信道到用户空间(zero-copy)——绕过sk_buff但保留socket接口。

## 关键结论

1. DPDK适合云服务商接入网关/流量清洗/DDoS缓解(Cloudflare的Spectrum使用DPDK) 2. XDP适合DDoS缓解和负载均衡(内核集成,无需重编译) 3. 内核旁路的主要代价是失去标准的socket生态(DPDK不兼容标准TCP) 4. ScyllaDB/Seastar使用DPDK网络层的用户态TCP(NIC>DPDK>Seastar>App) 5. AF_XDP是DPDK与标准socket之间的中间地带——提供DPDK级性能+标准socket-like接口

## 关联知识点

[[操作系统-eBPF内核虚拟机]] [[计算机网络-BBR拥塞控制]] [[Java深入-NIO与零拷贝]]
