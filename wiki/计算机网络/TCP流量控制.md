---
title: TCP流量控制
course: 计算机网络
chapter: 传输层
difficulty: INTERMEDIATE
tags: [TCP, 流量控制, 滑动窗口, 接收窗口, 零窗口, 糊涂窗口综合征]
aliases: [TCP Flow Control, Sliding Window, Receive Window, Zero Window, Silly Window Syndrome]
source:
  - 谢希仁《计算机网络》第8版
  - RFC 793, RFC 813
updated_at: 2026-05-02

---

## 核心定义

TCP流量控制（Flow Control）是TCP协议中防止发送方发送数据过快导致接收方缓冲区溢出的一种端到端控制机制。TCP采用基于滑动窗口的流量控制方法：接收方在每一个ACK报文段的窗口字段（Window字段）中通告自己接收缓冲区的剩余可用空间（即接收窗口rwnd，Receive Window），发送方以此窗口值作为自己能连续发送（未收到确认）的最大数据量——发送窗口swnd = min(rwnd, cwnd)，其中cwnd为拥塞控制窗口。接收方通过动态调整窗口大小来控制发送方的发送速率：窗口大→鼓励发送方快速发送，窗口为0→暂停发送。TCP流量控制的核心智慧在于它让接收方能够根据自身处理能力和应用层消费速度来调节数据流入速率，实现端到端的速率匹配，防止快发/慢收导致的不必要丢包和重传。

## 关键结论

- 发送窗口的三个边界：发送窗口的左沿 = 已发送且已确认的最后一个字节（发送窗口只有向前滑动不会后退）；发送窗口的右沿 = 左沿 + 发送窗口大小；窗口内分为"已发送但未确认"和"允许发送但尚未发送"两部分
- 零窗口问题（Zero Window）：当接收方缓冲区满、应用层来不及消费数据时，通告窗口为0。发送方接收到窗口为0后停止发送数据，并启动"窗口探测定时器"（Persist Timer），定时发送1字节的探测报文段查询接收方是否已释放缓冲区空间。接收方在ACK中回复新的窗口值。如果该ACK丢失，发送方可能永远等待——这就是Persist Timer存在的原因
- 窗口更新通知（Window Update）：接收方缓冲区空间释放后可能发送纯ACK报文（无数据携带）更新窗口大小给发送方。但如果这个ACK在网络中丢失，发送方将不？知窗口已经打开——此时唯一的数据发送机会即Persist Timer的探测报文
- 糊涂窗口综合征（Silly Window Syndrome, SWS）：当接收方每次只释放很小的缓冲区空间（如几个字节）就立即通知发送方，发送方也立即发送很少的数据填满窗口，导致网络中充斥大量携带非常少量数据的报文段（高头部开销、低有效载荷效率）。解决方案：(a)接收方规则——只在缓冲区空间达到MSS一半或一个MSS大小以上时才发送窗口更新（实际实现中使用Clark算法——延迟窗口更新直到可用空间显著增加）；(b)发送方规则——Nagle算法——发送方尽可能等到能凑够一个MSS大小的数据再发送，但对于需要立即响应的交互式应用优先发送（不用等待）
- Nagle算法与延迟确认（Delayed ACK）的相互作用可能带来性能下降：Nagle算法等待凑满MSS才发送下一段数据，而延迟确认延迟发送ACK（通常200ms），两者互相等待可能导致死锁或显著的延迟增加——在需要低延迟的交互式应用中往往需要禁用Nagle算法（TCP_NODELAY选项）

## 易错点

1. **流量控制与拥塞控制的混淆**：流量控制是端到端的（发送方 vs 接收方），关注接收方的处理能力；拥塞控制是发送方对网络拥塞程度的判断和响应，关注整个端到端路径上网络的承载能力。两者使用不同的窗口机制驱动——rwnd来自接收方通告，cwnd来自发送方的拥塞控制算法计算。

