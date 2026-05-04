---
title: TCP四次挥手
course: 计算机网络
chapter: 传输层
difficulty: INTERMEDIATE
tags: [TCP, 四次挥手, 连接释放, FIN, 半关闭, TIME_WAIT, 2MSL]
aliases: [TCP Four-Way Wavehand, TCP Connection Termination, TIME_WAIT, Half-Close]
source:
  - 谢希仁《计算机网络》第8版
  - RFC 793
updated_at: 2026-05-02

---

## 核心定义

TCP四次挥手（Four-Way Wavehand）是TCP协议正常终止一个已建立连接的过程。由于TCP是全双工通信，每个方向的通信需要独立关闭，因此释放连接需要四个报文段。标准流程为：（1）主动关闭方发送FIN=1, Seq=u的报文段，告知对方"我没有数据要发送了"，进入FIN-WAIT-1状态；（2）被动关闭方收到FIN后，回复ACK=1, Seq=v, ACK Number=u+1进行确认，被动关闭方进入CLOSE-WAIT状态（此时主动方→被动方的方向已关闭，但被动方→主动方还可以继续发送数据）；（3）被动关闭方发送完所有剩余数据后，发送FIN=1, ACK=1, Seq=w, ACK Number=u+1（与第二步的ACK号相同因为中间没有收到新的数据），此时被动关闭方进入LAST-ACK状态；（4）主动关闭方收到被动方的FIN后，回复ACK=1, Seq=u+1, ACK Number=w+1，进入TIME-WAIT状态，等待2MSL时间后进入CLOSED状态。四次比三次多一次是因为服务器的SYN和ACK在握手时可以合并（收到了一个SYN可以同时回复SYN+ACK），但在挥手时分离——服务器的ACK是对客户端FIN的确认（收到即可确认），而服务器的FIN需要等服务器应用层主动关闭该方向的数据流，两者在时间上无法合并。

## 关键结论

- TIME-WAIT状态及其2MSL等待时间的两个目的：（1）确保最后一个ACK能被对方收到——若丢失，对方会重传FIN，主动方在TIME-WAIT期间可重发ACK；（2）让本连接持续时间内产生的所有延迟报文段都在网络中消失，防止旧连接的报文干扰同一端口对的新连接。MSL（Maximum Segment Lifetime，报文最大生存时间）的典型值为30秒（RFC 793建议2分钟），2MSL=60秒至2分钟
- TCP半关闭（Half-Close）：在第二次挥手后至第三次挥手期间，被动关闭方仍可向主动关闭方发送数据（主动方的接收功能正常），构成"半关闭"状态——从主动方到被动方的方向已关闭但反向仍通畅。HTTP/1.0利用半关闭表示请求发送完毕等待响应。`shutdown(sock, SHUT_WR)` 即可实现半关闭
- 主动关闭方经历的状态序列：ESTABLISHED→FIN-WAIT-1→FIN-WAIT-2→TIME-WAIT→CLOSED。被动关闭方：ESTABLISHED→CLOSE-WAIT→LAST-ACK→CLOSED（LISTEN状态在某些情况下也可能出现）
- 同时关闭（Simultaneous Close）：当双方几乎同时发送FIN，双方都进入FIN-WAIT-1，收到对方的FIN后进入CLOSING状态（而非FIN-WAIT-2），发送ACK后进入TIME-WAIT
- RST强制关闭：RST报文段可以强制断开连接而不需要四次挥手，接收方收到RST后直接进入CLOSED状态。RST用于异常终止——连接收到不属于该连接的报文（如连接不存在但收到了数据）、拒绝连接请求（如端口未开放）

## 易错点

1. **为什么需要TIME-WAIT且必须是2MSL**：TIME-WAIT只出现在主动关闭方。如果无TIME-WAIT，最后一个ACK丢失时对方重传的FIN将收到RST响应（连接已不存在），导致对方认为非正常关闭。另外，若无TIME-WAIT等待期间内同端口对的新连接可能收到该连接的延迟报文。2MSL = MSL（一个方向最大存活）+ MSL（反向存活），确保两个方向上的最后报文都过期。

