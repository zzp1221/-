---
title: MAC地址详解
course: 计算机网络
chapter: 数据链路层
difficulty: BASIC
tags: [MAC地址, 物理地址, ARP, 单播, 组播, 广播]
aliases: [MAC Address, Physical Address, Hardware Address, EUI-48]
source:
  - 谢希仁《计算机网络》第8版
  - IEEE 802标准
updated_at: 2026-05-02
---

## 核心定义

MAC地址（Media Access Control Address），也称硬件地址、物理地址或EUI-48，是数据链路层用于标识网络设备接口的唯一标识符，长度为48比特（6字节），通常用十六进制表示，每字节间以冒号（:）或连字符（-）分隔，如00:1A:2B:3C:4D:5E。MAC地址由IEEE负责分配管理，前24位（OUI，Organizationally Unique Identifier）分配给设备制造商，后24位由制造商自行分配以保证每块网卡的MAC地址全球唯一。MAC地址存在于网卡的ROM中（可被软件修改），是局域网内数据帧寻址的基础。根据目的MAC地址的类型，帧传输分为单播（Unicast）、组播（Multicast）和广播（Broadcast）三种方式。MAC地址仅在局域网（广播域）内有效，跨越路由器时需要ARP协议将IP地址解析为MAC地址。

## 关键结论

- MAC地址的最高字节（第1字节）最低位（b0）为I/G位（Individual/Group）：0表示单播地址，1表示组播地址。次低位（b1）为G/L位（Global/Local）：0表示全球统一管理地址（IEEE分配），1表示本地管理地址（用户可自定义）
- 广播MAC地址为FF:FF:FF:FF:FF:FF（全1），发送到广播地址的帧会被同一广播域内所有设备接收处理
- 组播MAC地址用于一对多的选择性通信：IPv4组播的MAC地址以01:00:5E开头（前25位固定为00000001 00000000 01011110 0），后23位由IPv4组播地址的低23位映射而来
- MAC地址和IP地址服务于不同层次：MAC地址用于局域网内的帧转发（数据链路层，一跳范围内的寻址），IP地址用于跨网络的端到端路由（网络层，全球寻址）。两者通过ARP协议建立映射关系
- 交换机的MAC地址学习过程：交换机接收帧时，记录源MAC地址和接收端口号的映射关系到MAC地址表（CAM表），老化时间通常为300秒。对于未知目的MAC的帧，交换机执行泛洪（Flooding）

## 易错点

1. **MAC地址和IP地址不是固定绑定的**：虽然MAC地址在网卡出厂时被固化，但在网络中，一个IP地址可以对应不同的MAC地址（如设备更换网卡后IP不变），一个MAC地址也可以对应多个IP地址（如服务器绑定多个IP别名）。ARP动态解析使得同一IP在不同时刻可以映射到不同MAC地址。

2. **MAC地址并不是真正的"全球唯一"**：虽然IEEE的OUI分配机制在理论上保证了唯一性，但实践中存在：虚拟机/容器的虚拟网卡动态生成MAC地址、高可用集群中的浮动MAC地址、人为MAC地址克隆（如某些网络运营商绑定用户MAC地址）、以及隐私保护中的随机化MAC地址（iOS/Android的MAC地址随机化功能）。

3. **交换机不会修改经过的帧的MAC地址**：二层交换机和网桥工作在数据链路层，转发帧时不修改源MAC和目的MAC地址（透明传输）。而路由器（工作在网络层）在转发IP数据包时会修改源和目的MAC地址——因为数据包进入新的网段需要新的二层封装。

4. **MAC地址也不完全等于"物理地址"**：物理层（Layer 1）没有地址概念。MAC地址虽然被称为"物理地址"，但它属于数据链路层（Layer 2）的概念。称其为"物理地址"是因为它通常被固化在硬件中，与硬件绑定。

## 例题

**例题1**：以下哪个MAC地址为合法的组播地址？（ ）
A. 00:1A:2B:3C:4D:5E
B. 01:00:5E:00:00:01
C. FF:FF:FF:FF:FF:FF
D. 02:00:00:00:00:01

**解答**：选B。判断方法：MAC地址第一个字节最低位（b0）为1表示组播。A选项第一个字节00(0000 0000)，b0=0单播。B选项01(0000 0001)，b0=1组播。C选项FF(1111 1111)，b0=1，确为广播地址，是组播的一个特例。D选项02(0000 0010)，b0=0，b1=1本地管理单播。严格来说B和C都是合法的组播/广播地址。若单选则B最合适（典型组播示例）。

**例题2**：描述同一局域网内主机A（IP: 192.168.1.10, MAC: AA:AA:AA:AA:AA:AA）向主机B（IP: 192.168.1.20, MAC: BB:BB:BB:BB:BB:BB）发送数据包时，以太网帧的MAC地址封装过程和ARP的作用。

**解答思路**：应用层数据经过传输层和网络层封装后，在数据链路层需要确定目的MAC地址。A首先检查ARP缓存中是否有IP 192.168.1.20对应的MAC地址。如果有，直接使用BB:BB:BB:BB:BB:BB作为目的MAC。如果没有，A发送ARP请求广播帧（目的MAC=FF:FF:FF:FF:FF:FF），B收到后回复ARP应答（单播），包含自己的MAC地址。A获得B的MAC后，以太网帧头部填写：目的MAC=BB:BB:BB:BB:BB:BB，源MAC=AA:AA:AA:AA:AA:AA，类型=0x0800(IPv4)。交换机根据目的MAC查找CAM表，将帧从B所连端口发出去。B收到后检查目的MAC与自身MAC匹配，继续向上层解封装。

## 代码示例

```bash
# 查看本机MAC地址
# Linux
ip link show | grep ether
ifconfig | grep ether

# Windows
ipconfig /all | findstr "物理地址"

# 查看ARP缓存
arp -a           # Windows
ip neigh show    # Linux

# 查看交换机MAC地址表（Cisco IOS示例）
# show mac address-table
```

```python
# Python获取本机MAC地址
import uuid

def get_mac_address():
    """获取本机MAC地址（十六进制格式）"""
    mac = uuid.getnode()
    mac_hex = ':'.join(f'{(mac >> (i*8)) & 0xff:02x}' for i in range(5, -1, -1))
    return mac_hex

print(f"本机MAC地址: {get_mac_address()}")

# 判断MAC地址类型
def mac_type(mac_str):
    """判断MAC地址是单播/组播/广播"""
    first_byte = int(mac_str.split(':')[0], 16)  # Python 14行有多个值需括号
    if mac_str.upper() == 'FF:FF:FF:FF:FF:FF':
        return "广播"
    return "组播" if (first_byte & 0x01) else "单播"
```

## 关联页面

[[以太网]] [[ARP]] [[CSMA-CD]] [[交换机与VLAN]] [[IPv4地址分类]]
