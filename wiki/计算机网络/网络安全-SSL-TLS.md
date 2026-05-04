---
title: SSL/TLS安全协议
course: 计算机网络
chapter: 网络安全
difficulty: ADVANCED
tags: [SSL, TLS, 安全传输, 记录协议, 握手协议, 密码套件, TLS 1.3]
aliases: [Secure Sockets Layer, Transport Layer Security, TLS Handshake, TLS Record]
source:
  - 谢希仁《计算机网络》第8版
  - RFC 8446 (TLS 1.3), RFC 5246 (TLS 1.2)
updated_at: 2026-05-02

---

## 核心定义

SSL（Secure Sockets Layer）和TLS（Transport Layer Security）是位于应用层和传输层之间的安全协议，为TCP连接提供数据加密、服务器身份认证和消息完整性保护。SSL由Netscape公司在1990年代开发，经历了SSL 2.0、3.0后，标准化为TLS 1.0（RFC 2246，1999年），经历了TLS 1.1（2006年）、TLS 1.2（2008年），最新版本为TLS 1.3（RFC 8446，2018年）。TLS协议由两个核心子协议组成：（1）TLS握手协议（Handshake Protocol）——负责身份验证、密钥交换算法协商、加密套件协商和会话密钥生成；（2）TLS记录协议（Record Protocol）——使用协商的会话密钥对应用层数据进行加密、完整性保护并封装为TLS记录进行传输。TLS的设计采用混合加密体制：握手阶段使用非对称密码（RSA/ECDHE等）完成身份验证和密钥协商，数据传输阶段使用对称密码（AES-GCM/ChaCha20-Poly1305等AEAD模式）进行高速加密。TLS 1.3相比1.2进行了重大精简：只保留最安全的AEAD加密套件（AES-GCM和ChaCha20-Poly1305）、去除了RSA密钥交换（仅保留前向安全的ECDHE/DHE）、将握手往返从2-RTT降至1-RTT（并支持0-RTT恢复）、加密了服务器证书和握手后信息以增强隐私保护。

## 关键结论

- TLS 1.2完整握手（2-RTT）：(1)C→S: ClientHello（随机数、支持密码套件）→(2)S→C: ServerHello+Certificate+ServerKeyExchange+ServerHelloDone→(3)C→S: ClientKeyExchange+ChangeCipherSpec+Finished→(4)S→C: ChangeCipherSpec+Finished。总共2个往返时间后开始加密数据传输
- TLS 1.3首握（1-RTT）：(1)C→S: ClientHello（密钥共享参数+猜测的密码套件）→(2)S→C: ServerHello（选定套件）+EncryptedExtensions+Certificate+CertificateVerify+Finished→(3)C→S: Finished。密钥交换使用预共享的DH参数，仅1个往返即可完成握手开始传输应用数据
- 前向安全性（Forward Secrecy）：使用临时Diffie-Hellman（DHE/ECDHE）密钥交换时，即使服务器长期私钥将来被泄露，过去的会话密钥也不会被破解——因为每次会话生成临时的DH私钥并在握手完成后销毁。TLS 1.3移除了非前向安全的RSA密钥交换模式
- TLS记录协议：将应用层数据分为多个片段（≤16KB），每片段加密并添加记录头（Content Type+Version+Length）和认证标签（AEAD MAC）。记录按顺序编号，防止重放攻击和序列号回绕
- 密码套件（Cipher Suite）命名规则：TLS_密钥交换_身份认证_加密_哈希（如TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256）。TLS 1.3简化为仅指定AEAD和哈希（如TLS_AES_128_GCM_SHA256），密钥交换和身份认证由扩展字段独立协商

## 易错点

1. **TLS不是"第五层"或"第六层"**：虽然TLS介于应用层和传输层之间，但不能简单将它定位为"第几层"的协议。它主要提供会话层（身份识别/连接管理/加密）和表示层（数据格式转换/加密/压缩）功能。在TCP/IP模型中，它可在应用层协议内通过特定实现提供安全。

2. **TLS 1.3移除RSA密钥交换是为了消除安全隐患**：RSA密钥交换模式中，如果服务器RSA私钥泄露了，所有历史会话的预主密钥（pre-master secret）都可被解密。DHE/ECDHE使用临时密钥对，为每个会话独立生成临时DH私钥，完成后立即销毁，所以过去会话的密钥安全性不依赖长期私钥。