2. **TIME-WAIT过多的问题**：高并发短连接场景（如HTTP/1.0每个请求一个TCP连接）中，主动关闭方（通常是服务器）积累大量TIME-WAIT套接字，虽然不占CPU但消耗内存和端口资源。解决方案：SO_REUSEADDR（重用地址）、tcp_tw_reuse（重用TIME-WAIT连接）、SO_LINGER（跳过TIME-WAIT，但不安全）、使用长连接或连接池。

3. **CLOSE-WAIT大量堆积说明什么？** 当被动关闭方（通常是服务端应用）收到FIN后未调用close()或shutdown()向客户端发送FIN，CLOSE-WAIT会大量堆积。这通常表明应用代码中连接关闭的逻辑存在问题——服务端忘记主动关闭已完成通信的连接。

4. **最后一次挥手中的ACK丢失与三次握手第三次ACK丢失的处理**：类似但状态不同。挥手时如果最后的ACK丢失，被动关闭方超时后重传FIN（它处于LAST-ACK等待ACK），主动方如果还在TIME-WAIT状态会重发ACK。如果ACK丢失后主动方2MSL到期已经CLOSED，被动方的重传FIN到达时会收到RST——对于被动方来说这也是正常结束（连接已无对端）。

## 例题

**例题1**：在四次挥手中，被动方发送ACK和FIN之间可能经过较长的时间间隔。这个过程TCP处于什么状态？这个时间间隔存在的实际场景有哪些？

**解答**：被动方收到FIN后发送ACK并进入CLOSE-WAIT状态，主动方进入FIN-WAIT-2状态。此时间间隔内，被动方（应用层）可能还需向主动方发送剩余数据（半关闭状态的反向数据）。实际场景：HTTP/1.0中客户端发送请求后主动半关闭连接（表示请求完毕），服务器处理请求后发送HTTP响应（反向数据），然后服务器主动关闭连接——服务器既有CLOSE-WAIT（收到客户端FIN后）又会主动发送FIN（响应发送完毕）。类似地，数据库协议中的查询完成指示也常使用半关闭。

**例题2**：分析以下TCP异常场景：如果客户端在发送FIN后、收到服务器ACK前崩溃重启了（操作系统重启，TCP连接状态丢失），服务器会怎样？如果网络故障导致FIN永远无法到达服务器呢？

**解答思路**：场景一——客户端崩溃：服务器不知道客户端崩溃，认为连接仍然存在（ESTABLISHED状态），如果服务器尝试发送数据，多次重传失败后会触发TCP保活机制（Keep-Alive）或发送探测报文，最终超时后服务器关闭连接。场景二——FIN丢失：客户端发送FIN后进入FIN-WAIT-1等待ACK，超时后重传FIN，指数退避算法增加重传间隔（典型：1s, 2s, 4s, 8s, 16s, 32s...），多次重传失败后放弃，直接进入CLOSED。服务器端可能也会因为长期无数据传输触发Keep-Alive探测或RST。

## 代码示例

```bash
# 查看各种TCP状态的数量
netstat -ant | awk '{print $6}' | sort | uniq -c | sort -rn
ss -tan state time-wait | wc -l    # 统计TIME-WAIT数量
ss -tan state close-wait | wc -l   # 统计CLOSE-WAIT数量

# 调整系统TIME-WAIT相关参数
sysctl net.ipv4.tcp_tw_reuse        # 查看是否启用TIME-WAIT重用
sysctl net.ipv4.tcp_fin_timeout     # FIN-WAIT-2超时时间
```

```python
# TCP连接关闭的四种方式
# 1. 正常四次挥手 close() ——全双工关闭
# sock.close()

# 2. 半关闭 shutdown() ——仅关闭写方向
# sock.shutdown(socket.SHUT_WR)   # 发送FIN，但仍可读
# sock.shutdown(socket.SHUT_RD)   # 关闭读方向
# sock.shutdown(socket.SHUT_RDWR) # 关闭读写方向（不发送FIN，只标记）

# 3. SO_LINGER选项 ——控制close()行为
# linger = struct.pack('ii', 1, 0)  # 立即关闭，发送RST
# sock.setsockopt(socket.SOL_SOCKET, socket.SO_LINGER, linger)

# 4. SO_REUSEADDR ——允许重用TIME-WAIT状态的地址
# sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
```

## 关联页面

[[TCP三次握手]] [[传输层-TCP首部]] [[TCP流量控制]] [[传输层-TCP拥塞控制]]
