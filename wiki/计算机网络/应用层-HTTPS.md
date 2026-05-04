---
title: HTTPS安全超文本传输协议
course: 计算机网络
chapter: 应用层
difficulty: INTERMEDIATE
tags: [HTTPS, TLS, SSL, 加密传输, 证书, HSTS, 握手过程]
aliases: [HTTP Secure, HTTPS, HTTP over TLS, HTTP over SSL]
source:
  - 谢希仁《计算机网络》第8版
  - RFC 2818, RFC 8446 (TLS 1.3)
updated_at: 2026-05-02

---

## 核心定义

HTTPS（Hypertext Transfer Protocol Secure，安全超文本传输协议）是HTTP协议的安全版本，通过TLS（Transport Layer Security，传输层安全协议，前身是SSL）在HTTP和TCP之间插入加密层，实现通信加密、身份验证和数据完整性保护。HTTPS运行在TCP端口443上。其工作流程为：TCP三次握手建立后，客户端和服务器进行TLS握手——协商加密套件（密钥交换算法、对称加密算法、消息认证码算法）、通过数字证书验证服务器身份（以及可选的客户端证书验证）、协商生成会话密钥用于后续通信的对称加密。TLS握手完成后，所有HTTP数据（请求和响应）都使用协商的会话密钥进行加密传输。HTTPS保护了数据的机密性（防窃听）、完整性（防篡改）和服务器身份真实性（防伪造），是互联网安全的基础。现代Web安全实践强烈推荐甚至强制所有Web服务使用HTTPS。

## 关键结论

- HTTPS = HTTP + TLS（加密+认证+完整性）。TLS工作在应用层与传输层之间，它在传输层TCP连接建立后、HTTP数据传输前进行安全握手。HTTPS不是一种独立的协议，而是HTTP over TLS/SSL的简称
- TLS 1.3握手机制显著简化（1-RTT握手，首次连接可做到1-RTT）：ClientHello（含密钥共享参数和猜测的密码套件）→ServerHello（选定套件+服务器密钥共享参数+证书+Finished）→Client Finished。相比TLS 1.2的2-RTT握手减少了一半的建连时延。TLS 1.3还支持0-RTT恢复（PSK模式）
- HTTPS的证书验证链：客户端收到服务器证书后，检查证书中的域名与访问域名是否一致、证书是否在有效期内、证书是否被吊销（OCSP/CRL），并沿着证书链向上追溯直到根证书（浏览器/操作系统中预置的信任根）。如果任一步骤失败，浏览器会显示安全警告
- HSTS（HTTP Strict Transport Security）：服务器通过Strict-Transport-Security响应头告知浏览器始终使用HTTPS访问该站点（max-age指定有效期），防止SSL剥离攻击（将HTTPS降级为HTTP）。浏览器收到后自动将所有HTTP请求跳转为HTTPS，即使地址栏输入了http://也会自动转到https://
- HTTPS的缺点：加密/解密和TLS握手增加CPU开销（现代硬件已基本可忽略）和首包时延（TLS 1.3的1-RTT已大幅降低）；证书获取和维护有成本（但Let's Encrypt免费提供自动签发的DV证书）；CDN和反向代理需要额外配置透明转发

## 易错点

1. **HTTPS不是端到端全链路加密**：HTTPS保证的是客户端到边缘服务器（通常是CDN或反向代理）的加密。在反向代理到后端应用服务器之间、数据中心内部网络之间，通常不加加密。Full end-to-end encryption需要应用层端到端加密（如Signal协议的E2EE），那与HTTPS的传输层加密是不同层次的概念。

2. **HTTPS加密"一切"的误区**：TLS加密TCP载荷（包括HTTP头部和HTTP体），但不加密TCP/UDP首部或IP首部。TLS握手中的Server Name Indication（SNI）明码包含域名（TLS 1.3的加密SNI/ECH正在普及但未广泛部署），可被网络中间设备看到。

