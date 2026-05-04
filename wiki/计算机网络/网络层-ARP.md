---
title: ARP地址解析协议
course: 计算机网络
chapter: 网络层
difficulty: INTERMEDIATE
tags: [ARP, 地址解析, MAC地址, IP地址, ARP缓存, ARP欺骗, 免费ARP]
aliases: [Address Resolution Protocol, ARP Cache, ARP Spoofing, Gratuitous ARP]
source:
  - 谢希仁《计算机网络》第8版
  - RFC 826
updated_at: 2026-05-02
---

## 核心定义

ARP（Address Resolution Protocol，地址解析协议）是用于将网络层IP地址解析为数据链路层MAC地址的协议，工作于网络层与数据链路层之间。ARP的基本工作流程为：当源主机需要向目的IP地址发送数据包但不知道其MAC地址时，首先在本地ARP缓存（ARP Cache）中查找映射记录；如果没有找到（缓存未命中），则在本地局域网内广播一个ARP请求帧（以太网帧类型=0x0806），目的MAC地址为广播地址FF:FF:FF:FF:FF:FF，请求内容为"谁的IP地址是X.X.X.X？请告诉Y.Y.Y.Y"。局域网内所有主机收到该广播后，只有IP地址匹配的主机回复单播ARP应答，告诉源主机自己的MAC地址。源主机收到ARP应答后将映射关系存入ARP缓存（老化时间通常为600秒），之后就可以正常封装以太网帧并发送数据包。ARP仅作用于同一广播域（局域网）内，跨网段通信时需使用默认网关（路由器）的MAC地址。

## 关键结论

- ARP缓存的生命周期：动态条目有老化时间（通常Windows: 120-600秒，Linux: 通过gc_stale_time控制），静态条目永久有效。过期的缓存条目会通过ARP请求重新验证
- 免费ARP（Gratuitous ARP）：主机主动发送ARP广播宣告自己的IP-MAC映射（自己问自己的IP），用于检测IP地址冲突（若有其他主机回复，说明IP已被使用）和更新其他主机的ARP缓存（如切换网卡或更新MAC地址）
- 代理ARP（Proxy ARP）：路由器代表其他网段的主机回复ARP请求，将自己的MAC地址提供给请求方，从而使不同子网的主机可以"透明地"通信而无需配置默认网关（已被淘汰）
- ARP欺骗（ARP Spoofing/Poisoning）：攻击者发送伪造的ARP应答将合法IP地址映射到攻击者的MAC地址，实现中间人攻击或拒绝服务。防御措施包括静态ARP绑定、DAI（动态ARP检测）等
- RARP（反向ARP，RFC 903）协议用于无盘工作站从MAC地址获取IP地址，已被BOOTP和DHCP取代

## 易错点

1. **ARP是网络层协议还是链路层协议**：从功能看，ARP解决的是IP到MAC的映射，跨越了网络层和数据链路层。从封装形式看，ARP报文直接封装在以太网帧中（帧类型=0x0806），没有经过IP封装——所以ARP和IP是平行的网络层协议。严谨来说，ARP是处于网络层与数据链路层之间的"中间层"协议。

2. **跨越路由器的ARP解析**：当源主机和目的主机不在同一网段时，源主机会将数据包发给默认网关（路由器），ARP请求的是默认网关的MAC地址而不是目的主机的MAC地址。路由器收到数据包后进行路由转发，在新接口上重新封装帧并执行ARP解析下一跳的MAC地址。

3. **ARP缓存不是越大越好**：虽然ARP缓存能减少ARP广播，但保留大量过时的条目会导致通信失败（对方MAC地址已更新但缓存未刷新）。这就是为什么需要合理的缓存老化时间——太短导致频繁的ARP广播，太长导致陈旧信息误事。

4. **ARP没有安全机制**：ARP协议设计时假设局域网是可信的，无任何认证机制。任何主机都可以发送ARP应答声称自己是某个IP的拥有者，这是ARP欺骗攻击的根本原因。

## 例题

**例题1**：主机A(192.168.1.10/24)与主机B(192.168.2.20/24)通信，A的默认网关为192.168.1.1，B的默认网关为192.168.2.1。请描述A到B的全过程中ARP工作的完整流程。

**解答**：A判断B不在同一网段（因为B的IP属于192.168.2.0/24），A需要将数据包发给默认网关192.168.1.1。A查找ARP缓存中是否有192.168.1.1的MAC，若无则广播ARP请求192.168.1.1的MAC地址。路由器接口R1（192.168.1.1）回复ARP应答给A。A用R1的MAC封装数据包发往R1。R1收到后解封装，查路由表发现目的网段192.168.2.0/24通过接口R2（192.168.2.1）可达。R1查找ARP缓存中192.168.2.20的MAC，若无则在192.168.2.0/24网段广播ARP请求B的MAC。B回复ARP应答。R1用B的MAC重新封装帧发往B。

**例题2**：简述免费ARP的工作机制及其三个主要用途。

**解答思路**：免费ARP是主机主动发送的ARP请求，目标IP地址和源IP地址都填写为本机IP地址，以广播方式发送（目的MAC=FF:FF:FF:FF:FF:FF）。用途：（1）IP地址冲突检测——如果网络中有其他主机使用了相同的IP，它会回复ARP应答，源主机从而发现冲突；（2）更新其他主机的ARP缓存——当主机的MAC地址发生变更（如网卡替换或虚拟IP漂移）时，通过免费ARP通知局域网内其他主机更新ARP缓存；（3）高可用集群中的浮动IP接管——备用节点在接管VIP时发送免费ARP，引导交换机更新MAC地址表，将流量引向新节点。

## 代码示例

```bash
# 查看ARP缓存
arp -a              # Windows / Linux
ip neigh show       # Linux 推荐方式

# 手动添加静态ARP条目
arp -s 192.168.1.100 00:11:22:33:44:55    # Windows
ip neigh add 192.168.1.100 lladdr 00:11:22:33:44:55 dev eth0  # Linux

# 清除ARP缓存
arp -d 192.168.1.100        # Windows: 删除单条
ip neigh del 192.168.1.100 dev eth0   # Linux
arp -a -d                    # Windows: 清除所有
ip neigh flush all           # Linux: 清除所有

# 抓取ARP报文
sudo tcpdump -i eth0 arp -nn
```

```python
# Python使用scapy发送ARP请求（需管理员权限，仅供学习）
# from scapy.all import ARP, Ether, srp
# 
# def arp_request(ip):
#     arp = ARP(pdst=ip)
#     ether = Ether(dst="ff:ff:ff:ff:ff:ff")
#     packet = ether / arp
#     result = srp(packet, timeout=2, verbose=False)[0]
#     for sent, received in result:
#         return received.hwsrc    # MAC地址
```

## 关联页面

[[MAC地址]] [[以太网]] [[DHCP]] [[ICMP]] [[IPv4地址分类]]
