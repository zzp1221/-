---
title: OSPF路由协议
course: 计算机网络
chapter: 网络层
difficulty: ADVANCED
tags: [OSPF, 链路状态路由, Dijkstra, 区域, LSA, DR, BDR]
aliases: [Open Shortest Path First, Link State Routing, SPF, OSPF Area]
source:
  - 谢希仁《计算机网络》第8版
  - RFC 2328 (OSPFv2), RFC 5340 (OSPFv3)
updated_at: 2026-05-02
---

## 核心定义

OSPF（Open Shortest Path First，开放最短路径优先）是基于链路状态（Link State）算法的内部网关协议（IGP），使用Dijkstra最短路径优先（SPF）算法计算到达每个目的网络的最优路径。与RIP的距离矢量方法不同，OSPF中每个路由器不交换完整的路由表，而是通过泛洪（Flooding）LSA（链路状态通告）来构建和同步链路状态数据库（LSDB），每个路由器维护着全网拓扑的完整地图（同一区域内），然后独立运行SPF算法计算出以自己为根的最短路径树，据此生成路由表。OSPF支持分层网络设计，将大型自治系统划分为多个区域（Area），主干区域（Backbone Area 0）负责区域间流量转发，非主干区域必须与Area 0直接相连。OSPF使用Cost（代价，与链路带宽成反比）作为度量值，支持等价多路径负载均衡（ECMP），并具有快速收敛、支持VLSM/CIDR和路由认证等优点，是目前大型企业网络和运营商网络中最广泛使用的IGP。

## 关键结论

- OSPF的5种消息类型：Hello（建立和维护邻居关系，10秒/30秒周期）、数据库描述DBD/DDP（摘要交换，协商主从关系）、链路状态请求LSR（请求特定LSA的完整内容）、链路状态更新LSU（携带完整LSA）、链路状态确认LSAck（可靠洪泛的确认机制）
- OSPF邻居状态机（8个状态）：Down→Init→2-Way→ExStart→Exchange→Loading→Full。2-Way之前完成Hello交换，ExStart/Exchange/Loading三个阶段完成LSDB同步
- DR和BDR的选择：在广播多路访问网络（如以太网）上，OSPF选择指定路由器（DR）和备份指定路由器（BDR）以减少LSA洪泛量（所有路由器只与DR/BDR建立邻接，而非全互联）。DR/BDR通过Hello报文的优先级（0-255，默认1）和Router-ID决定，优先级为0的路由器不参与DR/BDR选举
- OSPF的7种LSA类型：Type 1 路由器LSA（区域内）、Type 2 网络LSA（DR产生）、Type 3 网络汇总LSA（ABR产生，区域间）、Type 4 ASBR汇总LSA、Type 5 自治系统外部LSA（ASBR产生）、Type 7 NSSA外部LSA。不同区域类型（Stub、Totally Stubby、NSSA）对不同类型的LSA传播有不同的策略限制
- OSPF区域类型：标准区域（所有LSA）、Stub区域（过滤Type 5 LSA，用默认路由替代）、Totally Stubby区域（连Type 3也过滤）、NSSA（允许有限的外部路由，通过Type 7 LSA导入后ABR转换为Type 5）、Totally NSSA

## 易错点

1. **DR/BDR选举不是抢占式的**：DR/BDR一旦选举确定，即使出现更高优先级的新路由器加入也不会触发重新选举，除非当前DR/BDR失效（超过40秒没有Hello）。这与很多人的直觉相反。

2. **Hello报文中的参数必须匹配才能建立邻居**：Hello/Dead间隔、区域ID、认证类型和密码、Stub标志这四项必须匹配。接口IP地址的子网掩码在广播网络中也需要匹配。很多OSPF邻居建立失败的根源就在这四个参数中。

