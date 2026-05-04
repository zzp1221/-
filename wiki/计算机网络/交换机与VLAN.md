---
title: 交换机与VLAN
course: 计算机网络
chapter: 数据链路层
difficulty: INTERMEDIATE
tags: [交换机, VLAN, 虚拟局域网, 广播域, trunk, IEEE 802.1Q, VLAN间路由]
aliases: [Switch, VLAN, IEEE 802.1Q, Trunk, Inter-VLAN Routing]
source:
  - 谢希仁《计算机网络》第8版
  - IEEE 802.1Q
updated_at: 2026-05-02

---

## 核心定义

交换机（Switch，二层交换设备）是工作在数据链路层的网络设备，通过MAC地址学习实现数据帧的精准转发，是组建局域网的必备基础设施。VLAN（Virtual Local Area Network，虚拟局域网）是将一个物理局域网按照逻辑划分为多个隔离的广播域的技术，同一VLAN内的设备可以像在同一个物理交换机上一样直接通信，不同VLAN之间的设备必须通过路由器（或三层交换机）进行通信。VLAN基于IEEE 802.1Q标准实现——在标准以太网帧的源MAC地址之后插入4字节的VLAN标签（Tag），包含2字节的标签协议标识符（TPID，0x8100）和2字节的标签控制信息（TCI，包含3位优先级PCP、1位丢弃标识DEI/CFI和12位VLAN ID）。VLAN解决了传统二层交换网络中广播域过大导致的广播风暴和安全隔离问题，在企业网络中被广泛部署。VLAN间通信通过三层交换机或路由器的单臂路由（Router-on-a-Stick）实现。

## 关键结论

- 交换机工作原理——自学习MAC地址表：收到帧后提取源MAC和接收端口建立MAC地址表项（MAC Address Table/CAM Table），老化时间约300秒。转发策略：如果目的MAC在MAC表中有记录→从相应端口转发（过滤/Forwarding）；如果目的MAC不在表中→向同VLAN的所有其他端口泛洪（Flooding）；如果是广播/组播→泛洪
- VLAN隔离广播域的原理和优点：传统交换机下所有端口在同一个广播域，ARP请求、DHCP Discover等广播包到达所有端口，大量无意义广播消耗网络和端系统资源。VLAN将交换机的端口分配到不同的逻辑域，广播/泛洪仅限于本VLAN成员之间，VLAN内部宿主无法被不同VLAN的设备访问
- 802.1Q Trunk端口与Access端口：Access端口属于单一VLAN，收发的是不带Tag的普通以太网帧（交换机内部用端口默认VLAN ID标识）；Trunk端口用于交换机之间或交换机到路由器的级联，承载多个VLAN的流量，帧在Trunk链路上带有802.1Q Tag（除Native VLAN的帧外）。Native VLAN是Trunk端口上的默认VLAN——该VLAN的帧不携带Tag传输
- VLAN间路由：不同VLAN的设备必须通过网络层（路由器/三层交换机）通信。实现方式：(a)单臂路由——路由器的一个物理接口配逻辑子接口（每个VLAN一个子接口，子接口终结802.1Q Tag）；(b)三层交换机（多层交换机）的SVI（Switch Virtual Interface）——为每个VLAN创建逻辑三层接口作为该VLAN的网关
- VTP（VLAN中继协议，Cisco私有）和MSTP：VTP用于在交换网络中自动同步VLAN配置（现在少用因容易导致安全漏洞——任何交换机默认加入VTP域可能清除所有VLAN配置）。STP（生成树协议）工作在VLAN之上——为每个VLAN单独计算一棵生成树（PVST+）或为多个VLAN共享一棵生成树（MSTP）

## 易错点

1. **VLAN ID范围限制**：802.1Q的VLAN ID为12位，理论0-4095。VLAN 0和4095保留不可使用，VLAN 1是所有端口的出厂默认VLAN（本征VLAN/管理VLAN），实际可用VLAN ID为2-4094。许多中小型交换机只支持256个VLAN同时激活。

