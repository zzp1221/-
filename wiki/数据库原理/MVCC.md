---
title: 多版本并发控制MVCC
course: 数据库原理
chapter: 并发控制
difficulty: ADVANCED
tags: [MVCC, 多版本并发控制, ReadView, 快照读, 当前读, 版本链, undo日志]
aliases: [Multi-Version Concurrency Control, ReadView, Snapshot Read, Current Read]
source:
  - 王珊《数据库系统概论》第5版
updated_at: 2026-05-02

---

## 核心定义

MVCC（Multi-Version Concurrency Control，多版本并发控制）是一种通过保存数据的多个历史版本来实现高并发访问的数据库并发控制机制。MVCC的核心思想是"读不加锁、读写不冲突"——当多个事务并发读写同一数据行时，写操作不阻塞读操作（反之亦然）。其实现方式为：每个事务修改数据时不是原地覆盖原始数据，而是产生一个新的数据版本；老版本仍被保留（不物理删除）供其他事务进行一致性的快照读取。MVCC基于快照（Snapshot）和UNDO日志工作——每次修改在原始数据上新增一行版本，并将旧版数据复制到UNDO段——旧版本链通过回滚指针（ROLL_PTR）关联在一起形成版本链。读取事务通过ReadView（读视图/快照）决定在当前事务的一致性视图中应该看到版本链中的哪个版本。MySQL InnoDB依靠MVCC实现了高效的非锁定一致性读（Consistent Nonlocking Read），PostgreSQL通过XID_xmin和xmax同样实现了MVCC。MVCC是应对读写冲突并发的最优雅方案——允许长事务和复杂的混合读写负载共存而大量降低锁竞争。

## 关键结论

- InnoDB MVCC的行版本中包含三个隐藏字段：DB_TRX_ID（最近一次修改此行的事务ID）、DB_ROLL_PTR（指向UNDO日志中前一个版本的指针，形成版本链）、DB_ROW_ID（仅在无主键时使用的聚簇行标识）。当更新行时，旧版本进入UNDO段，新行存放新值并更新DB_TRX_ID，串联版本链
- ReadView（快照）是在事务开始时的第一个快照读(SELECT)瞬间形成的"活动事务列表"：记录了当前系统中所有还未提交的事务ID集合。ReadView定义了可见性规则——任何TRX_ID落在ReadView"已提交且小于最小活动事务ID"范围内的版本是可见的，否则不可见(沿版本链找上一个版本)
- 快照读（Snapshot Read）与当前读（Current Read）：普通SELECT在不加锁隔离级别≥RC下使用快照读（通过ReadView看到的是历史版本——不加任何锁不阻塞）。当前读——SELECT ... FOR UPDATE / SELECT ... FOR SHARE（加X/S锁）、UPDATE、DELETE（自动加X锁并执行当前读读最新版本同时锁住）——始终读取最新版本
- MVCC在不同隔离级别的行为：READ COMMITTED下每个SELECT语句生成一个新的ReadView（事务中可以看见其他已提交事务的修改）。REPEATABLE READ下仅首次SELECT时创建ReadView，随后所有SELECT复用同一快照保证一致性可重复读
- MVCC与垃圾清理(Purge)：旧版本占UNDO空间——当事务不再需要读取这些旧版本时（所有比时间戳早于版本所有的事务都已结束），系统后台的Purge线程会压缩并物理删除对应过期的UNDO记录。如果长事务长期不提交，会阻止旧版本的清理，导致UNDO段过大和表膨胀

## 易错点

1. **MVCC不是全替代锁的方案**：MVCC处理的是"读写冲突"——让读不需要锁、写事务持锁用X锁保证写之间的互斥。多个并发写仍需X锁等互斥——MVCC只优化了读。写事务继续通过2PL加锁处理。

2. **快照读看到的"历史版本"不是"旧快照"**：快照是在事务开始时基于当时的提交状态"冻结"的——对REPEATABLE READ而言这个快照的时间点在开始SELECT后保持不变；对READ COMMITTED则每语句重建。但快照不会随时间演进。

3. **MVCC版本链太长导致性能下降**：如果开启了长事务（在RR隔离级别下占着最早快照不放），后续的大量UPDATE将在此表产生数百数千的内联版本——导致版本链遍历的查询开销增大。这就是为什么要控制长事务生命周期的原因。

4. **SELECT COUNT(*)结果的差异可能是MVCC快照导致**：REPEATABLE READ下统计函数COUNT返回的是快照时点的可见行数——与当前数据库的实际最新总数值可能不一致（因为有些已提交事务不在快照中）。这是因为MVCC产生的现象，不是幻觉读。

## 例题

**例题1**：在REPEATABLE READ下，事务T1执行SELECT，事务T2执行INSERT并提交，事务T1再次执行同样的SELECT。T1能看到T2插入的新行吗？为什么？

**解答**：RR下T1使用最初SELECT时创建的ReadView——此时T2还未提交或甚至在快照中T2不在活动事务列表中且T2的TRX_ID大于ReadView的最大事务值（T2通过提交来不可见）。T2插入的行的DB_TRX_ID=T2的ID不符合T1的ReadView可见性条件→新行对T1不可见。T1两次查询结果一致——杜绝了幻读。

**例题2**：说明InnoDB MVCC下的版本可见性判定算法。

**解答思路**：给定某行的DB_TRX_ID = N，ReadView包含min_id(最小活跃事务)、max_id(下一待分配事务ID)、active_list(活跃事务集合)。判定：(a)若N < min_id→该版本在ReadView创建时已提交→可见；(b)若N >= max_id→该版本在ReadView创建后由后来的事务提交→不可见；(c)若min_id ≤ N < max_id→若N在active_list中（活跃未提交）→不可见；否则N不在活跃列表中说明已提交→可见。不可见时沿DB_ROLL_PTR遍历版本链找满足条件的版本。

## 关联页面

[[并发问题]] [[封锁-排他锁与共享锁]] [[两段锁协议]] [[事务-ACID]]
