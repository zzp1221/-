---
title: DNS域名系统
course: 计算机网络
chapter: 应用层
difficulty: INTERMEDIATE
tags: [DNS, 域名解析, 域名服务器, 递归查询, 迭代查询, DNS缓存]
aliases: [Domain Name System, DNS Resolution, Recursive Query, Iterative Query]
source:
  - 谢希仁《计算机网络》第8版
  - RFC 1034, RFC 1035
updated_at: 2026-05-02

---

## 核心定义

DNS（Domain Name System，域名系统）是互联网的核心应用层基础设施服务，它提供的主要功能是将人类友好的域名（如www.example.com）解析为机器可路由的IP地址（如93.184.216.34），以及反向解析。DNS是一个层次化的、分布式的命名系统：域名空间按照树状结构组织（根域→顶级域→二级域→子域），全球的DNS服务器各司其职地管理着自己所在区的权威数据并协同完成全球域名的解析。DNS使用UDP 53端口进行查询（减少开销和时延），对于超过512字节的响应或区域传输（Zone Transfer）场景则切换到TCP 53端口。一次完整的DNS解析可能涉及递归查询（由本地DNS服务器代表客户端完成全链查询）和迭代查询（本地DNS服务器依次访问根服务器、顶级域服务器、权威服务器获取结果）。DNS还支持多种记录类型（A/AAAA/CNAME/MX/NS/PTR/TXT/SOA等），实现了邮件路由、负载均衡、域名别名、反向解析和域验证等高级功能。

## 关键结论

- DNS的层次化域名空间：根域为"."（由全球13组根服务器管理）；顶级域TLD分为通用顶级域（.com/.net/.org等）和国家代码顶级域（.cn/.uk/.jp等，共约250个）；二级和更深层级域名由各组织向注册局购买。完整域名如www.example.com.中最后的"点"表示根域，通常省略
- DNS解析的两种查询方式：递归查询——客户端要求本地DNS服务器代表自己完成全链查询并返回最终结果，本地DNS"递归"地承担责任；迭代查询——本地DNS服务器向多个权威DNS服务器依次请求，每次获得"去问谁"的指引后继续查询。通常客户端→本地DNS用递归，本地DNS→外部服务器用迭代
- DNS常见记录类型：A记录（域名→IPv4）、AAAA记录（域名→IPv6）、CNAME记录（别名→规范域名，如www→example.com）、MX记录（邮件交换服务器及其优先级）、NS记录（域名的权威DNS服务器）、PTR记录（IP→域名，反向解析）、TXT记录（文本信息，SPF/DKIM/DMARC等邮件验证用）、SOA记录（权威域的起始管理信息）
- DNS的缓存机制：本地DNS服务器和操作系统都缓存DNS解析结果，TTL（Time To Live）由权威DNS服务器设定（通常300-86400秒）。缓存极大地减少了DNS查询的时延和根/顶级域名服务器的负担，但也带来了DNS记录变更后传播延迟的问题（最多需要等所有中间缓存过期）
- DNS的负载均衡应用：通过给同一域名配置多个A记录（轮询返回不同IP）或使用智能DNS（GeoDNS按客户端地理位置返回最近的服务器IP），在应用层实现简单但有效的负载均衡

## 易错点

1. **递归查询不等于代理**：递归查询要求DNS服务器一定返回最终IP或报错（域名不存在）。如果服务器选择迭代查询（说"我不负责，问别人"），则不是递归。客户端一般配置两个DNS服务器地址（主用和备用），两个DNS服务器都对客户端执行递归查询服务。

2. **根域名服务器不是13台计算机**：互联网的根域名服务器标识为a.root-servers.net到m.root-servers.net，共13个标识。但由于Anycast（任播）技术的应用，这13个名字的实际部署是由全球数百台服务器组成的集群，具有极高的可用性和抗攻击能力。

