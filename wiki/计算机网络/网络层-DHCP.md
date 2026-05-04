---
title: DHCP动态主机配置协议
course: 计算机网络
chapter: 网络层
difficulty: INTERMEDIATE
tags: [DHCP, 动态IP分配, DHCP服务器, DHCP中继, DORA过程]
aliases: [Dynamic Host Configuration Protocol, DHCP Relay, DHCP DORA]
source:
  - 谢希仁《计算机网络》第8版
  - RFC 2131, RFC 2132
updated_at: 2026-05-02
---

## 核心定义

DHCP（Dynamic Host Configuration Protocol，动态主机配置协议）是用于自动为网络中的主机分配IP地址及其他网络配置参数（子网掩码、默认网关、DNS服务器等）的应用层协议，基于UDP协议，使用端口67（服务器）和68（客户端）。DHCP的前身是BOOTP协议，DHCP完全兼容BOOTP。DHCP的工作过程遵循DORA四阶段模型：Discover（发现）——客户端以255.255.255.255广播DHCP Discover消息寻找可用的DHCP服务器；Offer（提供）——DHCP服务器收到发现消息后，从地址池中选择一个可用IP地址通过单播或广播DHCP Offer消息提供给客户端；Request（请求）——客户端选择一个Offer（如有多个服务器响应）并广播DHCP Request消息请求该IP地址；Acknowledgment（确认）——服务器广播DHCP ACK消息确认分配，同时下发子网掩码、网关、DNS、租约时间等配置参数。DHCP采用租约（Lease）机制管理地址的分配和回收。

## 关键结论

- DHCP分配地址的三种方式：动态分配（默认，有租约期限）、自动分配（永久分配，类似BOOTP）、手动分配（根据MAC地址绑定固定IP，也称DHCP保留/静态绑定）
- DHCP租约更新流程：租约期的50%时客户端尝试单播续约（向原DHCP服务器直接发Request）；如果成功，租约被刷新。如果87.5%（7/8）时仍未成功，客户端广播Request向任何服务器请求续约。如果租约到期仍未获得确认，客户端必须停止使用该IP地址
- DHCP中继代理（DHCP Relay Agent）：由于DHCP Discover使用广播，跨子网时需要DHCP中继。中继代理在网关上运行，监听本网段的DHCP广播，将其以单播形式转发给指定DHCP服务器（并将giaddr字段设为中继接口IP），收到服务器回复后转发回客户端
- DHCP常见选项：Option 1 子网掩码、Option 3 默认网关、Option 6 DNS服务器、Option 15 域名、Option 51 租约时间、Option 53 DHCP消息类型、Option 61 客户端标识
- DHCP释放：客户端可以发送DHCP Release主动归还IP地址（如正常关机），但并非强制——服务器依赖租约过期机制回收未续约的地址

## 易错点

1. **DHCP不是网络层协议**：DHCP虽然是网络配置的基础协议，但它属于应用层协议，运行在UDP之上。不能因为它配置了IP地址就把它归类为网络层协议。网络层是处理IP包转发的，DHCP不参与数据包的路由。

2. **DHCP Offer和ACK为什么使用广播而非单播**：因为此时客户端还没有正式获得IP地址（Offer阶段虽然收到了提议的IP，但在完成全部四次握手之前该IP并未正式分配给客户端），目标IP地址不能确定可靠路由。实际上DHCP Offer可以通过客户端MAC地址单播（服务器发送到客户端MAC而非IP）。

3. **DHCP Discover源地址为0.0.0.0**：因为客户端此时没有任何IP地址，源地址为0.0.0.0，目的地址为255.255.255.255（受限广播），源端口为UDP 68，目的端口为UDP 67。

4. **多DHCP服务器的竞争**：如果网络中存在多个DHCP服务器，客户端会收到多个Offer，但最终只选择一个（通常是第一个到达的Offer）。被拒绝的服务器通过Request广播得知客户端选择了其他服务器，释放预留的地址。

## 例题

**例题1**：描述客户端从加入网络到获得正确IP地址并能够访问互联网的完整DHCP DORA过程。

**解答**：（1）Discover：客户端刚连接到网络，源IP=0.0.0.0，目的IP=255.255.255.255，广播DHCP Discover；（2）Offer：DHCP服务器（如192.168.1.1）收到发现消息，从未分配地址池中选一个（如192.168.1.100），广播Offer（yiaddr=192.168.1.100）；（3）Request：客户端收到Offer，广播DHCP Request确认选择（如果收到多个Offer，选择第一个）；（4）ACK：服务器最终广播ACK确认分配，并填充子网掩码、网关、DNS等Option。客户端获得IP后，可发送ARP免费包检测IP冲突，检测通过后将IP绑定到接口上。之后客户端配置默认路由指向网关，就可以通过网关访问互联网。

**例题2**：某公司网络规模不断扩大，现需在子公司A部署新的子网，但子公司A的交换机不支持VLAN DHCP Relay，且主DHCP服务器在总部数据中心。请给出两个可行的解决方案并简要分析。

**解答思路**：方案一：在子公司A部署DHCP中继——在连接子公司的路由器接口上配置ip helper-address指向总部DHCP服务器地址，该路由器接口收到DHCP广播后将其单播转发给总部服务器并回传。方案二：在子公司A本地部署辅助DHCP服务器——可以是总部DHCP服务器的故障转移伙伴，或独立服务器。方案一无需额外的服务器硬件，适合小规模的扩展；方案二可靠性更高（即使WAN链路中断本地也能保障地址分配），但增加了管理开销。

## 代码示例

```bash
# Linux客户端手动触发DHCP
sudo dhclient -v eth0          # 请求IP（详细模式）
sudo dhclient -r eth0          # 释放IP（发送DHCP Release）

# Windows
ipconfig /release              # 释放IP
ipconfig /renew                # 重新获取IP

# 查看DHCP租约信息
cat /var/lib/dhcp/dhclient.leases   # Linux
ipconfig /all                        # Windows

# 抓取DHCP报文
sudo tcpdump -i eth0 port 67 or port 68 -nn -v
```

```python
# Python使用socket模拟DHCP Discover（简化演示）
import socket

# DHCP Discover的基本结构
# DHCP运行在UDP 67(Server) / 68(Client)
# 此处展示构造Discover报文的思路，完整的DHCP报文构造较复杂
# 需设置：OP=1(请求), HTYPE=1(以太网), HLEN=6, HOPS=0
#        XID=随机, SECS=0, FLAGS=0x8000(广播),
#        CIADDR=0.0.0.0, YIADDR=0.0.0.0, SIADDR=0.0.0.0, GIADDR=0.0.0.0
#        CHADDR=客户端MAC地址
#        Options: 53=1(Discover), 55(参数请求列表), 255(END)
pass  # 实际实施需完整构造DHCP报文
```

## 关联页面

[[IPv4地址分类]] [[网络层-ARP]] [[网络层-NAT]] [[子网划分-CIDR]] [[应用层-DNS]]
