---
title: 容器技术原理与Docker
course: 操作系统
chapter: 虚拟化与容器
difficulty: INTERMEDIATE
tags: [操作系统, 容器, Docker, 虚拟化, namespace, cgroups]
aliases: [Docker, 容器, Container]
source:
  - Docker官方文档
  - Linux Kernel Namespace/Cgroups文档
  - 《Docker深度实战》
updated_at: 2026-05-03
---

## 核心定义

容器是一种操作系统级虚拟化技术，通过Linux内核的Namespace和Cgroups机制实现进程隔离与资源限制。与传统虚拟机不同，容器共享宿主机内核，不需要独立的操作系统镜像，因此启动速度快（毫秒级）、资源开销小。Namespace提供6种隔离：PID（进程ID隔离）、NET（网络隔离）、MNT（文件系统挂载隔离）、UTS（主机名隔离）、IPC（进程间通信隔离）、USER（用户ID隔离）。Cgroups限制容器可用的CPU、内存、磁盘IO等资源。Docker是目前最流行的容器运行时，采用镜像分层（UnionFS）设计，每一层都是只读的，容器运行时在最上层添加可写层。OCI（Open Container Initiative）标准定义了容器镜像格式和运行时规范，使不同容器运行时（runc、containerd、CRI-O）可以互操作。容器编排工具Kubernetes管理大规模容器集群的调度、扩缩容和自愈。

## 关键结论

- 容器共享宿主机内核，比虚拟机轻量得多，但隔离性弱于虚拟机
- Namespace实现可见性隔离，Cgroups实现资源限制，Seccomp/AppArmor实现系统调用过滤
- Docker镜像采用分层存储，多个容器可共享相同的基础镜像层，节省磁盘空间
- 容器安全需要关注：镜像漏洞扫描、运行时最小权限、网络策略、镜像签名
- Kata Containers/Firecracker通过轻量VM兼顾容器便利性和虚拟机隔离性

## 易错点

1. 容器不是轻量级虚拟机：容器共享内核，内核漏洞影响所有容器；虚拟机有独立内核
2. PID Namespace隔离后容器内PID 1是init进程，需要正确处理信号（SIGTERM），否则容器无法优雅停止
3. 容器内数据默认是临时的，容器删除后数据丢失，需要使用Volume持久化

## 例题

**例1：** 一个Docker容器设置了CPU限制为0.5核、内存限制为512MB。容器内运行一个CPU密集型程序和一个内存密集型程序，请分析资源竞争情况。

**解答：** CPU限制0.5核表示该容器最多使用50%的CPU时间片（通过CFS带宽控制实现）。如果两个线程都想满负荷运行，每个线程实际只能获得25%的CPU时间。内存限制512MB是硬限制，容器内所有进程的内存总和超过512MB时会触发OOM Killer杀死容器内进程（不是宿主机进程）。CPU和内存的限制是独立的，CPU限制通过`cpu.cfs_quota_us`控制，内存限制通过`memory.limit_in_bytes`控制。

## 关联页面

[[Cgroups与容器资源隔离]] [[虚拟化技术对比]] [[微内核与宏内核]]