2. **rwnd不是发送窗口的绝对上限**：发送窗口 = min(rwnd, cwnd) ，两者都约束发送速率。当网络拥塞时cwnd可能远小于rwnd；当接收方缓冲区有限时rwnd可能远小于cwnd。真正限制发送速率的是两者中的较小者。

3. **窗口缩放选项和实际窗口大小**：当BDP（时延带宽积）很大时，16位窗口（最大65535字节）远远不够。Window Scale Option（RFC 1323）允许窗口左移n位（实际窗口 = 窗口字段值 × 2^n），n最大14（窗口最大~1GB）。该选项在SYN段协商，且必须在两侧都确认后才生效。

4. **零窗口死锁和Persist Timer**：如果接收方窗口从0变为非0时发送的Window Update ACK丢失，双方都会等待对方而陷入死锁。Persist Timer（窗口探测定时器）的特殊性在于——它在收到0窗口后启动，超时发送1字节探测报文，即使超时后仍收到0窗口回复，Persist Timer也会重新计时，确保最终窗口打开时发送方能感知。

## 例题

**例题1**：接收方的接收缓冲区大小为4KB，初始时有1KB空闲空间。发送方以1KB/s的速度发送数据，接收方应用层以200B/s的速度消费数据。以时间轴描述接收窗口rwnd的变化和发送方发送速率的变化。

**解答**：初始rwnd=1KB，发送方发送1KB后窗口变为0（停止发送）。接收方缓冲区现有1KB数据（1KB空闲+1KB接收=满），应用层以200B/s消费，1秒后可消费200B，rwnd通告变为200B，发送方发送200B。2秒后再消费200B，rwnd=200B...如此反复，发送方的平均发送速率被限制为约200B/s，与接收方消费速率匹配。最终缓冲区数据清空后，rwnd稳定在应用消费速率×RTT的平衡点上。

**例题2**：解释Nagle算法和延迟确认（Delayed ACK）之间的互操作性冲突问题，并给出解决方案。

**解答思路**：Nagle算法规则：只有前一个发送的数据被确认（收到了ACK），或者待发送数据已达到MSS大小，才能发送下一个报文段。延迟确认：收到数据后不立即回复ACK，等待200ms看看是否有反向数据可以捎带ACK，或者等待第二个数据段到达再一次性发两个ACK。冲突场景：发送方发了小段数据后Nagle等待凑满MSS→等不到新数据（应用层没有更多的请求）→等待前一个数据的ACK；接收方延迟200ms才发送ACK→发送方在200ms内不能发送新请求→整体延迟增加了200ms。解决方案：(a)在实时交互应用中设置TCP_NODELAY禁用Nagle；(b)接收方对交互式流量使用快速ACK（不延迟）；(c)应用层设计上避免连续发送小数据段——合并为一个大请求。

## 代码示例

```python
# Python TCP流量控制相关Socket选项
import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# 禁用Nagle算法（适合低延迟交互式应用）
sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

# 设置收发缓冲区大小（影响rwnd）
SEND_BUF = 65536
RECV_BUF = 65536
sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, SEND_BUF)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, RECV_BUF)

# SO_RCVLOWAT - 接收低水位线（recv返回所需的最小数据量）
sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVLOWAT, 1)

# Linux启用TCP窗口缩放
# sysctl -w net.ipv4.tcp_window_scaling=1
```

```bash
# 查看TCP连接的实际窗口和缓冲区
ss -tmi   # 详细连接信息包括rwnd、cwnd、rtt等
# 输出示例中的关键指标：
#   rcv_space: 接收窗口自动调整值
#   rcv_ssthresh: 接收窗口初始值
#   snd_wnd: 当前发送窗口
#   rcv_wnd: 当前接收窗口
```

## 关联页面

[[传输层-TCP拥塞控制]] [[传输层-TCP首部]] [[滑动窗口-GBN-SR]] [[网络概述-性能指标]]