3. **DNS劫持与DNS污染**：DNS劫持是指恶意修改DNS响应将用户导向钓鱼网站；国内常见的"DNS污染/投毒"是在UDP层面伪造DNS响应包，且因为UDP无状态，客户端会采信最先到达的响应。DNSSEC（DNS Security Extensions）通过在DNS记录上附加数字签名来防止伪造/篡改，但并不加密查询通信（DNS over HTTPS/DoH/DNS over TLS/DoT才是加密解决方案）。

4. **localhost和127.0.0.1的关系不需要DNS**：操作系统在解析localhost时不需要查询DNS，而是通过本机的hosts文件（Windows: C:\Windows\System32\drivers\etc\hosts, Linux: /etc/hosts）直接映射到127.0.0.1。hosts文件的优先级高于DNS查询。

## 例题

**例题1**：用户在浏览器中输入www.example.com后，从DNS解析到最终页面显示的完整过程是什么？

**解答**：（1）浏览器检查自身DNS缓存；（2）未命中则调用操作系统的DNS解析器（stub resolver）；（3）OS解析器查询本地DNS服务器（如ISP或8.8.8.8）——递归查询；（4）本地DNS服务器执行迭代查询：先问根服务器→获得.com顶级域名服务器的IP→再问.com服务器→获得example.com权威服务器的IP→最后问权威服务器→获得IP地址；（5）本地DNS将结果缓存在本地并返回给客户端；（6）浏览器获得www.example.com的IP后建立TCP连接发送HTTP请求获取页面。每步都有TTL控制缓存的时效。

**例题2**：用户同时使用电信(202.96.134.133)和Google(8.8.8.8)作为DNS服务器。电信DNS对某域名的解析返回电信CDN节点IP，而Google DNS返回的是海外源站IP。请解释为什么同一域名会获得不同的A记录，这种机制有什么好处和副作用。

**解答思路**：这是智能DNS（GeoDNS/ECS）机制——权威DNS根据查询来源的IP地址（或本地DNS转发请求时附带的ECS/EDNS Client Subnet子网信息），返回物理上离用户最近的服务器IP。好处：优化用户体验（低延迟）、实现地域负载均衡和CDN分发。潜在副作用：（1）DNS缓存按DNS服务器视角而非最终用户视角缓存，可能导致跨境访问延迟（如果误使用了海外DNS服务器）；（2）ECS子网信息可能泄露用户隐私（减少了IP地址的前缀长度）；（3）不同DNS服务器返回不同IP会导致一致性策略难以控制，CDN的故障切换可能需要依赖更复杂的智能路由逻辑。

## 代码示例

```bash
# DNS查询常用命令
nslookup www.example.com                     # 查询A记录
nslookup -type=MX example.com                # 查询MX记录
nslookup www.example.com 8.8.8.8            # 指定DNS服务器

dig www.example.com                           # 详细查询
dig +short www.example.com                    # 简洁输出
dig -t MX example.com                         # 按类型查询
dig +trace www.example.com                    # 跟踪整个迭代过程

host www.example.com                          # 简洁的DNS查询工具

# 查看本地DNS缓存(macOS)
sudo dscacheutil -cachedump -entries host     # macOS
sudo killall -INFO mDNSResponder             # 刷新DNS缓存(macOS)
ipconfig /flushdns                            # Windows
sudo systemd-resolve --flush-caches           # Linux (systemd-resolved)
```

```python
import socket

# Python DNS查询
ip = socket.gethostbyname('www.example.com')
print(f"www.example.com → {ip}")

# 使用dnspython库进行更详细的查询
# import dns.resolver
# answers = dns.resolver.resolve('example.com', 'A')
# for rdata in answers:
#     print(f"A记录: {rdata}")
# answers = dns.resolver.resolve('example.com', 'MX')
# for rdata in answers:
#     print(f"MX记录: {rdata.exchange} 优先级:{rdata.preference}")
```

## 关联页面

[[应用层-HTTP]] [[传输层-UDP]] [[应用层-SMTP-POP3-IMAP]]
