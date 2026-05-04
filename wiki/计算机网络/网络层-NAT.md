---
title: NAT网络地址转换
course: 计算机网络
chapter: 网络层
difficulty: INTERMEDIATE
tags: [NAT, NAPT, 地址转换, 私有地址, 端口映射, IP伪装]
aliases: [Network Address Translation, NAPT, PAT, IP Masquerade, NAT Traversal]
source:
  - 谢希仁《计算机网络》第8版
  - RFC 2663, RFC 3022
updated_at: 2026-05-02
---

## 核心定义

NAT（Network Address Translation，网络地址转换）是将私有IP地址（内网地址）转换为公有IP地址（外网地址）的技术，使使用私有地址的内部网络中的多个主机能够共享有限的公有IP地址访问互联网。NAT的核心机制是在NAT路由器上维护一张NAT转换表（NAT Translation Table），记录内网IP:端口与外网IP:端口的映射关系。当内网主机向外发送数据包时，NAT路由器将数据包的源IP地址（私有地址）替换为公网出口IP地址，并在转换表中记录该映射；当外部回包到达时，NAT路由器查找转换表将目的IP地址（公网地址）转换回原来的私有地址并转发给内网主机。NAT根据转换粒度的不同分为：静态NAT（一对一永久映射）、动态NAT（一对多地址池动态分配）和NAPT/PAT（网络地址端口转换，通过端口号区分不同内网主机，多对一，最常见）。

## 关键结论

- NAPT（Network Address and Port Translation，也称PAT/IP伪装）是最广泛使用的NAT形式：它将多个内网IP+端口的组合映射到一个公网IP的不同端口上，理论上一个公网IP可以支持约65535个端口（扣除已用端口），实际支持数万并发连接
- NAT转换表的条目类型：静态NAT条目（手动配置，永久有效）、动态NAT转换条目（有超时时间，TCP通常24小时、UDP通常5分钟、ICMP通常60秒）
- NAT穿透（NAT Traversal）是P2P应用面临的主要挑战：由于NAT对外的映射关系无法被外部主机预先知晓，外部主机无法主动向NAT内的主机发起连接。NAT穿透技术包括STUN（获取映射后的公网IP:端口）、TURN（中继转发）、ICE（组合方案）、UPnP（自动端口映射）和ALG（应用层网关，解析特定协议并动态开放端口）
- NAT的优缺点：优点——缓解IPv4地址耗尽、隐藏内部网络拓扑（安全性）、网络合并无需重新编号；缺点——破坏了端到端原则、不支持IPsec加密载荷穿透、某些应用协议（H.323、SIP、FTP）需要ALG支持
- NAT不仅仅是"伪装IP"，NAT路由器还需要修改IP首部校验和、TCP伪首部校验和（因为IP地址变了），以及部分应用层协议载荷中的嵌入IP地址（如FTP的PORT命令）

## 易错点

1. **NAT不是防火墙**：NAT虽然隐藏了内网地址，但不等于具备了防火墙功能。NAT默认允许所有内网向外发起的连接及其响应回包，但不阻止恶意软件从内部向外发起连接。真正的防火墙需要对外部和内部流量都进行策略控制。

2. **NAPT的65535端口上限误解**：理论最大端口数65535，但实际受限于NAT设备的内存和CPU，家用路由器通常只能处理1000-4000个并发连接（受限于连接跟踪表的大小），企业级NAT设备可以支持数十万到数百万并发连接。端口限制不等于连接数限制。

3. **NAT转换表条目不是永久的**：NAT表中的每个条目都有老化时间。如果一条连接长时间没有数据包流动，超时后NAT表项会被删除，之后到达的数据包无法被正确转发（外部回包找不到对应的内网主机）。这就是为什么NAT后面的服务器需要定时发送keep-alive数据包维持NAT表项。

4. **NAT对内网的"保护"是一种副作用**：NAT的安全性是一种"模糊安全"（Security through Obscurity），并非设计目标。攻击者仍然可以通过NAT穿透技术、恶意软件反弹连接等方式攻破NAT。不应将NAT作为唯一的安全防护手段。

## 例题

**例题1**：内网主机192.168.1.10:4567通过NAT路由器（公网IP 203.0.113.5）访问外部服务器10.10.10.10:80。请画出NAT转换前后的IP数据包和NAT转换表项的变化。

**解答**：转换前（内网→NAT）：源IP=192.168.1.10:4567，目的IP=10.10.10.10:80。NAT表新增条目：内网192.168.1.10:4567 ↔ 公网203.0.113.5:5001（随机分配端口）。转换后（NAT→外网）：源IP=203.0.113.5:5001，目的IP=10.10.10.10:80。回包（外部服务器→NAT）：源IP=10.10.10.10:80，目的IP=203.0.113.5:5001。NAT查表匹配到条目，逆向转换。最终回包（NAT→内网）：源IP=10.10.10.10:80，目的IP=192.168.1.10:4567。

**例题2**：讨论在NAT环境中部署VoIP（SIP协议）面临的问题以及常用的解决方案。

**解答思路**：SIP协议的问题在于：SIP信令报文中嵌入了IP地址信息（如SDP中的c=行），这些私有IP地址（如192.168.1.10）在穿越NAT后对公网不可达。解决方案：（1）SIP ALG——NAT设备解析SIP报文内容，自动修改嵌入的IP地址并建立临时端口映射；（2）STUN——SIP客户端向STUN服务器查询自己在NAT上的公网映射地址，然后使用公网地址填充SDP；（3）TURN——当STUN不成功时（对称NAT），使用TURN服务器进行数据中继；（4）SIP Proxy + RTP Proxy——在NAT边界部署专用代理服务器处理信令和媒体流的中转。

## 代码示例

```bash
# Linux查看NAT转换表（conntrack表）
conntrack -L                    # 查看所有连接跟踪条目
conntrack -L -p tcp             # 仅查看TCP连接
conntrack -D -s 192.168.1.10    # 删除某内网主机的所有连接跟踪

# iptables配置SNAT/Masquerade
iptables -t nat -A POSTROUTING -s 192.168.1.0/24 -o eth0 -j MASQUERADE
iptables -t nat -A POSTROUTING -s 192.168.1.0/24 -o eth0 -j SNAT --to-source 203.0.113.5

# 配置端口映射/端口转发（DNAT）
iptables -t nat -A PREROUTING -i eth0 -p tcp --dport 80 -j DNAT --to-destination 192.168.1.10:8080

# 查看NAT规则
iptables -t nat -L -n -v
```

```python
# Python使用netfilter/conntrack查看NAT连接（需要python3-conntrack库）
# 以下为概念演示
nat_table = {
    # "内网IP:端口" -> ("公网IP:端口", 协议, 状态, 超时时间)
    "192.168.1.10:4567": ("203.0.113.5:5001", "TCP", "ESTABLISHED", 86400),
}

def nat_translate_inbound(packet):
    """NAT入站转换：外网回包转内网"""
    key = f"{packet['dst_ip']}:{packet['dst_port']}"
    if key in nat_table:
        entry = nat_table[key]
        packet['dst_ip'], _ = entry[0].split(':')
        return packet
    return None  # 无匹配的NAT表项
```

## 关联页面

[[IPv4地址分类]] [[子网划分-CIDR]] [[IPv6]] [[网络安全-防火墙]]
