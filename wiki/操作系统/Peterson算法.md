---
title: Peterson算法
course: 操作系统
chapter: 进程同步
difficulty: INTERMEDIATE
tags: [操作系统, Peterson算法, 临界区, 互斥, 软件方法]
aliases: [Peterson's Algorithm, Peterson互斥算法]
source:
  - Gary L. Peterson 论文 (1981)
  - Silberschatz《操作系统概念》
updated_at: 2026-05-02

---

## 核心定义

Peterson 算法是由 Gary L. Peterson 于 1981 年提出的经典软件互斥算法，用于解决两个进程间的临界区问题。它只使用两个共享变量——int turn（指示轮到哪个进程进入）和 bool flag[2]（每个进程是否准备好进入临界区的标志）。算法描述如下：(1) 进程 i 先设置 flag[i] = true 表示"我想进入"；(2) 然后设置 turn = j（谦让给另一方）；(3) 随后在 while(flag[j] && turn == j) 循环中等待；(4) 当条件不满足时进入临界区；(5) 退出临界区时 flag[i] = false。该算法满足互斥、前进和有限等待三个条件，且不使用任何硬件原子指令，是两进程互斥的经典软件解决方案。对于多进程（N>2）的扩展方案（如面包店算法 Bakery Algorithm）复杂度更高。

## 关键结论

- Peterson 算法仅适用于两个进程的互斥
- 使用两个变量：flag[2] 和 turn，纯软件无硬件依赖
- 满足互斥性、前进性和有限等待性
- 存在忙等（让权等待不满足），但在临界区短的情况下可以接受
- 现代硬件上由于编译器优化和 CPU 重排序可能导致失效，需内存屏障（memory barrier）保障正确性

## 易错点

1. turn = j 的"谦让"语义：进程 i 在表达意愿后将 turn 给对面，这是算法满足互斥的关键。如果取消这步，当两个进程同时表达意愿时会产生死锁
2. while 循环条件的理解：`while(flag[j] && turn == j)` 的含义是"如果对方也想进并且轮到对方进，则我等待"。如果对方不想进（flag[j]==false），或虽然对方想进但该我了（turn==i），则可以进入
3. 现代多核 CPU 的乱序执行问题：编译器可能重排指令顺序，需要使用内存屏障 `__sync_synchronize()` 或 C11 的 `atomic_thread_fence(memory_order_seq_cst)` 来保证正确性

## 例题

**例1：** 用 Peterson 算法的核心思想解释为什么它能保证互斥（不可能两个进程同时进入临界区）。

**解答：** 假设两个进程同时想进入（flag[0]=flag[1]=true）。由于 turn 只能取 0 或 1 中的一个值，所以必然有一个进程的 while 条件 `flag[other] && turn==other` 为 true 而等待，另一个为 false 而进入。不可能两边同时满足进入条件。

## 代码示例

```cpp
#include <atomic>
using namespace std;

class PetersonLock {
    atomic<bool> flag[2];
    atomic<int> turn;
public:
    PetersonLock() : flag{false, false}, turn(0) {}
    
    void lock(int i) {  // i = 0 或 1
        int j = 1 - i;
        flag[i].store(true, memory_order_seq_cst);
        turn.store(j, memory_order_seq_cst);
        // 内存屏障防止重排
        while (flag[j].load(memory_order_seq_cst) && 
               turn.load(memory_order_seq_cst) == j) {
            // 忙等
        }
    }
    
    void unlock(int i) {
        flag[i].store(false, memory_order_seq_cst);
    }
};
```

## 关联页面

[[临界区]] [[互斥与同步机制]] [[PV操作与信号量]] [[经典同步问题-生产者消费者]]