3. **DV、OV、EV证书的区别**：Domain Validated（仅验证域名所有权，Let's Encrypt免费提供）、Organization Validated（额外验证组织身份）、Extended Validation（最严格验证，曾在浏览器地址栏显示企业绿色名称）。EV证书并不能阻止网络钓鱼（钓鱼者可用DV证书搭建HTTPS钓鱼网站），其安全性仅体现在身份可信度上。

4. **"HTTP严格"传输安全HSTS的缺陷**：HSTS依赖首次访问时服务器返回的HSTS头——如果用户从未通过HTTPS访问过该网站，攻击者可以在首次HTTP连接时实施SSL剥离。解决方法是HSTS Preload（浏览器内建HSTS预加载列表，名单中的域名即使首次访问也强制HTTPS）。

## 例题

**例题1**：简述TLS 1.3的握手流程，并与TLS 1.2比较主要的改进点。

**解答**：TLS 1.3握手：ClientHello发送支持的密码套件+DH密钥共享参数→ServerHello选定密码套件+服务器密钥共享参数+证书+Finished（用协商密钥加密）→Client验证证书后计算会话密钥并发送Finished。总耗时1-RTT。TLS 1.2需要2-RTT：ClientHello（不含密钥共享）→ServerHello+证书+ServerKeyExchange→ClientKeyExchange+ChangeCipherSpec+Finished→Server ChangeCipherSpec+Finished。TLS 1.3的改进：（1）去除不安全算法（RC4、3DES、CBC、SHA-1）；（2）握手机制中删除了ChangeCipherSpec协议；（3）支持0-RTT恢复；（4）加密了证书和部分握手信息（提升隐私）。

**例题2**：用户通过公共WiFi访问HTTPS网站安全吗？攻击者可能进行哪些攻击？如何防范？

**解答思路**：HTTPS保证了加密传输，攻击者无法窃听或篡改通信内容。但在公共WiFi环境下仍存在以下威胁：（1）SSL剥离——DHCP/DNS劫持+代理服务器降级到HTTP（防范：HSTS + HSTS Preload）；（2）伪造证书MITM——诱导用户安装恶意根证书（浏览器会警告证书不受信任，需用户主动同意安装）；（3）DNS劫持/投毒——将HTTPS网站域名解析到攻击者的服务器（浏览器发现证书域名不匹配会报警）；（4）WiFi的凭证窃取（Evil Twin）——攻击者建立了冒牌SSID诱导用户连接后监听明文通信和DNS。防范核心是：用户不忽略浏览器安全警告、不安装不明来源的根证书、使用VPN建立额外加密隧道。

## 代码示例

```bash
# 使用openssl测试HTTPS连接
openssl s_client -connect www.example.com:443 -servername www.example.com
openssl s_client -connect www.example.com:443 -tls1_3  # 指定TLS版本

# 查看网站证书详情
openssl s_client -connect www.example.com:443 -showcerts </dev/null 2>/dev/null | openssl x509 -text -noout

# 使用curl测试HTTPS
curl -vI https://www.example.com
curl --tlsv1.3 https://www.example.com  # 强制TLS 1.3
```

```python
import ssl
import socket

# Python创建HTTPS连接（底层）
context = ssl.create_default_context()
# 检查证书
# context.check_hostname = True
# context.verify_mode = ssl.CERT_REQUIRED

# 建立HTTPS连接并查看协商的TLS信息
with socket.create_connection(('www.example.com', 443)) as sock:
    with context.wrap_socket(sock, server_hostname='www.example.com') as ssock:
        print(f"TLS版本: {ssock.version()}")
        print(f"加密套件: {ssock.cipher()}")
        cert = ssock.getpeercert()
        print(f"证书颁发者: {cert['issuer']}")
        print(f"证书有效期: {cert['notBefore']} - {cert['notAfter']}")
```

## 关联页面

[[应用层-HTTP]] [[SSL-TLS]] [[数字证书-CA]] [[数字签名]] [[非对称加密-RSA]]
