---
title: RIP路由协议
course: 计算机网络
chapter: 网络层
difficulty: INTERMEDIATE
tags: [RIP, 距离矢量路由, Bellman-Ford, 跳数, 路由环路, 水平分割]
aliases: [Routing Information Protocol, Distance Vector, RIPv1, RIPv2]
source:
  - 谢希仁《计算机网络》第8版
  - RFC 1058, RFC 2453
updated_at: 2026-05-02
---

## 核心定义

RIP（Routing Information Protocol，路由信息协议）是最早出现的内部网关协议（IGP）之一，基于距离矢量（Distance-Vector）路由算法（Bellman-Ford算法），使用跳数（Hop Count）作为路由度量值（Metric）。RIP的工作原理是：每个路由器每隔30秒（默认）向所有邻居发送自己的完整路由表，邻居收到后使用Bellman-Ford方程更新自己的路由表——对于每个目的网络，选择min(当前Metric, 邻居Metric+1)的路径。RIP规定最大跳数为15（16表示不可达），因此只能用于不超过15跳的小型自治系统（AS）内部网络。RIP有两个版本：RIPv1（无类编址，不支持CIDR和VLSM，使用广播更新，无认证）和RIPv2（支持CIDR/VLSM，使用224.0.0.9组播更新，支持MD5明文/密文认证）。RIP被广泛用于小型、简单的网络中，但由于其慢收敛、环路问题和15跳限制，在大规模网络中被OSPF取代。

## 关键结论

- RIP的距离矢量路由算法核心：每个路由器维护到每个目的网络的方向（下一跳）和距离（跳数）；路由器通过交换路由表获得全局网络拓扑信息；收到邻居的更新后，如果邻居到目的地的跳数加1小于自己当前的跳数，则更新路由表中的该条目，并将下一跳设为该邻居
- RIP解决路由环路问题的五大机制：（1）最大跳数16——不可达基准线防止无限计数；（2）水平分割（Split Horizon）——从一个接口学到的路由不再从这个接口发送回去；（3）毒性反转（Poison Reverse）——在更优路由消失时立即将跳数设为16通知邻居；（4）触发更新（Triggered Update）——路由变化时立即发送更新而不等待30秒周期；（5）抑制计时器（Hold-down Timer）——路由失效后等待一段时间再接受新路由，防止错误信息蔓延
- RIP路由表老化：每条路由有一个180秒的老化计时器，如果在180秒内收到包含该路由的更新，计时器重置；如果超时则标记为16（不可达）并从路由表中删除（通常再等待120秒彻底清除）
- RIPv1与RIPv2的主要区别：RIPv1是有类协议（不携带子网掩码），RIPv2是无类协议（携带子网掩码）；RIPv1使用255.255.255.255广播更新，RIPv2使用224.0.0.9组播更新；RIPv2支持路由标记和认证

## 易错点

1. **16跳不可达的含义不等于15跳就到了**：RIP中度量值是0-16。直连网络的度量值为0（有些实现从1开始），最多经过15个路由器（跳数15），共16跳不可达。配置RIP前需先确认网络直径不超过15跳。

2. **30秒的更新周期和定时器的漂移**：RIP实际使用25-35秒的随机化间隔（路由更新定时器有±5秒的随机抖动），目的是避免多个路由器的更新定时器同步导致的瞬时全网广播风暴。

3. **慢收敛问题**：当链路断掉后，好消息传播快但坏消息传播慢。网络中的错误路由信息可能需要数分钟才能被所有路由器清除。典型的"计数到无穷"问题在没有水平分割和毒性反转的情况下尤其严重。

4. **RIP只能基于跳数，不能基于链路带宽**：这意味着RIP会选择跳数少但带宽低的路径（如选择2跳64kbps链路而非3跳1Gbps链路）。对于需要按带宽选路的网络，OSPF显然更合适。

## 例题

**例题1**：网络中有三个路由器R1、R2、R3呈链状连接，R1连接网络N1，R1-R2链路、R2连接网络N2，R2-R3链路、R3连接网络N3。RIP收敛后，写出R3关于N1的路由表项以及该距离信息的传播路径。

**解答**：R3关于N1的路由：目的=N1，下一跳=R2，跳数=2。传播路径：R1直接连接N1（metric=0/1，取决于实现），R1向R2发送更新时告知N1的metric=1。R2收到后加上自身到R1的1跳，写入路由表N1 metric=2 next-hop=R1。R2向R3发送更新告知N1 metric=2。R3收到后加1跳，写入路由表N1 metric=3 next-hop=R2（跳数3或2也取决于实现）。

**例题2**：解释RIP中水平分割和毒性反转的区别，以及在什么情况下毒性反转优于水平分割。

**解答思路**：水平分割是从接口X学到的路由不再从接口X通告出去，防止将路由信息"回灌"给原来的发送者。毒性反转更为激进：从接口X学到的路由会从接口X通告回去，但使用时将跳数设为16（不可达），主动告诉对方"这条路从我这里不通"。毒性反转在以下情况优于水平分割：当网络中有环路拓扑（非树形）时，单纯的抑制信息传播可能不够快，毒性反转能够更主动地传播坏消息。但毒性反转增加了更新报文的尺寸。

## 代码示例

```bash
# Cisco路由器RIP配置示例
# router rip
#  version 2
#  no auto-summary     # RIPv2通常关闭自动汇总
#  network 192.168.1.0
#  network 10.0.0.0

# Linux使用Quagga/FRRouting配置RIP
# (在vtysh中)
# configure terminal
# router rip
#  network 192.168.1.0/24
#  network eth0
```

```python
# RIP距离矢量路由算法简化实现
class RIPRouter:
    def __init__(self, router_id):
        self.router_id = router_id
        # 路由表: {destination: (next_hop, metric)}
        self.routing_table = {}
        self.neighbors = {}  # {neighbor_id: cost}
    
    def receive_update(self, neighbor, neighbor_table):
        """收到邻居路由表更新，执行Bellman-Ford更新"""
        changed = False
        for dest, (_, neighbor_metric) in neighbor_table.items():
            # 水平分割检查：如果邻居说去dest要从我这里走则忽略
            new_metric = neighbor_metric + self.neighbors[neighbor]
            if new_metric > 16:
                continue  # 超过最大跳数
            
            if dest not in self.routing_table:
                self.routing_table[dest] = (neighbor, new_metric)
                changed = True
            elif new_metric < self.routing_table[dest][1]:
                self.routing_table[dest] = (neighbor, new_metric)
                changed = True
            elif (self.routing_table[dest][0] == neighbor and 
                  new_metric != self.routing_table[dest][1]):
                # 同一下一跳的路由更新
                self.routing_table[dest] = (neighbor, new_metric)
                changed = True
        return changed  # 返回是否有变化，触发可能的触发更新
```

## 关联页面

[[路由协议-OSPF]] [[路由协议-BGP]] [[子网划分-CIDR]]
