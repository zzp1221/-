---
title: MESI协议
course: 计算机组成原理
chapter: 第八章 多核处理器
difficulty: ADVANCED
tags: [MESI, Cache一致性, 监听协议, 四状态, Modified, Exclusive, Shared, Invalid]
aliases: [MESI Protocol, Illinois Protocol, MESI状态转换]
source:
  - Patterson & Hennessy, Computer Organization and Design
  - Papamarcos & Patel, A Low-Overhead Coherence Solution for Multiprocessors (1984)
updated_at: 2026-05-02

---

## 核心定义

MESI 协议是最经典的写无效式（Write-Invalidate）Cache 一致性监听协议之一，也称为 Illinois 协议。协议为每个 Cache 行定义了四种状态：M（Modified，已修改）——该 Cache 行的数据是脏的（已修改），在其他 Cache 中没有副本，数据仅在本地有效，必须由该 Cache 在替换时写回主存；E（Exclusive，独占）——该 Cache 行的数据与主存一致且干净，仅在本地有这个副本（其他 Cache 中没有），可直接静默修改为 M 而不必发送总线消息；S（Shared，共享）——该 Cache 行的数据与主存一致且干净（Effective），可能与其他 Cache 共享同一个干净副本，修改前必须发送无效化消息（BusRdX）将其他副本失效；I（Invalid，无效）——该 Cache 行无效（如未缓存或已被其他核的写操作失效化），访问时需重新从主存或其他 Cache 加载。状态转换由两种事件触发：处理器侧事件（PrRd 读、PrWr 写）和总线侧事件（BusRd 读、BusRdX 读独占、BusInv 失效化、Flush/WriteBack）。

## 关键结论

- E 态是 MESI 相较于基础 MSI 协议的关键优化：在 E 态下静默升级到 M 态无需总线事务，极大减少了私有数据的写协议开销
- 总线事务类型：BusRd（普通读请求）、BusRdX（读独占/Read For Ownership）、BusUpgr（升级请求/Invalidate，仅在其他核有共享副本时发出）
- 替换策略影响 MESI 行为：替换 M 态行必须写回主存（WriteBack）并将本地变 Invalid；替换 E/S 态行可直接丢弃
- MOESI 是 MESI 的扩展：引入 O（Owned）状态允许多个核持有脏数据但由拥有者最后写回
- MESIF 是 Intel 的变体：引入 F（Forward）状态，指定一个核专门负责在共享状态下提供数据给其他请求者

## 易错点

1. E 和 S 的共同点和区别：两者数据都与主存一致。区别在于——E 态下可以断定其他处理器没有该数据（无需 BusUpgr），S 态下则不确定。
2. 从 S 到 M 的升级需要总线事务：即使是本地处理器写入，也必须通过 BusUpgr 使其他 S 态副本无效化。
3. M 态下的读处理：M 态 Cache 行接收到其他处理器的读请求时，必须提供最新数据（可能既写回主存也提供给请求方），同时将自己降级为 S 态。

## 例题

**例题1：** 单核场景跟踪变量 A 的完整 MESI 状态转换。

**解答：** 初始 A 不在 Cache(I)。核读 A：发 BusRd，获数据且发现无其他副本，进入 E 态。核再次读 A：Cache 命中，E 态不变。核写 A：从 E 静默升级到 M，无总线事务（关键优化）。核再写 A：Cache 命中，M 态不变。替换 A：发 WriteBack 写回主存，转 I。

**例题2：** 说明 MESI 如何解决核心 A 写数据、核心 B 读到旧值的问题。

**解答：** 初始数据在 A 和 B 的 Cache 均为 S 态。A 执行写操作：A 首先发 BusUpgr 使 B 中该 Cache 行无效化（B: S->I），A 从 S 转 M，然后 A 完成写操作。若 B 再次读该地址：B 发 BusRd，A 侦听到该请求，因为 A 持有 M 态（最新数据），A 将数据提供给 B（Flush），A 和 B 均转 S 态。这确保 B 总是读到最新数据。

## 关联页面

[[Cache一致性]] [[Snooping协议]] [[Cache写策略]] [[多核处理器基础]]
