---
title: TCP三次握手
course: 计算机网络
chapter: 传输层
difficulty: INTERMEDIATE
tags: [TCP, 三次握手, 连接建立, SYN, SYN-ACK, ISN, SYN Flood]
aliases: [TCP Three-Way Handshake, SYN, SYN-ACK, Connection Establishment]
source:
  - 谢希仁《计算机网络》第8版
  - RFC 793
updated_at: 2026-05-02
---

## 核心定义

TCP三次握手（Three-Way Handshake）是TCP协议建立面向连接通信的初始化过程，客户端和服务器通过交换三个特殊的TCP报文段来同步双方的初始序列号（ISN）、协商连接参数（MSS、窗口缩放因子、SACK等选项）并为可靠的数据传输做好准备。具体流程为：（1）第一次握手——客户端向服务器发送SYN=1, ACK=0, Seq=x, 无数据（消耗一个序号），客户端进入SYN-SENT状态；（2）第二次握手——服务器收到SYN后，若同意建立连接，回复SYN=1, ACK=1, Seq=y, ACK Number=x+1，服务器进入SYN-RCVD状态并分配连接资源（TCB，传输控制块）；（3）第三次握手——客户端收到SYN-ACK后，回复ACK=1, Seq=x+1, ACK Number=y+1（此报文段可携带数据），客户端进入ESTABLISHED状态，服务器收到该ACK后也进入ESTABLISHED状态。三次握手的核心逻辑是：(a)确认双方发送和接收能力都正常；(b)同步双方的初始序列号；(c)防止已失效的连接请求报文段突然到达服务器引起错误的连接建立。

## 关键结论

- 为什么是三次握手而不是两次：两次握手只能确认客户端的发送和服务器端的接收能力正常，但服务器端无法确认自己的发送能力是否正常（即客户端能否收到服务器的消息）。第三次ACK报文让服务器确认客户端的接收功能正常，从而双向通信都得到了验证
- 为什么不是四次或更多：三次已经足够完成双向发送/接收能力的确认和序列号同步（第二次握手就把服务器的SYN和ACK合并在一个报文段中），更多的握手没有额外收益只会增加时延
- 防止旧连接请求：假设网络中存在一个延迟到达的老SYN报文段，若只有两次握手，服务器会立即分配资源建立连接（认为客户端有连接请求），而客户端根本不认这个连接。三次握手中，客户端收到服务器回复的SYN-ACK后如果自己并未发起连接请求，会发送RST重置响应，服务器从而不会在无用连接上浪费资源
- SYN Cookie机制：为防止SYN Flood攻击耗尽服务器的半连接队列资源，SYN Cookie在收到SYN时不立即分配TCB，而是根据客户端IP/端口、服务器IP/端口、时间戳通过哈希算法生成一个加密的ISN（即Cookie）填入SYN-ACK的Seq字段；第三次握手验证ACK Number的Cookie值是否合法后再分配完整资源。这是典型的在安全性（消耗CPU做计算）和资源消耗（被SYN Flood耗尽内存）之间的权衡
- 半连接/全连接队列：服务器维护两个队列——SYN队列（半连接队列，存放收到SYN-未完成第三次握手的连接）和ACCEPT队列（全连接队列，已完成三次握手等待应用层accept()取走的连接）。若队列满，新的SYN可能被丢弃

## 易错点

1. **SYN报文段是否可以携带数据？** 标准允许SYN=1的报文段携带数据（如TFO，TCP Fast Open），但传统习惯不允许。如果携带数据了，该数据将被缓冲到连接建立完成（ESTABLISHED状态）后才交付应用层。

2. **第三次ACK丢失会怎样？** 服务器端在SYN-RCVD状态等待ACK时会启动定时器，若超时未收到ACK，服务器会重传SYN-ACK（第二次握手报文）。重传策略通常为指数退避（初始重传间隔约1秒或3秒，逐次加倍）。

