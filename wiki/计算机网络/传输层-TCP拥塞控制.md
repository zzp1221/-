---
title: TCP拥塞控制
course: 计算机网络
chapter: 传输层
difficulty: ADVANCED
tags: [TCP, 拥塞控制, 慢启动, 拥塞避免, 快重传, 快恢复, Tahoe, Reno, CUBIC]
aliases: [TCP Congestion Control, Slow Start, Congestion Avoidance, Fast Retransmit, Tahoe, Reno]
source:
  - 谢希仁《计算机网络》第8版
  - RFC 5681, RFC 8312
updated_at: 2026-05-02

---

## 核心定义

TCP拥塞控制（Congestion Control）是TCP协议中控制发送方向网络中注入数据速率、防止网络拥塞的机制。与流量控制关注接收方能力不同，拥塞控制关注的是端到端路径上网络链路的承载能力。TCP通过维护一个拥塞窗口（cwnd）来调节发送速率，实际发送窗口 = min(rwnd, cwnd)。拥塞控制基于"丢包==网络拥塞"的隐式信号（在传统TCP中），通过四个核心算法实现自适应调节：慢启动（Slow Start）、拥塞避免（Congestion Avoidance）、快重传（Fast Retransmit）和快恢复（Fast Recovery）。现代TCP的拥塞控制有多种实现变种：Tahoe（最早版本）、Reno（最广泛）、NewReno、Vegas（基于RTT而非丢包）、CUBIC（Linux默认）和BBR（Google基于带宽和RTT的模型）等。拥塞控制是互联网稳定运行的基石，没有它全网将陷入"拥塞崩溃"。

## 关键结论

- 慢启动（Slow Start）并不"慢"：初始cwnd=1 MSS（现代实现初始为10 MSS），每收到一个ACK将cwnd加倍（指数增长），直到达到慢启动阈值（ssthresh）或检测到拥塞。慢启动的名称来自于与之前无拥塞控制时一次性发送整个接收窗口数据的对比
- 拥塞避免（Congestion Avoidance）：cwnd≥ssthresh时进入拥塞避免阶段，每个RTT将cwnd增加1 MSS（线性增长，Additive Increase），小心翼翼探测网络剩余容量
- 丢包检测的两种方式：（1）超时重传（RTO Expired）——发送方认为网络严重拥塞，将ssthresh设为cwnd/2，cwnd重置为1 MSS，重新进入慢启动；（2）收到三个重复ACK（3 Duplicate ACKs）——表示少量丢包（网络仍能传输数据），ssthresh=cwnd/2，cwnd=ssthresh+3（快重传/快恢复），然后进入拥塞避免而非慢启动
- Tahoe vs Reno的区别：Tahoe在超时和三次重复ACK时都执行相同的动作（ssthresh=cwnd/2, cwnd=1, 慢启动）。Reno引入了快重传（三次重复ACK立即重传缺失报文而不等超时）和快恢复（收到三次重复ACK时不回到慢启动，而是将cwnd减半后直接进入拥塞避免阶段），这是对偶发包丢失的优化
- CUBIC算法（Linux内核默认）：取代传统AIMD的Reno算法，使用三次函数作为窗口增长函数，在接近上次丢包点（W_max）时谨慎增长（凹函数区域），在远离W_max时更快探测（凸函数区域），提高了高BDP网络中的带宽利用率

## 易错点

1. **cwnd的单位是MSS而不是字节**：许多资料中cwnd按MSS计算。初始cwnd=1 MSS（约1460字节），每次增长也是按MSS。具体实现中cwnd和rwnd都按字节计算，但拥塞控制的逻辑以MSS为粒度。

2. **慢启动的指数增长不是无限的**：cwnd从1到2到4到8到16...听起来增长极快，但有上限ssthresh。当cwnd≥ssthresh时切换到线性增长。初始ssthresh可以设得很大（Linux初始为无限），但在第一次丢包后就由丢包事件更新为cwnd/2。

3. **重复ACK不一定是丢包**：收到重复ACK还可以是因为报文段乱序到达。标准要求收到3个重复ACK才触发快重传（降低因乱序而误判丢包的概率）。如果只收到1-2个重复ACK，不触发快重传。

