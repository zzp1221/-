---
title: UDP用户数据报协议
course: 计算机网络
chapter: 传输层
difficulty: BASIC
tags: [UDP, 用户数据报协议, 无连接, 端口, 校验和, 伪首部]
aliases: [User Datagram Protocol, UDP Header, UDP Checksum]
source:
  - 谢希仁《计算机网络》第8版
  - RFC 768
updated_at: 2026-05-02
---

## 核心定义

UDP（User Datagram Protocol，用户数据报协议）是传输层的一种无连接、不可靠的数据传输协议。与TCP不同，UDP在发送数据之前不需要建立连接（没有握手过程），直接将应用层数据加上UDP首部后交给网络层发送。UDP首部十分简洁，仅8字节：源端口（2B）、目的端口（2B）、长度（2B，UDP首部+数据的总字节数）和校验和（2B，可选）。UDP提供的最核心功能是端口复用与分用——通过端口号将数据准确投递到目的主机的特定应用进程。UDP不提供连接管理、确认重传、流量控制和拥塞控制，因此传输效率高、时延低，非常适合实时音视频通信（VoIP/视频会议）、广播/组播（如DHCP、RIP）、DNS查询等对时延敏感但对丢包容忍度相对较高的应用场景，或者应用层自身已实现了可靠传输机制（如QUIC协议建立在UDP之上）。

## 关键结论

- UDP的核心设计哲学是"简约至上"——将可靠性实现留给应用层，传输层只做最基本的端口复用和可选的数据完整性检测。这种设计避免了TCP中复杂的拥塞控制算法对实时数据的时延影响
- UDP校验和计算包含"伪首部"（Pseudo-header）：12字节的伪首部包含源IP、目的IP、零填充字节、协议号(17)和UDP长度。伪首部的加入使得校验和能够验证IP层传递的源目地址信息是否正确，严格来说违反了分层原则但提升了检测能力
- UDP校验和是可选的：IPv4中UDP校验和可以为0（表示发送方未计算校验和），但IPv6中UDP校验和是强制的（因为IPv6首部无校验和，UDP必须承担部分检测责任）
- UDP的典型应用场景及原因：DNS（53端口，请求/应答各一个数据包即可完成，TCP建连开销太大）；RIP路由协议（520端口，定时广播路由表）；流媒体/实时通信（视频会议，对时延极度敏感，丢失几帧不影响体验）；DHCP（67/68端口，客户端刚开始没有IP地址，TCP无法建立连接）
- UDP虽然简单，但在高并发场景下可以利用其无连接的特性支撑远超TCP连接数上限的并发通信（没有连接状态表的内存压力），因此QUIC、HTTP/3等现代协议选择基于UDP构建

## 易错点

1. **UDP不是"绝对不可靠"**：虽然UDP本身不提供可靠传输机制，但在局域网环境中，UDP的丢包率通常极低（<0.01%）。"不可靠"是指协议不保证、不处理丢包情况，并非"一定会丢包"。

2. **UDP校验和的计算**：UDP校验和是可选的（IPv4时），但如果发送方计算了校验和（即便为0也要写为0xFFFF），接收方也必须验证。校验和检验失败的数据报直接丢弃，不向上层交付。UDP不会通知发送方校验和失败——应用层可能永远不知道某个UDP包因校验和错误被丢弃。

3. **UDP不保证发送顺序**：数据报到达目的地的顺序可能与发送顺序不同（网络层IP包的路由变化、负载均衡等因素导致）。应用层使用UDP需要自行处理乱序问题（如RTP协议中的序列号和时间戳）。

4. **UDP的"长度"字段包含首部自身**：UDP长度字段是2字节=16位，表示UDP数据报的总长度（首部8字节+数据部分），最小值为8（仅有首部无数据），最大值为65535（受限于IP总长度的16位限制）。当数据部分超过65527字节时需在IP层分片。

## 例题

**例题1**：UDP用户数据报的数据部分为8字节，计算UDP总长度字段的值。

**解答**：UDP首部固定8字节 + 数据8字节 = 16字节。所以长度字段 = 16（十进制）= 0x0010（十六进制）。注意：长度字段包含首部自身，且单位为字节。

**例题2**：比较TCP和UDP在以下场景中的适用性：(a)传输一个1GB的文件；(b)实时视频通话；(c)DNS域名查询；(d)发送路由协议的周期性更新。

**解答思路**：(a)文件传输：必须TCP——文件必须完整无误，使用TCP的确认重传、流量和拥塞控制。(b)视频通话：优先UDP——时延要求极高（<150ms端到端），容忍少量丢包（可通过FEC/PLC补偿），TCP的拥塞控制和重传会引入不可接受的抖动。(c)DNS查询：UDP优先（默认）——单个请求/应答的数据量小（通常<512字节），可装在一个UDP数据报中，无连接建连开销。但超长DNS响应（>512B，如DNSSEC）会自动切换到TCP。(d)路由更新：RIP使用UDP广播（无需可靠保证，定期全量更新）而OSPF直接使用IP（协议号89），BGP使用TCP（可靠传输路由信息）。选择的差异源于对可靠性和效率的不同权衡。

## 代码示例

```python
import socket
import struct

# UDP通信示例
# 服务端
server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server.bind(('0.0.0.0', 9999))
print("UDP服务器监听 9999 端口")

while True:
    data, addr = server.recvfrom(1024)
    print(f"收到来自 {addr} 的数据: {data.decode()}")
    server.sendto(b'ACK', addr)  # 注意：UDP需要手动确认（如果有此需求）

# 客户端
client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client.sendto(b'Hello UDP', ('127.0.0.1', 9999))
data, _ = client.recvfrom(1024)
print(f"收到回复: {data.decode()}")

def udp_checksum(source_ip, dest_ip, udp_data):
    """UDP校验和计算（包含伪首部+UDP首部+数据）"""
    # 构造伪首部
    pseudo_header = struct.pack('!4s4sBBH',
        socket.inet_aton(source_ip),
        socket.inet_aton(dest_ip),
        0, socket.IPPROTO_UDP, len(udp_data))
    
    full_data = pseudo_header + udp_data
    if len(full_data) % 2:
        full_data += b'\x00'
    
    total = 0
    for i in range(0, len(full_data), 2):
        total += struct.unpack('!H', full_data[i:i+2])[0]
    while total >> 16:
        total = (total & 0xFFFF) + (total >> 16)
    return ~total & 0xFFFF
```

## 关联页面

[[传输层-TCP首部]] [[TCP三次握手]] [[TCP流量控制]] [[传输层-TCP拥塞控制]]