2. **Native VLAN不标记的误解**：本征VLAN的帧在Trunk链路上不携带802.1Q Tag。如果Trunk两端的Native VLAN配置不匹配（一端Native VLAN 1而另一端Native VLAN 2），VLAN 1的帧未标记到达另一端后会被错误地归入VLAN 2，造成VLAN泄露。这是常见的网络配置错误。

3. **VLAN和子网不是一对一强制对应的**：最佳实践建议一个VLAN对应一个IP子网，这样路由和ACL配置更清晰。但从协议角度，多个子网在同一个VLAN内可以共存（但不推荐——会导致不必要的广播和ARP响应混乱），一个子网跨越多个VLAN通常不可行（除非使用了特殊的代理/二层隧道）。

4. **三层交换机的"路由"和路由器的"交换"**：三层交换机内部有硬件路由芯片（ASIC），VLAN间的数据包在硬件层面上执行路由查找后转发（线速转发）。路由器的转发倾向于CPU处理或更复杂的路由策略。现代网络的VLAN间转发首选三层交换机，外网或VPN流量由路由器/防火墙专门处理。

## 例题

**例题1**：某企业网络架构为：核心层三层交换机连接4台接入层二层交换机，全网部署了VLAN 10（财务部）和VLAN 20（市场部）。同VLAN在不同接入交换机上的主机如何通信？假设二层交换机只做VLAN接入和Trunk，三层交换机处理VLAN间路由。

**解答**：同VLAN主机通信：VLAN 10的主机A在接入交换机SW1上，主机B在SW2上。A发出的帧（无Tag）通过SW1的Access端口进入，SW1在帧上添加VLAN 10 Tag后通过上行Trunk端口转发到核心交换机。核心交换机查MAC表发现目的MAC对应SW2的某个Trunk端口，将带Tag的帧转发到SW2。SW2去掉Tag后送到主机B的Access端口。全程VLAN信息通过Tag保留，保证VLAN 10的广播域逻辑一致。不同VLAN通信：财务部VLAN 10的主机请求市场部VLAN 20的主机——数据包到达核心交换机的VLAN 10 SVI接口（如IP 192.168.10.1），核心交换机执行三层查表，发现目的IP属于VLAN 20子网（如192.168.20.0/24），通过VLAN 20 SVI接口（IP 192.168.20.1）转发。硬件上数据包在核心交换机内部经历了"解封装→L3查表→重新封装"的路由过程。

**例题2**：静态VLAN和动态VLAN的区别及各自适用场景。

**解答思路**：静态VLAN——管理员手动将交换机的每个端口分配到特定VLAN，配置简单，适用于终端位置固定、变动不频繁的企业网络（常规办公室）。动态VLAN——基于MAC地址（VMPS）、协议类型或用户身份（802.1X认证+Radius服务器分配的动态VLAN）将设备动态加入对应的VLAN。适用场景：移动办公（员工在各VLAN之间移动而自动分配正确的VLAN）、访客网络（根据802.1X认证结果将访客设备隔离到Guest VLAN）、基于设备类型的动态访问控制。动态VLAN需要VLAN策略服务器。

## 代码示例

```bash
# Cisco交换机VLAN配置示例
# 创建VLAN
# vlan 10
#  name Finance
# vlan 20
#  name Marketing

# 分配Access端口
# interface g0/1
#  switchport mode access
#  switchport access vlan 10

# 配置Trunk端口
# interface g0/24
#  switchport mode trunk
#  switchport trunk native vlan 1
#  switchport trunk allowed vlan 10,20

# 三层交换机SVI配置
# interface vlan 10
#  ip address 192.168.10.1 255.255.255.0
# interface vlan 20
#  ip address 192.168.20.1 255.255.255.0
# ip routing  # 启用三层路由
```

```bash
# Linux基于VLAN的接口配置
ip link add link eth0 name eth0.10 type vlan id 10
ip addr add 192.168.10.1/24 dev eth0.10
ip link set eth0.10 up
```

## 关联页面

[[以太网]] [[MAC地址]] [[CSMA-CD]] [[子网划分-CIDR]]
