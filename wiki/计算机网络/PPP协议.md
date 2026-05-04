---
title: PPP点对点协议
course: 计算机网络
chapter: 数据链路层
difficulty: INTERMEDIATE
tags: [PPP, 点对点协议, HDLC, LCP, NCP, 拨号上网, 身份认证]
aliases: [Point-to-Point Protocol, LCP, NCP, PAP, CHAP]
source:
  - 谢希仁《计算机网络》第8版
  - RFC 1661, RFC 1662
updated_at: 2026-05-02
---

## 核心定义

PPP（Point-to-Point Protocol，点对点协议）是互联网工程任务组（IETF）制定的数据链路层协议，用于在点对点链路上传输多协议数据报。PPP是目前使用最广泛的数据链路层协议，取代了早期的SLIP协议，成为拨号上网、PPPoE（以太网上的PPP）、广域网专线等场景的标准协议。PPP协议由三部分组成：（1）封装协议——使用HDLC类帧格式封装多种网络层协议的数据报；（2）链路控制协议LCP（Link Control Protocol）——用于建立、配置、测试和终止数据链路连接，协商选项包括最大接收单元（MRU）、认证协议类型、链路质量监测等；（3）网络控制协议NCP（Network Control Protocol）——为每种网络层协议提供独立的配置和管理。PPP不提供纠错和流量控制功能（这些留给上层协议处理），仅提供差错检测（CRC）。

## 关键结论

- PPP的帧格式采用HDLC类格式：标志(1B, 0x7E) + 地址(1B, 0xFF) + 控制(1B, 0x03) + 协议(1-2B) + 信息(可变, 默认≤1500B) + CRC(2-4B) + 标志(1B, 0x7E)。其中地址和控制字段为固定值，NCP协商时使用压缩可缩减为0字节
- LCP链路建立的三阶段：链路静止（Dead）→链路建立（Establish，LCP协商）→认证（Authenticate，可选）→网络层协议（Network，NCP协商）→链路打开（Open）。链路终止时反向执行
- PPP支持的两种认证协议：PAP（口令认证协议，两次握手，明文传输密码，安全性弱）和CHAP（挑战-握手认证协议，三次握手，使用MD5散列，密码不在网络上传输，安全性强）
- PPP的透明传输：同步链路使用零比特填充（比特填充法），异步链路使用字符填充（字节填充法，转义字符0x7D），确保任何比特组合都可以透明传输
- PPPoE（PPP over Ethernet）将PPP帧封装在以太网帧中，使PPP的用户认证和管理功能能在以太网接入环境中使用，广泛用于ADSL宽带拨号和光纤到户

## 易错点

1. **PPP不是全功能的链路层协议**：PPP不实现流量控制和纠错重传（它只检错不纠错），PPP的设计理念是"简约"——只做必要的事情，将可靠性留给上层协议（如TCP）。不能像分析HDLC的滑动窗口那样去套用PPP。

2. **PPP地址字段始终为0xFF**：HDLC中有地址字段用于区分主从站，但PPP是点对点链路上运行的，只有两个端点，地址字段固定为0xFF（广播地址），并无实际意义。LCP可以协商将地址和控制字段一起压缩掉。

3. **PPP认证发生在网络层阶段之前**：LCP建立链路→可选认证→NCP协商网络层参数，这个顺序是有意设计的：必须在允许用户访问网络层资源之前完成身份认证。PAP即使认证失败也会通知，CHAP可以周期性地在通信过程中重复认证。

4. **PPP可以承载多种网络层协议**：通过NCP为每种网络层协议（IPv4的IPCP、IPv6的IPv6CP、MPLS等）分别进行配置。协议字段标识了封装的数据类型（0x0021=IPv4, 0x0057=IPv6, 0x8021=IPCP, 0xC021=LCP）。初学者常以为PPP只能用于IP。

## 例题

**例题1**：描述PPP协议从Dead状态到网络层数据传输的完整状态转换过程。

**解答**：起点Dead状态：物理层未就绪（无载波）。当检测到载波或其他事件触发后，进入Establish状态：LCP通过Configure-Request/Ack/Nak/Reject报文协商链路参数（如MRU、认证协议等），协商成功后进入Authenticate状态（如果协商了认证协议）；认证（PAP或CHAP）成功后进入Network状态：各NCP（如IPCP）协商网络层参数（如IP地址分配），协商成功进入Open状态：可以传输网络层数据。断开过程反向执行：先终止NCP，再终止LCP，回到Dead状态。

**例题2**：比较PPP的异步传输（字符填充）和同步传输（比特填充）的透明传输实现差异，说明在什么场景下使用哪种方式。

**解答思路**：异步传输（8位数据+起始位+停止位）以字符为传输单位，使用字符填充法：将0x7E（帧标志）替换为0x7D 0x5E，将0x7D（转义字符）替换为0x7D 0x5D，数据中ASCII控制字符（小于0x20的）也可以替换。同步传输以比特为传输单位，使用零比特填充法：发送方每遇到5个连续的1就插入一个0。场景选择：异步传输适用于模拟Modem拨号（PSTN/ISDN）、计算机串口等低速或字符导向的链路；同步传输适用于SDH/SONET、DDN专线等高速数字链路。

## 代码示例

```bash
# Linux中建立PPPoE连接
pppoe-setup              # 配置PPPoE
pppoe-start / pppoe-stop # 启动/停止PPP连接
pppoe-status             # 查看PPP连接状态

# 查看PPP接口
ifconfig ppp0
ip addr show ppp0
```

```python
# PPP帧结构示意（简化版）
class PPPFrame:
    FLAG = b'\x7e'
    ESC = b'\x7d'
    ADDRESS = b'\xff'
    CONTROL = b'\x03'
    
    @staticmethod
    def byte_stuffing(data):
        """PPP异步传输的字节填充"""
        result = bytearray()
        for b in data:
            if b == 0x7e:
                result.extend(b'\x7d\x5e')
            elif b == 0x7d:
                result.extend(b'\x7d\x5d')
            elif b < 0x20:  # ASCII控制字符
                result.extend(bytes([0x7d, b ^ 0x20]))
            else:
                result.append(b)
        return bytes(result)
    
    @staticmethod
    def create_frame(protocol, data):
        """构造PPP帧"""
        payload = PPPFrame.byte_stuffing(data)
        return PPPFrame.FLAG + PPPFrame.ADDRESS + PPPFrame.CONTROL + \
               protocol + payload + b'\x00\x00' + PPPFrame.FLAG  # CRC简化
```

## 关联页面

[[数据链路层-成帧]] [[数据链路层-差错控制-CRC]] [[以太网]] [[IP协议]]
