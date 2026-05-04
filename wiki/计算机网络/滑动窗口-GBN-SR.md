---
title: 滑动窗口协议-GBN与SR
course: 计算机网络
chapter: 数据链路层
difficulty: ADVANCED
tags: [滑动窗口, GBN, SR, Go-Back-N, 选择重传, ARQ, 流水线]
aliases: [Sliding Window, Go-Back-N, Selective Repeat, Pipeline Protocol]
source:
  - 谢希仁《计算机网络》第8版
  - Kurose & Ross《Computer Networking》
updated_at: 2026-05-02
---

## 核心定义

滑动窗口协议是停止-等待协议的改进版本，通过流水线（pipelining）技术允许发送方在未收到确认前连续发送多个数据帧，从而大幅提高信道利用率。滑动窗口协议使用"发送窗口"和"接收窗口"两个核心概念来控制流量。发送窗口的大小W_S表示发送方最多可以连续发送而未收到确认的帧数；接收窗口的大小W_R表示接收方愿意接收的帧序号范围。根据接收窗口大小和处理策略的不同，滑动窗口协议主要分为两种：退回N步协议（GBN，Go-Back-N，W_S > 1，W_R = 1）和选择重传协议（SR，Selective Repeat，W_S > 1，W_R > 1）。GBN中接收方只按序接收，一旦某个帧丢失或出错，之后所有正确收到的帧都被丢弃，发送方超时后从出错的帧开始重传所有后续帧。SR中接收方可以接收并缓存乱序到达的帧，发送方只重传丢失或出错的个别帧。

## 关键结论

- GBN的核心策略是"累积确认 + 退回重传"：ACK n表示序号n及之前的所有帧都已正确收到；若帧k超时，发送方后退到帧k并重新发送帧k及之后的所有已发帧（即使其中一些可能已被正确接收）
- SR的核心策略是"逐个确认 + 选择重传"：每个帧单独确认，接收方缓存正确但乱序的帧；发送方只重传那些未收到确认的帧，避免不必要的重传
- 对于n比特的序号空间，GBN的发送窗口最大值为2^n - 1（需保证新旧帧不会混淆）；SR的发送窗口和接收窗口最大值之和≤2^n，通常取W_S = W_R = 2^(n-1)
- GBN实现简单（接收方只需维护一个状态变量expected_seq），但信道出错时效率低（一个帧出错可能导致大量不必要的重传）；SR实现复杂（接收方需缓存和重排序），但出错时只重传出错帧，效率更高
- 在链路误码率极低的环境（如光纤局域网）中，GBN和SR性能差异不大；在高误码率环境（如无线网络）中，SR远优于GBN

## 易错点

1. **GBN确认序号的含义**：ACK n表示n号及之前的所有帧都正确收到（累积确认）。如果发送方收到了ACK3但未收到ACK1和ACK2，意味着1、2、3都已正确收到。这与SR中每个确认只对应单个帧不同。

2. **SR接收窗口的错位问题**：设n=3（序号范围0-7），W_S=W_R=4。当接收方收到了帧0-3并提交上层后，接收窗口滑动为{4,5,6,7}。此时如果由于网络延迟原因收到一个延迟到达的旧帧0，该帧落在当前接收窗口内会被错误接受！为避免此问题，必须满足W_S+W_R ≤ 2^n = 8的限制。

3. **GBN的"退回N步"不是每次都退回所有W_S个帧**：退回的数量取决于超时触发的帧与最后一个被确认的帧之间的差距。如果帧0被确认后帧1-4都已发出但帧1超时，则退回重传帧1-4（而非全部帧0-4）。

4. **GBN和SR都有定时器管理问题**：GBN只需一个定时器（为最早未确认帧计时）；SR需要为每个未确认帧维护独立的定时器，定时器管理开销更大。

## 例题

**例题1**：某滑动窗口协议使用3比特帧序号，发送窗口W_S=5，接收窗口W_R=1。该协议属于哪种类型？若发送方一次发出帧0-4后，帧1丢失而帧2-4正确到达，请描述双方的处理过程和最终的确认/重传情况。

**解答**：W_S=5>1, W_R=1，属于GBN协议。处理过程：（1）发送方发出帧0-4后启动定时器；（2）接收方正确收到帧0，发送ACK0，滑动窗口到{1}；（3）帧1丢失，接收方不会超时等待而是继续接收；（4）接收方收到帧2，帧2不是期望的帧1，丢弃帧2并发送ACK0（累积确认最后正确帧）；（5）帧3和帧4同样被丢弃，分别回复ACK0；（6）发送方收到ACK0后知道帧0已被确认，但定时器仍在为帧1计时；（7）帧1定时器超时，发送方退回重传帧1、2、3、4（所有5帧中除已确认的帧0外都重传）。

**例题2**：比较GBN和SR在以下场景中的性能效率：发送窗口W=4，已发送帧0-3，帧1丢失而帧2-3正确到达。假设每个帧的发送时间为Td，RTT=5Td。

**解答思路**：GBN场景：接收方按序接收，丢弃帧2和3并回复ACK0（或发送NAK1）。发送方在帧1超时后重传帧1-3。总用时：4Td（发送4帧）+ 5Td（RTT等待/超时）+ 3Td（重传3帧）= 12Td。SR场景：接收方缓存帧2和3并回复ACK2和ACK3，只对帧1回复NAK1（或由发送方超时重传帧1）。发送方重传帧1。总用时：4Td（发送）+ 最短超时（收到ACK2/3后可能不等帧1超时就通过NAK触发重传，约4Td）+ 1Td（重传帧1）= 约9Td。SR效率约为GBN的1.33倍，在高误码率场景中优势会更显著。

## 代码示例

```python
class GBNSender:
    def __init__(self, window_size, seq_bits):
        self.window_size = window_size
        self.max_seq = 2 ** seq_bits
        self.base = 0           # 发送窗口下界（最早未确认帧）
        self.next_seq = 0       # 下一个可用的序号
        self.buffer = []        # 待发送缓冲区
    
    def send_available(self, data_list, channel):
        """尽可能多地在窗口内发送帧"""
        while self.next_seq < self.base + self.window_size and data_list:
            frame = data_list.pop(0)
            seq = self.next_seq % self.max_seq
            channel.transmit(frame, seq)
            self.next_seq += 1
            if self.base == self.next_seq - self.window_size:
                self._start_timer()
    
    def receive_ack(self, ack_seq):
        """收到累积ACK，滑动窗口"""
        if self._in_window(ack_seq):
            self.base = ack_seq + 1
            if self.base == self.next_seq:
                self._stop_timer()
            else:
                self._restart_timer()
    
    def timeout(self):
        """超时重传所有已发未确认帧"""
        self._start_timer()
        for seq in range(self.base, self.next_seq):
            self._retransmit(seq % self.max_seq)
```

## 关联页面

[[数据链路层-流量控制-停等协议]] [[数据链路层-成帧]] [[数据链路层-差错控制-CRC]] [[TCP流量控制]]
