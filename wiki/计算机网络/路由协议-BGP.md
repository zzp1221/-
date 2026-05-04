---
title: BGP边界网关协议
course: 计算机网络
chapter: 网络层
difficulty: ADVANCED
tags: [BGP, 外部网关协议, AS, 路径矢量, AS_PATH, eBGP, iBGP, BGP属性]
aliases: [Border Gateway Protocol, BGP-4, Path Vector, AS_PATH, eBGP, iBGP]
source:
  - 谢希仁《计算机网络》第8版
  - RFC 4271
updated_at: 2026-05-02
---

## 核心定义

BGP（Border Gateway Protocol，边界网关协议）是互联网使用的唯一外部网关协议（EGP），用于在不同的自治系统（AS，Autonomous System）之间交换路由信息。BGP当前版本为BGP-4，采用路径矢量（Path Vector）路由算法，即路由器记录到达目标网络的完整AS路径序列（AS_PATH属性），而非仅记录下一跳或跳数。BGP的设计目标是可伸缩性、稳定性和基于策略的路由（Policy-Based Routing），而不追求最短路径（与IGP不同）。BGP通过TCP 179端口建立可靠的BGP Peering会话（BGP邻居关系），分为两个类别：eBGP（External BGP，不同AS之间的对等体）和iBGP（Internal BGP，同一AS内部的路由器之间，用于传递外部路由信息）。BGP使用丰富的路径属性（如AS_PATH、LOCAL_PREF、MED、NEXT_HOP、Origin）和复杂的选路规则来决定最佳路径，管理者可以通过配置路由策略（Route Map/Routing Policy）精确控制路由的导入、导出和优选，实现流量工程和安全策略。

## 关键结论

- BGP的四种消息类型：OPEN（建立BGP会话，协商BGP版本、AS号、Hold Time和BGP Identifier）、UPDATE（通告或撤销路由，每条UPDATE消息包含：撤销路由列表 + 一组共享相同路径属性的可达路由的前缀）、KEEPALIVE（保持会话心跳，默认60秒周期，Hold Time通常180秒）、NOTIFICATION（报告错误并关闭会话）
- BGP路径属性分类：公认必遵（AS_PATH、NEXT_HOP、Origin）、公认自决（LOCAL_PREF、ATOMIC_AGGREGATE）、可选传递（Community、Aggregator）、可选非传递（MED/MULTI_EXIT_DISC、Originator_ID、Cluster_List）。不同类型属性在AS间传播的范围和规则不同
- BGP的选路规则（Cisco的13步选路顺序）：(1)最高Weight（Cisco私有）→(2)最高LOCAL_PREF→(3)本地始发路由→(4)最短AS_PATH→(5)最低Origin类型（IGP<EGP<Incomplete）→(6)最小MED→(7)eBGP优于iBGP→(8)最低IGP Cost到NEXT_HOP→...(11)最低Router-ID→(12)最小Cluster-List长度→(13)最低邻居地址
- BGP路由通告规则：从eBGP邻居学到的路由通告给所有BGP邻居（eBGP和iBGP）；从iBGP邻居学到的路由不向其他iBGP邻居通告（iBGP水平分割），只通告给eBGP邻居。这是为了防止iBGP环路——因为AS_PATH只跨越AS边界递增，在同一AS内部不变
- BGP的核心创新——策略路由：运营商通过LOCAL_PREF控制出口流量、通过MED影响入站流量、通过AS_PATH Prepend让优选路径的AS_PATH变"长"让备选路径变"短"、通过Community标签执行BGP社区策略

## 易错点

1. **iBGP全互联要求**：由于iBGP水平分割规则，AS内部所有iBGP路由器必须两两建立iBGP Peer（全互联，Full Mesh），否则某些路由器无法获得完整的外部路由信息。解决方案：路由反射器（Route Reflector，打破水平分割规则，允许部分路由器向其他iBGP邻居反射路由）或BGP联盟（Confederation，将大AS拆分为子AS）。

2. **BGP不是自动发现邻居**：与OSPF不同，BGP邻居必须手动配置（neighbor x.x.x.x remote-as NNN）。BGP不会主动发现相邻的路由器。如果配置IP地址错误，邻居会一直处于Idle/Active状态。

