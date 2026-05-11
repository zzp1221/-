---
title: "CFS调度器实现细节"
course: 操作系统
chapter: 进程调度
difficulty: ADVANCED
tags: [操作系统, CFS, 调度器, 红黑树, vruntime]
aliases: [Completely Fair Scheduler, CFS, vruntime]
source: "Linux kernel sched/fair.c源码; Robert Love《Linux Kernel Development》Ch 4; Linux kernel CFS documentation"
updated_at: 2026-05-02
---

## 核心定义

CFS(Completely Fair Scheduler, Linux 2.6.23+)是Linux的默认调度器。核心思想：每个任务获得虚拟运行时间(vruntime)与nice权重的比例时间。CFS使用红黑树(red-black tree)组织可运行任务——键值为vruntime(最小vruntime的任务在最左叶节点)。调度器选择最左节点执行。vruntime增量=实际运行时间×(NICE_0_LOAD/权重)——nice值越低(优先级高)权重越高,因此vruntime增长更慢从而获得更多CPU时间。

## 实现机制

CFS调度粒度和延迟：sched_min_granularity_ns(最小调度粒度——避免过于频繁切换)、sched_latency_ns(目标调度延迟——一个调度周期内所有可运行任务至少执行一次)。cgroup的CFS带宽控制通过cpu.cfs_quota_us/cpu.cfs_period_us限制CPU使用率。cfs_rq(每个CPU的CFS运行队列)跟踪运行统计数据。load_tracking(PELT——Per-Entity Load Tracking)将任务对CPU load的历史贡献按衰减指数计算以指导负载均衡。

## 关键结论

1. CFS是无时钟的(tickless)工作模式——动态计算时间片而非固定HZ 2. 新唤醒的任务vruntime设置为min(min_vruntime, se->vruntime - sysctl_sched_latency)以快速获得CPU(交互式任务) 3. CFS的负载均衡数个子任务在每个核心上执行(load_balance/pick_next_task) 4. Linux 6.6引入了EEVDF替代CFS(Earliest Eligible Virtual Deadline First)——更好的延迟保证

## 关联知识点

[[操作系统-多级反馈队列调度MLFQ]] [[操作系统-实时调度算法RMS与EDF]] [[操作系统-CPU亲和性与NUMA]]