3. **ISN不一定是纯粹的随机数**：虽然教科书说ISN是随机生成的，但某些现代实现（包括Linux）使用基于时间戳和MD5/SHA1生成的伪随机ISN，以防止ISN预测攻击（TCP Sequence Number Prediction Attack）。攻击者如果能准确猜测ISN，可以伪造TCP连接。

4. **同时打开（Simultaneous Open）**：当两端几乎同时发送SYN给对方时（极少见但TCP支持），双方都进入SYN-SENT状态，收到对方的SYN而非SYN-ACK后，双方各自回复SYN-ACK，最终经过四个报文段建立连接。这需要双方都知道对方的端口号，在实际应用中需要端口既不打洞很难实现。

## 例题

**例题1**：客户端使用端口50000向服务器80端口发起TCP连接。写出三次握手过程中三个报文段的关键字段（Seq, ACK, SYN, ACK标志位，数据部分字节数）的值。

**解答**：第1次：SrcPort=50000, DstPort=80, Seq=client_isn, ACK=0, SYN=1, ACKbit=0, Data=0。第2次：SrcPort=80, DstPort=50000, Seq=server_isn, ACK=client_isn+1, SYN=1, ACKbit=1, Data=0。第3次：SrcPort=50000, DstPort=80, Seq=client_isn+1, ACK=server_isn+1, SYN=0, ACKbit=1, Data可为0或更多。

**例题2**：SYN Flood攻击的原理和常见防御措施。

**解答思路**：SYN Flood是DDoS的经典形式，攻击者发送大量SYN报文（通常伪造不存在的源IP地址），目标服务器为每个SYN分配半连接资源后回复SYN-ACK，但由于源IP伪造，SYN-ACK的ACK应答永远等不到，服务器半连接队列（SYN队列）被填满，正常用户的SYN请求被丢弃，导致服务不可用。防御措施：(a)SYN Cookie（如前述）；(b)SYN Cache（限制每个源IP的半连接数量）；(c)定期清理半连接队列中超时的连接（TCP默认会重传SYN-ACK若干次后清理，但攻击能赶在清理前填满队列）；(d)tcp_syncookies内核参数启用（Linux）；(e)部署在云清洗中心做流量过滤。现代CDN和DDoS防护服务已能在边缘网络中拦截大量SYN Flood流量。

## 代码示例

```bash
# 查看TCP连接状态
netstat -ant | grep SYN
ss -tan state syn-sent
ss -tan state syn-recv

# 查看SYN Cookie设置
sysctl net.ipv4.tcp_syncookies     # 查看
sysctl -w net.ipv4.tcp_syncookies=1  # 启用

# 抓取三次握手过程
sudo tcpdump -i eth0 'tcp[tcpflags] & (tcp-syn) != 0' -nn
```

```python
# TCP三次握手状态机示意
TCP_STATES = {
    'CLOSED': {},
    'LISTEN': {},
    'SYN_SENT': {},
    'SYN_RCVD': {},
    'ESTABLISHED': {}
}

def tcp_connect_client(server_ip, server_port):
    """客户端三次握手流程"""
    # 生成随机ISN
    client_isn = generate_isn()
    # 第1次：发送SYN
    send_syn(server_ip, server_port, client_isn)
    state = 'SYN_SENT'
    
    # 等待第2次：SYN-ACK
    syn_ack = recv_syn_ack(timeout=3)
    if syn_ack and syn_ack.ack_num == client_isn + 1:
        # 验证服务器ISN和ACK有效性
        server_isn = syn_ack.seq_num
        # 第3次：发送ACK
        send_ack(server_ip, server_port, 
                 seq=client_isn + 1, 
                 ack=server_isn + 1)
        state = 'ESTABLISHED'
        return True
    else:
        # 收到RST或超时
        state = 'CLOSED'
        return False
```

## 关联页面

[[TCP四次挥手]] [[传输层-TCP首部]] [[TCP流量控制]] [[传输层-TCP拥塞控制]]
