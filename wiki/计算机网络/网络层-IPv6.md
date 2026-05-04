---
title: IPv6协议详解
course: 计算机网络
chapter: 网络层
difficulty: ADVANCED
tags: [IPv6, 128位地址, 即插即用, NDP, IPv6首部, 过渡技术]
aliases: [IPv6, Internet Protocol Version 6, IPv6 Header, Dual Stack, NDP]
source:
  - 谢希仁《计算机网络》第8版
  - RFC 8200, RFC 4861
updated_at: 2026-05-02
---

## 核心定义

IPv6（Internet Protocol Version 6）是互联网工程任务组（IETF）设计的用于替代IPv4的下一代网络层协议。IPv6将地址空间从32位扩展到128位（可提供约3.4×10^38个地址），从根本上解决了IPv4地址耗尽问题。IPv6的首部格式简化为40字节固定长度（不含扩展首部），去除了IPv4中的首部校验和、分片字段等低效或重复字段，引入了流标签（Flow Label）支持QoS。IPv6地址采用冒号十六进制记法（Colon-Hexadecimal Notation），如2001:0db8:85a3:0000:0000:8a2e:0370:7334，并可进行前导零压缩和全零块压缩（::只能出现一次）。IPv6取消了广播，引入了任播（Anycast）地址类型。IPv6的过渡不能一蹴而就，需要通过双协议栈（Dual Stack）、隧道（Tunneling）和翻译（Translation/NAT64）三种技术逐步实现。

## 关键结论

- IPv6首部固定40字节（标准部分），共8个字段：版本(4bit, 6)、流量类型(8bit, DSCP+ECN用于QoS)、流标签(20bit, 新型QoS)、有效载荷长度(16bit)、下一个头(8bit, 取代IPv4协议字段+指示扩展头类型)、跳数限制(8bit, 类似TTL)、源地址(128bit)、目的地址(128bit)。相比IPv4最明显的变化：去掉首部校验和、分片字段移入扩展头、去掉首部长度字段（首部固定长度）
- IPv6地址分类：单播（Unicast，包括全局单播2000::/3、链路本地fe80::/10、唯一本地fc00::/7等）、组播（Multicast，ff00::/8，替代了IPv4广播）、任播（Anycast，与单播共用地址空间，发往最近节点）。IPv6中不再有广播
- IPv6地址自动配置：有状态自动配置（通过DHCPv6）和无状态自动配置（SLAAC，通过路由器通告RA中的前缀+EUI-64生成接口ID）。NDP邻居发现协议集成了IPv4中的ARP、ICMP路由器发现、ICMP重定向等功能
- IPv6分片仅由源端进行：中间路由器不再进行分片（与IPv4不同）。源端使用Path MTU Discovery（PMTUD）确定路径MTU，超过MTU时由源端扩展首部中的分片首部完成分片
- 过渡技术三大支柱：双协议栈（节点同时支持IPv4和IPv6）、隧道（IPv6数据封装在IPv4中传输，如6in4/6to4/ISATAP/Teredo）、翻译（NAT64/DNS64实现纯IPv6访问纯IPv4）

## 易错点

1. **IPv6的"全0地址"含义不同**：IPv6的::（全0地址）不是"本网络本主机"，而是"未指定地址"（Unspecified Address），用于DHCPv6等场景。环回地址是::1（正好128位全0再最后1位）。这两者不能等同IPv4的0.0.0.0和127.0.0.1来记忆。

2. **IPv6并非天然安全**：IPv6设计中推荐使用IPsec，但IPsec支持并非强制。很多初学的误解是"IPv6天然安全"，实际上IPv6在设计层面并没有增加比IPv4更多的安全性——地址空间大使得网络扫描变得困难，但这不是真正的安全性。

3. **扩展首部的"下一个头"链**：IPv6中每个扩展首部和上层协议头部都有一个"下一个头"字段，形成一个链表。例如：IPv6头→路由头→分片头→认证头→TCP头。解析数据包时需要遍历这个链才能找到TCP/UDP负载，不可直接按固定偏移量读取TCP头。

4. **NDP不是ARP的简单替代**：NDP（Neighbor Discovery Protocol）集成了IPv4中ARP、ICMP Redirect、ICMP Router Discovery等多项功能，基于ICMPv6（Type 133-137），使用组播而非广播。NDP的地址解析使用请求节点组播地址（ff02::1:ffxx:xxxx）代替全局广播。

## 例题

**例题1**：给出IPv6地址2001:0db8:0000:0000:ff00:0042:8329的有效压缩形式。

**解答**：步骤：去掉每个块的前导零：2001:db8:0:0:ff00:42:8329。中间连续的两个零块可以压缩为::，得到2001:db8::ff00:42:8329（注意::只能在一处使用，不能压缩非连续零块）。验证：::代表若干个完整的0块。

**例题2**：说明IPv6无状态地址自动配置（SLAAC）的完整工作流程，以及它与DHCPv6的角色分工。

**解答思路**：SLAAC流程：（1）主机生成链路本地地址（fe80::/10 + EUI-64接口标识）并通过DAD（重复地址检测）验证唯一性；（2）主机发送RS（路由器请求）报文到ff02::2（所有路由器组播地址）；（3）路由器回复RA（路由器通告）包含网络前缀和前缀长度等信息；（4）主机从RA中获取前缀，结合自身接口标识（EUI-64或随机生成）组装全局单播地址。DHCPv6分工：SLAAC只能分配IP地址，无法下发DNS服务器等配置参数（除非RA中包含RDNSS选项）。DHCPv6可以分配地址（有状态）和更多配置参数（无状态DHCPv6仅分配参数不管地址）。实践中两者互补使用（RA中M/O位控制：M=1使用有状态DHCPv6分配地址，O=1使用无状态DHCPv6获取其他配置参数）。

## 代码示例

```bash
# Linux查看IPv6地址
ip -6 addr show
ifconfig eth0 inet6

# 配置IPv6地址
ip -6 addr add 2001:db8::1/64 dev eth0

# 查看IPv6路由表
ip -6 route show

# 查看IPv6邻居缓存（类似IPv4 ARP缓存）
ip -6 neigh show

# ping IPv6
ping6 2001:db8::1
ping -6 fe80::1%eth0  # 链路本地地址需指定接口

# traceroute IPv6
traceroute6 2001:db8::1
```

```python
import ipaddress
import socket

# Python IPv6地址操作
ipv6_addr = ipaddress.IPv6Address('2001:db8::1')
print(f"压缩形式: {ipv6_addr.compressed}")
print(f"展开形式: {ipv6_addr.exploded}")
print(f"是否为链路本地: {ipv6_addr.is_link_local}")
print(f"是否为组播: {ipv6_addr.is_multicast}")

# IPv6网络
network = ipaddress.IPv6Network('2001:db8::/32')
print(f"网络地址: {network.network_address}")
print(f"总地址数: {network.num_addresses}")  # 注意这个数字极其巨大

# 创建IPv6 socket
sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
# 绑定IPv6地址
sock.bind(('::1', 8080, 0, 0))  # ::1 = IPv6环回地址
```

## 关联页面

[[IP协议]] [[IPv4地址分类]] [[子网划分-CIDR]] [[网络层-ICMP]] [[网络层-NAT]]