3. **NEXT_HOP属性的真正含义**：对于eBGP，NEXT_HOP是发送UPDATE消息的eBGP对等体的IP地址；对于iBGP，NEXT_HOP保持不变（不清零重写）——这意味着iBGP路由器收到的NEXT_HOP是外部AS边界的地址，而iBGP路由器可能不知道如何通过IGP到达该NEXT_HOP。这也是为什么需要在IGP中引入AS边界地址的路由，或使用next-hop-self命令改写NEXT_HOP。

4. **AS_PATH防止环路的机制**：当一个BGP路由器收到UPDATE消息，检查AS_PATH中是否包含自己的AS号。如果包含，说明存在环路，直接丢弃。BGP不依靠跳数或TTL防止环路。

## 例题

**例题1**：AS 100向AS 200通告了一条192.0.2.0/24的路由。AS 200经eBGP学习后通过iBGP通告给AS 200内部的路由器。然后AS 200向AS 300通过eBGP通告该路由。请写出各个阶段AS_PATH属性值。

**解答**：AS 100发往AS 200：AS_PATH = {100}（AS 100向AS 200发送更新时添加自己的AS号）。AS 200收到后在AS_PATH前添加自己的AS号，AS_PATH = {200, 100}。AS 200通过iBGP向内部路由器传递时AS_PATH不变仍为{200, 100}。iBGP不修改AS_PATH。AS 200向AS 300发送eBGP更新时在AS_PATH前加上自己的AS号：AS_PATH = {200, 200, 100}——等等，这是错误的理解！正确做法：AS 200只在发送前加一次自己的AS号，所以是{200, 200, 100}。但如果AS 200通过联盟或路由反射处理，AS_PATH的内容和结构可能不同。最常见情况：AS_PATH = 200 100（即200且遍历了100）。

**例题2**：某企业通过两条链路连接两个不同的ISP（AS 100和AS 200），如何利用BGP策略实现主备切换和负载分担？

**解答思路**：通过LOCAL_PREF控制出口方向：给从主ISP（AS 100）学到的路由设置较高的LOCAL_PREF（如200），给从备ISP学到的设置较低LOCAL_PREF（如100），则所有出站流量优选主ISP。通过MED或AS_PATH Prepend影响入站流量：向备ISP通告路由时将AS_PATH加长（Prepend自己的AS号多次，如65001 65001 65001），外部路由器会优先选择较短的AS_PATH路径进入主ISP链路。负载分担：可通过条件性设置不同前缀的LOCAL_PREF值实现选择性流量分流。

## 代码示例

```bash
# FRRouting BGP配置示例（vtysh）
# router bgp 65001
#  bgp router-id 1.1.1.1
#  neighbor 203.0.113.1 remote-as 65002       # eBGP Peer
#  neighbor 203.0.113.1 description ISP-A
#  neighbor 10.0.0.2 remote-as 65001          # iBGP Peer
#  neighbor 10.0.0.2 update-source loopback0
#  network 192.168.0.0/24
#  !
#  address-family ipv4 unicast
#   neighbor 203.0.113.1 route-map ISP-IN in
#   neighbor 203.0.113.1 route-map ISP-OUT out

# 查看BGP摘要
# show bgp summary
# show bgp ipv4 unicast
```

```python
# BGP路由数据结构简化示例
class BGPRoute:
    def __init__(self, prefix, as_path, next_hop, local_pref=100, med=0):
        self.prefix = prefix           # 路由前缀（如 '192.0.2.0/24'）
        self.as_path = as_path         # AS路径列表（如 [200, 100]）
        self.next_hop = next_hop       # 下一跳IP
        self.local_pref = local_pref   # 本地优先级（默认100）
        self.med = med                 # Multi-Exit Discriminator
        self.origin = 'IGP'            # Origin类型
    
    def as_path_length(self):
        return len(self.as_path)
    
    def has_own_as(self, my_as):
        """AS_PATH环路检测"""
        return my_as in self.as_path

# BGP水平分割规则检查
def can_advertise_to_ibgp(peer_type, received_from):
    """判断能否向iBGP邻居通告路由"""
    if peer_type == 'eBGP':
        return True  # 从eBGP学到的可以通告给所有邻居
    if peer_type == 'iBGP' and received_from == 'iBGP':
        return False  # iBGP水平分割
    return True
```

## 关联页面

[[路由协议-RIP]] [[路由协议-OSPF]] [[IP协议]]
