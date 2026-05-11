---
title: "容器隔离(cgroups/namespace)深度"
course: 操作系统
chapter: 虚拟化
difficulty: ADVANCED
tags: [操作系统, cgroups, namespace, 容器, 隔离]
aliases: [cgroups v2, Linux Namespaces, Container Isolation]
source: "Linux kernel文档 cgroups v2; Michael Kerrisk《Namespaces in operation》; Docker/containerd源码"
updated_at: 2026-05-02
---

## 核心定义

Linux容器依赖两大内核机制实现隔离。cgroups(Control Groups, v2已取代v1)：控制器(controller)控制进程组的资源使用——cpu(带宽/shares)、memory(硬限制+软限制、oom_group)、io(bfq/throttle)、pids(防fork炸弹)、cpuset(亲和性)。namespace：8种独立的命名空间——Mount(独立的文件系统视图/overlay2)、PID(独立的PID树)、Net(独立的网络栈/veth pair)、User(UID/GID映射,允许rootless容器)、UTS(hostname)、IPC、Cgroup、Time。

## 安全边界分析

容器不是完整的虚拟化——共享内核意味着容器间的攻击面：微架构侧信道(Spectre/Meltdown——容器的内核共享特性令其成为目标)、内核漏洞(容器逃逸漏洞如Dirty COW、Dirty Pipe)、共享资源消耗(写时拷贝的攻击)。Seccomp(secure computing)允许容器过滤系统调用减少攻击面。user namespace将容器中的root(UID 0)映射为主机上的非特权UID(安全隔离——免root容器)。gVisor/Kata Containers提供更强的安全隔离(为每个容器提供轻量级内核)。

## 关键结论

1. Kubernetes的QoS类(Guaranteed/Burstable/BestEffort)基于cgroups配置 2. OOM score基于当前+历史内存使用量(oom_score_adj调整) 3. cgroup v2去除了v1的forked hierarchy混乱(统一层级结构——每个控制器仅有一个实例) 4. 容器的资源限制不能超过实际资源容量否则形成资源过度承诺 5. Docker的default seccomp profile禁止约44个不安全的系统调用(约300+个总体调用)

## 关联知识点

[[操作系统-虚拟内存与TLB]] [[操作系统-eBPF内核虚拟机]] [[分布式系统-容器编排Kubernetes基础]]