3. **Cost的计算公式**：OSPF Cost = 参考带宽 / 接口带宽，默认参考带宽为100Mbps（Cisco）。对于千兆以太网，Cost = 100M/1000M = 1，再高速的万兆就成0.1了。为避免Cost值趋近于0导致无法区分，通常需要手动调整参考带宽（auto-cost reference-bandwidth 10000即按10Gbps为基准）。

4. **链路状态算法不是"网状洪泛"**：虽然所有路由器都要向Area内洪泛LSA，但OSPF使用可靠的洪泛机制（每个LSA需要LSAck确认），并通过序列号、老化时间和校验和避免LSA的重复传播和无序循环。这不是简单的泛洪广播。

## 例题

**例题1**：简述OSPF从路由器启动到路由表收敛的完整过程。

**解答**：（1）接口启用OSPF后发送Hello报文（224.0.0.5组播）；（2）收到邻居的Hello，检查参数匹配，建立2-Way双边邻居；（3）在广播网上选举DR和BDR；（4）ExStart：邻居间协商主从关系，由Router-ID大的作为主方；（5）Exchange：交换DBD报文同步LSDB摘要信息，每个LSA用头部标识；（6）Loading：向邻居请求自己缺少或不新的LSA（LSR/LSU/LAck）；（7）Full：LSDB完全同步；（8）以自身为根节点运行Dijkstra SPF算法计算最短路径树，生成路由表。整网所有路由器LSDB同步后达到收敛状态。

**例题2**：某大型企业有三个分布在不同城市的分支机构，各有一个OSPF区域，通过运营商MPLS VPN互联。总部的路由器作为Area 0，各分支为Area 1、Area 2、Area 3。请设计区域划分方案并说明ABR（区域边界路由器）的路由聚合策略。

**解答思路**：Area 0设在总部，各分支区域通过ABR与Area 0相连。分支Area 1、2、3作为标准区域或Stub区域。通常分支如果是叶子节点应设置为Stub/Totally Stub区域以减少LSA洪泛和路由表规模。ABR上配置Type 3 LSA的路由聚合（area range命令）——将分支网段汇总后通告到Area 0，如分支1的10.1.0.0/16汇总为一个/16而非众多/24。汇总能减少LSA数量，加速收敛和改进稳定性。注意聚合不应过于宽泛（不要超出实际分配范围），以免产生路由黑洞。

## 代码示例

```bash
# Cisco IOS OSPF配置示例
# router ospf 1
#  router-id 1.1.1.1
#  network 192.168.1.0 0.0.0.255 area 0
#  network 10.0.0.0 0.0.0.3 area 1
#  area 1 stub
#  area 0 range 192.168.0.0 255.255.0.0  # Type3汇总

# Linux FRRouting OSPF配置
# (vtysh)
# router ospf
#  ospf router-id 1.1.1.1
#  network 192.168.1.0/24 area 0
```

```python
import heapq

def dijkstra(graph, source):
    """OSPF的SPF算法核心：Dijkstra最短路径"""
    dist = {node: float('inf') for node in graph}
    dist[source] = 0
    prev = {node: None for node in graph}
    pq = [(0, source)]
    visited = set()
    
    while pq:
        d, u = heapq.heappop(pq)
        if u in visited:
            continue
        visited.add(u)
        for v, cost in graph[u].items():
            if dist[v] > d + cost:
                dist[v] = d + cost
                prev[v] = u
                heapq.heappush(pq, (dist[v], v))
    
    return dist, prev

# 示例拓扑：{路由器: {邻居: cost}}
graph = {
    'R1': {'R2': 10, 'R3': 20},
    'R2': {'R1': 10, 'R3': 5, 'R4': 15},
    'R3': {'R1': 20, 'R2': 5, 'R4': 8},
    'R4': {'R2': 15, 'R3': 8}
}
dist, prev = dijkstra(graph, 'R1')
print(f"R1到各节点的最短距离: {dist}")
print(f"最短路径树前驱: {prev}")
```

## 关联页面

[[路由协议-RIP]] [[路由协议-BGP]] [[IP协议]] [[子网划分-CIDR]]
