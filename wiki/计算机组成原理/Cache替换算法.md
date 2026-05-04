---
title: Cache替换算法
course: 计算机组成原理
chapter: 第四章 存储器系统
difficulty: INTERMEDIATE
tags: [Cache替换, LRU, FIFO, RAND, 伪LRU, 替换策略]
aliases: [Cache Replacement, LRU Algorithm, FIFO Replacement]
source:
  - Patterson & Hennessy, Computer Organization and Design
updated_at: 2026-05-02

---

## 核心定义

当 Cache 发生缺失（Cache Miss）且目标组无空闲行槽时，需要根据某种策略选择一个现有 Cache 行替换出去，腾出空间存放从主存取来的新数据块——这一决策机制称为 Cache 替换算法（Replacement Algorithm）。其目标是最小化未来的缺失率（即选择未来最长时间不会被访问的块替换出去——Belady 最优替换算法，需要预知未来访问序列，无法物理实现）。实际使用的替换算法有三种：LRU（Least Recently Used，最近最少使用）——替换最长时间未被访问的行，利用了时间局部性，性能最好但硬件复杂度高（需要维护访问时间戳或位序）；FIFO（First In First Out，先进先出）——替换最早进入 Cache 的行，硬件简单但可能误淘汰频繁使用的老数据，性能不如 LRU；Random（随机替换）——随机选择被替换行，硬件最简单（伪随机数生成器），在相联度较高时性能接近 LRU。现代 CPU 中多使用伪 LRU（Tree-PLRU）或 NRU（Not Recently Used），在硬件开销和替换精度之间取得权衡。

## 关键结论

- LRU 性能最优：理论依据为时间局部性（最近使用的块最可能被再次使用）
- FIFO 简单但性能波动较大：基本忽略时间局部性，仅按时间入队信息决策
- RAND 在高相联度时表现接近 LRU：因为样本空间大时随机选择不太可能选中热数据
- 实际 CPU 常用伪 LRU（PLRU）：用二叉树位记录近似最近访问顺序，每 Cache 行仅需 1 位
- 替换算法的开销增大命中时间：复杂算法虽降低缺失率，但可能延长每次命中所需时间

## 易错点

1. LRU 不等于"先进先出"：最久前使用的（LRU）不等同于最早进入的（FIFO）。如果最早进入的块刚被重新使用，FIFO 会错误地淘汰它而 LRU 不会。
2. 替换决策只发生在相同组内：组相联 Cache 中，替换仅影响同组的路，不能跨组替换。
3. 实际 LRU 硬件实现：2 路 LRU 只需 1 位（记录最近访问的是哪路）；4 路需跟踪 24 种排列，需 5 位/组；8 路需跟踪 40320 种排列，硬件开销过大而改用伪 LRU。

## 例题

**例题1：** 某 2 路组相联 Cache，访问序列：A, B, C, A, D。模拟 FIFO 和 LRU 的行为。

**解答：** FIFO：A进入、B进入、C替换A（FIFO A最老）、A替换B（FIFO B次老）、D替换C。命中 1 次（A）。LRU：A进入、B进入、C替换A（LRU A）、A替换B（B非LRU? A刚用过但已被淘汰——C刚入为MRU, B为LRU故替换B, A进）、D替换C（C为LRU），命中 0 次。

**例题2：** 比较 LRU 和 Belady 最优替换。序列：1,2,3,4,1,2,5,1,2,3,4,5, Cache 3行。

**解答：** Belady：1,2,3; 3->4(淘汰3因为3最远被访问); 1hit; 2hit; 5替换4(1,2,5); 1hit; 2hit; 3替换5; 4替换3; 5替换4。缺失 7 次。LRU 缺失 10 次。Belady 是理论最优下界，LRU 有一定差距。

## 关联页面

[[Cache概述]] [[Cache映射方式]] [[Cache写策略]] [[存储器层次结构]]