4. **TCP拥塞控制不是端到端的唯一参与者**：路由器中的AQM（主动队列管理）机制，如RED/ECN，也在参与拥塞控制。ECN（显式拥塞通知）允许路由器标记（而非丢弃）数据包让其通过，发送方在收到带CE标记的ACK时早期响应拥塞（降低cwnd而不需要丢包），显著提高网络效率。

## 例题

**例题1**：一个TCP连接使用Reno拥塞控制，ssthresh初始=8 MSS，cwnd=1 MSS。传输过程中cwnd=12时发生了超时。描述cwnd和ssthresh从开始到超时再到恢复的完整变化过程。

**解答**：（1）慢启动阶段：cwnd=1→2→4→8（指数增长），达到ssthresh=8后进入拥塞避免；（2）拥塞避免阶段：cwnd=8→9→10→11→12（每RTT+1），在cwnd=12时超时；（3）超时响应：ssthresh=cwnd/2=6，cwnd=1，重新进入慢启动；（4）慢启动：cwnd=1→2→4→6（指数增长），达到ssthresh=6后进入拥塞避免；（5）拥塞避免：cwnd=6→7→8→9...继续线性增长。注意：Reno中超时事件不触发快恢复（快恢复只在三次重复ACK时触发）。

**例题2**：CUBIC与Reno的区别及CUBIC在高BDP网络中的优势。

**解答思路**：Reno使用AIMD（加性增乘性减），每个RTT增加1 MSS，丢包后cwnd减半，在高速高时延网络中恢复速度慢（因为窗口增长速率恒定与RTT无关，RTT大的网络需要很长时间才能填满可用带宽）。CUBIC的窗口增长函数是cwnd = C×(t-K)^3 + W_max，其中t是自上次丢包以来的时间，K是到达W_max所需时间，C为缩放常数。这种三次函数增长特性使CUBIC：（1）在接近W_max时更保守（减少丢包概率）；（2）在远离W_max时加速探测（更快利用空闲带宽）；（3）窗口增长速率独立于RTT（高RTT网络的公平性更好）。现代CDN和大文件传输普遍使用CUBIC。

## 代码示例

```python
class TCPReno:
    """TCP Reno 拥塞控制简化模型"""
    def __init__(self):
        self.cwnd = 1.0         # 拥塞窗口 (MSS)
        self.ssthresh = 64.0    # 慢启动阈值
        self.dup_ack_count = 0  # 重复ACK计数
        self.state = 'SLOW_START'
    
    def on_ack(self):
        """收到新ACK"""
        self.dup_ack_count = 0
        if self.state == 'SLOW_START':
            self.cwnd += 1.0  # 指数增长（每个ACK cwnd+1MS相当于每RTT翻倍）
            if self.cwnd >= self.ssthresh:
                self.state = 'CONGESTION_AVOIDANCE'
        elif self.state == 'CONGESTION_AVOIDANCE':
            self.cwnd += 1.0 / self.cwnd  # 线性增长（每RTT +1）
        elif self.state == 'FAST_RECOVERY':
            self.cwnd = self.ssthresh
            self.state = 'CONGESTION_AVOIDANCE'
    
    def on_dup_ack(self):
        """收到重复ACK"""
        self.dup_ack_count += 1
        if self.dup_ack_count == 3:
            # 快重传 + 快恢复
            self.ssthresh = max(self.cwnd / 2, 2.0)
            self.cwnd = self.ssthresh + 3
            self.state = 'FAST_RECOVERY'
            return True  # 触发重传
        elif self.state == 'FAST_RECOVERY':
            self.cwnd += 1.0  # 在快恢复中每收到一个重复ACK增加cwnd
        return False
    
    def on_timeout(self):
        """超时重传"""
        self.ssthresh = max(self.cwnd / 2, 2.0)
        self.cwnd = 1.0
        self.state = 'SLOW_START'
        self.dup_ack_count = 0

# 模拟TCP拥塞窗口变化
reno = TCPReno()
for rtt in range(1, 20):
    reno.on_ack()
    print(f"RTT {rtt}: cwnd={reno.cwnd:.1f}MSS, state={reno.state}")
```

## 关联页面

[[TCP流量控制]] [[传输层-TCP首部]] [[TCP三次握手]] [[网络概述-性能指标]] [[TCP拥塞控制算法对比]]