3. **TLS 0-RTT重放攻击的问题**：TLS 1.3支持0-RTT恢复模式允许客户端在第一次握手后缓存PSK（Pre-Shared Key），下一次连接时在首包中直接携带加密的应用数据。危险：0-RTT数据可能被攻击者截获并重放——对幂等请求（GET）相对安全，对非幂等请求（POST/PUT/DELETE）需要有应用层的防重放保护。

4. **TLS不保护连接数量信息**：TLS保护传输内容的机密性，但TLS握手过程中的SNI（服务器名称指示）字段是明文的（TLS 1.3的Encrypted SNI/ECH正在推广），而且观察者可以从加密流量的大小和时间模式中推断用户活动——这是流量分析（Traffic Analysis）的安全威胁。

## 例题

**例题1**：对比TLS 1.2和TLS 1.3的握手差异，说明从1.2升级到1.3如何减少时延。

**解答**：TLS 1.2需要2-RTT：ClientHello→ServerHello...+KeyExchange(服务器DH公钥在ServerKeyExchange中，签名保护)→ClientKeyExchange(客户端DH公钥)→Finished(开始加密)。TLS 1.3在ClientHello中直接包含客户端DH密钥共享参数（对每个支持的加密套件生成的临时密钥对公钥），服务器选定套件后可立即计算出会话密钥，从而将第2个往返（ServerHello+密钥交换+Finished）压缩为单个消息组合。TLS 1.3的0-RTT恢复模式在首次握手中通过PSK协商缓存密钥，下次连接可直接以0-RTT发送应用数据——总共只1-RTT恢复密话。相比TLS 1.2至少2-RTT或需要Session Resumption时2-RTT(TLS 1.2 Session Ticket有额外的Client Hello+Server Finished往返回顾)。

**例题2**：TLS 1.3支持PSK（Pre-Shared Key，预共享密钥）和0-RTT数据传输。描述PSK模式的工作机制和安全注意事项。

**解答思路**：PSK模式流程——首次全握手后，服务器发送NewSessionTicket消息给客户端，包含了PSK ID、PSK生命周期和对应的早期数据最大量限制。客户端下次连接时可在ClientHello的"pre_shared_key"扩展中携带该PSK ID，并在"early_data"扩展中表明打算发送0-RTT数据。服务器回复ServerHello确认PSK身份，客户端即可在后续的Finished消息前发送0-RTT应用数据。安全关注——0-RTT数据不提供前向安全性（如果PSK泄露可解密0-RTT历史数据），且容易被重放攻击。应用层必须确保：仅幂等请求使用0-RTT（如HTTP GET），非幂等操作应强制限制在握手完成后（1-RTT）。服务器可在NewSessionTicket中设置"max_early_data_size"限制0-RTT数据大小。

## 代码示例

```python
import ssl
import socket

# Python TLS客户端（TLS 1.2+）
context = ssl.create_default_context()
# 可选：设置最低TLS版本
context.minimum_version = ssl.TLSVersion.TLSv1_2

with socket.create_connection(('example.com', 443)) as sock:
    with context.wrap_socket(sock, server_hostname='example.com') as ssock:
        # 查看协商结果
        print(f"TLS版本: {ssock.version()}")
        print(f"密码套件: {ssock.cipher()[0]}")
        print(f"密钥长度: {ssock.cipher()[2]} bits")
        
        # 发送HTTPS请求
        ssock.send(b"GET / HTTP/1.1\r\nHost: example.com\r\n\r\n")
        response = ssock.recv(4096)
        print(f"响应: {response[:200]}...")
```

```bash
# 测试TLS版本支持
openssl s_client -connect example.com:443 -tls1_2   # TLS 1.2
openssl s_client -connect example.com:443 -tls1_3   # TLS 1.3

# 查看服务器支持的密码套件
nmap --script ssl-enum-ciphers -p 443 example.com

# 测试特定密码套件
openssl s_client -connect example.com:443 -cipher 'ECDHE-RSA-AES128-GCM-SHA256'
```

## 关联页面

[[应用层-HTTPS]] [[数字证书-CA]] [[数字签名]] [[非对称加密-RSA]] [[网络安全-对称加密]]
