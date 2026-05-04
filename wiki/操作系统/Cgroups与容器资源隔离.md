---
title: "Cgroups与容器资源隔离"
course: 操作系统
chapter: 虚拟化与容器
difficulty: INTERMEDIATE
tags: [操作系统, cgroups, 容器, Docker, 资源隔离]
aliases: [Control Groups]
source: "Linux Kernel Documentation (cgroups v1/v2); Docker官方文档"
updated_at: 2026-05-02
---

## 核心定义

Cgroups(Control Groups)是Linux内核的资源限制和统计机制，是Docker/Kubernetes等容器技术的基石。子系统：cpu（CPU配额/shares）、cpuset（CPU亲和性+NUMA）、memory（内存限制+OOM）、blkio（块设备IO限制）、net_cls（网络优先级）、pids（进程数限制）。Cgroups v2统一了层次结构。

## 关键结论

1. 容器=Namespaces(隔离)+Cgroups(限制)+rootfs(文件系统) 2. memory.limit_in_bytes超过后触发OOM killer 3. cpu.shares是相对权重（满负载时按比例分配）

## 关联页面

[[Docker容器技术]] [[进程隔离]] [[虚拟化技术对比]]
