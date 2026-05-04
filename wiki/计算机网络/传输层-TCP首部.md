---
title: TCP首部格式详解
course: 计算机网络
chapter: 传输层
difficulty: ADVANCED
tags: [TCP, 首部格式, 端口, 序号, 确认号, 标志位, 窗口, 选项]
aliases: [TCP Header, TCP Segment Format, Sequence Number, ACK Number]
source:
  - 谢希仁《计算机网络》第8版
  - RFC 793, RFC 1323
updated_at: 2026-05-02
---

## 核心定义

TCP（Transmission Control Protocol，传输控制协议）的首部是TCP报文段（Segment）的控制部分，标准长度为20字节（不含选项）。TCP首部格式设计精妙，包含了实现面向连接、可靠传输、全双工通信、流量控制和拥塞控制所需的所有控制字段。主要字段包括：16位源端口号和目的端口号（标识发送和接收应用进程）、32位序号（Segment序号，以字节为单位的发送数据第一个字节编号）、32位确认号（期望收到的下一个字节序号，同时起到累积确认作用）、4位数据偏移/首部长度、6位保留字段、6个控制标志位（URG/ACK/PSH/RST/SYN/FIN）、16位窗口大小（接收方通告的剩余接收缓冲区大小，用于流量控制）、16位校验和（校验首部+数据+伪首部）、16位紧急指针（仅在URG=1时有效）。此外，TCP选项字段（可变长度，最常用的是MSS最大报文段大小选项、窗口缩放因子、SACK选择性确认和时间戳选项）可以在建立连接时通过SYN报文段协商。

## 关键结论

- TCP序号（Sequence Number）是该报文段数据部分第一个字节在发送的整个字节流中的编号。初始序号（ISN）随机生成（防止被伪造攻击），SYN和FIN报文段各消耗一个序号（即使不带数据）。确认号（ACK Number）表示期望接收的下一个字节序号，具有累积确认的功能——ACK n意味着n之前的字节全部收到
- TCP的6个标志位：URG（紧急指针有效）、ACK（确认号有效，连接建立后所有报文段都置ACK=1）、PSH（催促接收方立即交付应用层而不等到缓冲区填满）、RST（重置连接，拒绝非法报文或异常终止连接）、SYN（同步序号，仅在三次握手的前两次出现）、FIN（发送方无更多数据需发送，请求终止连接）
- 数据偏移字段（4bit），单位是4字节（32bit字），表示TCP首部长度。最小值为5（20字节标准首部），最大值为15（60字节，即选项字段最多40字节）
- MSS最大报文段大小（Maximum Segment Size）是SYN报文段中的重要选项，表示发送方愿意接收的最大数据段长度（不含TCP首部）。MSS = MTU - 20(IP首部) - 20(TCP首部)，以太网环境典型值为1460字节
- 窗口缩放因子（Window Scale Option）扩展了16位窗口字段的表示范围。实际窗口大小 = 窗口字段值 × 2^(缩放因子)。不使用缩放因子时窗口最大为65535字节，使用缩放因子（最大14）窗口最大可到约1GB，解决了长肥网络（LFN）问题

## 易错点

1. **序号和确认号的方向**：TCP是全双工的，两个方向的通信独立编号。A→B方向的序号基于A的ISN，A→B的确认号是对B向确认号。不能把两个方向的序号混在一起理解。

2. **ACK与ACK标志的区分**：ACK可指确认号字段，也可指ACK标志位（控制位）。建立连接后所有的TCP报文段都设置ACK=1；但"发送一个ACK报文段"通常指的是仅携带ACK标志（无数据）的纯确认报文。

3. **PSH标志并非一定被应用层识别**：PSH标志提示接收方尽快将数据交付应用层（不要缓冲）。但实际上许多TCP实现（尤其是Berkeley Socket API）不向应用层暴露PSH标志——推送机制依赖于TCP实现的选择而不是应用层可以强制控制的。

4. **窗口探测机制**：当接收方通告窗口为0（缓冲区满）时，发送方停止发送数据并启动"窗口探测定时器"（Persist Timer），定时发送1字节的探测报文段查询接收方窗口是否已打开。接收方回复的ACK若仍为0则重新等待；若不为0则回复ACK包含新的窗口大小，发送方恢复发送。这与重传定时器是不同的机制。

## 例题

**例题1**：主机A向主机B发送一个TCP报文段：Seq=100, ACK=200, 数据部分200字节。B收到后回复的TCP报文段的Seq和ACK分别应为多少？（假设B已无数据发送）

**解答**：A发送的报文段数据部分200字节，序号100-299（共200字节）。B回复纯ACK报文段（无数据），确认号 = 100+200 = 300（表示期望接收第300个字节）。B的序号 = B上一次发给A的最后字节序号+1，题目未给B的发送历史，无法精确确定。如果B之前最后发送的字节序号是199，则B回复Seq=200, ACK=300。

**例题2**：MSS和MTU的关系，以及TCP如何通过MSS避免IP层分片。

**解答思路**：MTU（Maximum Transmission Unit）是数据链路层帧的最大有效载荷长度，以太网MTU=1500字节。MSS = MTU - IP首部(20B) - TCP首部(20B) = 1460B。发送方在SYN报文中通告自己的MSS（实际上是对端的接收MSS），双方选择较小的MSS作为该连接的MSS。TCP将应用层数据（字节流）按MSS分块，每块加上TCP首部成为TCP报文段，再交给IP层封装，此时IP数据包总长为MSS+20+20≤MTU，自然不需要IP分片。这就是TCP避免IP分片的机制。如果路径中存在MTU更小的链路（如PPPoE隧道），可能还需要PMTUD配合。

## 代码示例

```python
import struct

class TCPHeader:
    def __init__(self, src_port, dst_port, seq, ack, flags, window=65535):
        self.src_port = src_port
        self.dst_port = dst_port
        self.seq = seq
        self.ack = ack
        self.data_offset = 5  # 20字节，无选项
        self.flags = flags    # 如 {'SYN': 1, 'ACK': 0}
        self.window = window
    
    def pack(self):
        """打包为二进制（简化，不含选项和校验和）"""
        # 标志位编码
        flags_byte = 0
        if self.flags.get('URG'): flags_byte |= 0x20
        if self.flags.get('ACK'): flags_byte |= 0x10
        if self.flags.get('PSH'): flags_byte |= 0x08
        if self.flags.get('RST'): flags_byte |= 0x04
        if self.flags.get('SYN'): flags_byte |= 0x02
        if self.flags.get('FIN'): flags_byte |= 0x01
        
        data_offset_reserved = (self.data_offset << 4) | 0
        
        return struct.pack('!HHIIBBH',
            self.src_port, self.dst_port,
            self.seq, self.ack,
            data_offset_reserved, flags_byte, self.window)

# TCP选项：MSS
def create_mss_option(mss=1460):
    """构造MSS TCP选项"""
    kind = 2       # MSS选项类型
    length = 4     # 选项总长度（含kind和length自身）
    return struct.pack('!BBH', kind, length, mss)
```

## 关联页面

[[TCP三次握手]] [[TCP四次挥手]] [[TCP流量控制]] [[传输层-TCP拥塞控制]] [[传输层-UDP]]
