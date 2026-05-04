---
title: SRAM与DRAM
course: 计算机组成原理
chapter: 第四章 存储器系统
difficulty: INTERMEDIATE
tags: [SRAM, DRAM, 静态RAM, 动态RAM, 刷新, 存储单元]
aliases: [Static RAM, Dynamic RAM, 静态存储器, 动态存储器]
source:
  - Patterson & Hennessy, Computer Organization and Design
updated_at: 2026-05-02

---

## 核心定义

SRAM（Static Random Access Memory, 静态随机存取存储器）和 DRAM（Dynamic Random Access Memory, 动态随机存取存储器）是两种主要的半导体主存储器技术。SRAM 使用 6 个晶体管（6T SRAM cell）构成一个双稳态触发器来存储 1 位数据，只要不断电，数据就能稳定保持，无需刷新——因而称为"静态"。DRAM 使用 1 个晶体管 + 1 个电容（1T1C cell）存储数据，电容上的电荷会逐渐泄漏（毫秒量级），因此需要周期性地读出-放大-写回的刷新（Refresh）操作来维持数据——因而称为"动态"。SRAM 存取速度快（几纳秒）、功耗相对较低、集成度低（每单元 6T）、成本高，用作 Cache；DRAM 集成度高（每单元 1T1C）、成本低、容量大，但速度较慢（几十纳秒）且需刷新电路，用作主存储器。

## 关键结论

- SRAM 比 DRAM 快约 5-10 倍，但价格贵约 10-20 倍，集成度低约 4-8 倍（相同面积下 DRAM 容量更大）
- DRAM 的刷新周期通常为 64ms，所有行必须在此时段内至少刷新一次（典型的 DDR4 每 7.8μs 发出一次刷新命令）
- DRAM 的行/列地址分时复用：先发送行地址（RAS, Row Address Strobe），后发送列地址（CAS, Column Address Strobe），减少引脚数
- 刷新方式：集中刷新（所有行逐行刷新，期间停止读写）、分散刷新（将刷新周期分散到每个存储周期中）
- SRAM 用作 Cache，DRAM 用作主存——这种分工正是存储层次在物理实现层面的体现

## 易错点

1. DRAM 的"动态"指电容电荷需刷新，而非数据内容动态变化——"刷新"在 DRAM 中是硬件自动完成的底层操作，上层程序员无感。
2. SRAM 虽然不是"动态"刷新，但其数据会在断电后丢失——它仍是易失性存储器（Volatile Memory），这一点与 DRAM 一致。
3. DRAM 读取是破坏性的：读出时电容电荷被释放，读后需要自动写回（Read-Modify-Write），由 DRAM 内部电路自动完成。

## 例题

**例题1：** 比较 SRAM 和 DRAM 在 Cache 和主存中的应用选择。

**解答：** Cache 需要极低延迟（1-4 个时钟周期），但容量只需 KB~MB 级别，SRAM 的速度和成本符合要求。主存需要 GB 级容量，延迟容忍度相对高（100+ 个时钟周期），DRAM 成本低、容量大是合理选择。两者的电路工艺也不兼容（逻辑工艺 vs DRAM 工艺），因此无法混用。

**例题2：** 计算 64GB DDR4 内存需要多少个 DRAM 芯片（假设每个芯片 8Gb）。

**解答：** 64GB = 512Gb。芯片数 = 512Gb / 8Gb = 64 个芯片。考虑 ECC（错误校验）需要额外 8 个芯片，共 72 个芯片，通常通过 DIMM 模块组织（如 8 个 x8 芯片构成一个 Rank，多个 Rank 构成一个 DIMM）。

## 代码示例

```python
# DRAM 刷新模拟
from collections import deque

class DRAMSimulator:
    def __init__(self, num_rows, refresh_interval_ms=64):
        self.num_rows = num_rows
        self.rows = [0] * num_rows  # 模拟存储
        self.refresh_interval = refresh_interval_ms
        self.time_since_refresh = [0] * num_rows  # ms
        self.refresh_count = 0
    
    def tick(self, ms=1):
        """模拟时间流逝，检查是否需要刷新"""
        for i in range(self.num_rows):
            self.time_since_refresh[i] += ms
        need_refresh = [i for i, t in enumerate(self.time_since_refresh) 
                       if t >= self.refresh_interval]
        return need_refresh
    
    def refresh(self, row):
        """刷新一行（重写数据以保持电荷）"""
        self.time_since_refresh[row] = 0
        self.refresh_count += 1
        # 实际操作：读出 -> 放大 -> 写回

# SRAM vs DRAM 参数对比
sram = {'speed_ns': 1, 'cell_size_T': 6, 'cost_per_bit': 10, 'refresh': False}
dram = {'speed_ns': 50, 'cell_size_T': 1, 'cost_per_bit': 1, 'refresh': True}
print(f"SRAM: {sram['cell_size_T']}T/cell, {sram['speed_ns']}ns")
print(f"DRAM: {dram['cell_size_T']}T+1C/cell, {dram['speed_ns']}ns (需刷新)")
```

## 关联页面

[[SDRAM与DDR]] [[存储器层次结构]] [[Cache概述]] [[存储器容量扩展]]
