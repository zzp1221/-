---
title: 数字证书与CA公钥基础设施
course: 计算机网络
chapter: 网络安全
difficulty: INTERMEDIATE
tags: [数字证书, CA, PKI, X.509, 证书链, 根证书, CRL, OCSP]
aliases: [Digital Certificate, Certificate Authority, PKI, X.509, Root CA]
source:
  - 谢希仁《计算机网络》第8版
  - ITU-T X.509
updated_at: 2026-05-02

---

## 核心定义

数字证书（Digital Certificate）是公钥基础设施（PKI, Public Key Infrastructure）的核心构件，是由证书颁发机构（CA, Certificate Authority）使用自己的私钥进行数字签名的一段数据，它将一个实体的身份信息（如域名、组织名称）与该实体的公钥绑定在一起。标准的数字证书格式为X.509 v3，包含以下核心字段：版本号、序列号、签名算法标识、颁发者（CA的可分辨名称/ Distinguished Name）、有效期（Not Before / Not After）、主体（证书拥有者的DN和域名等）、主体公钥信息（公钥算法和公钥值）、扩展字段（如SAN主体别名、密钥用法、基本约束）以及CA的数字签名。验证证书的过程是：客户端使用预信任的CA根证书中的公钥，沿着证书链逐级验证每一级证书的数字签名，直到验证网站的服务器证书。证书体系解决了非对称加密中的公钥分发问题——用户不需要预先知道每个网站的公钥，只需要信任少数根CA（浏览器/操作系统中预置的根证书库），就能安全验证从未访问过的网站的身份。

## 关键结论

- X.509证书验证链（Certificate Chain）的工作原理：根CA（自签名，绝对信任）→中间CA（由根CA签发，可多个层级）→终端实体证书（服务器/客户端证书）。验证时依次检查每一级的签名、有效期和吊销状态。若链路中任何一个环节验证失败，整个验证失败
- 证书吊销机制：（1）CRL（证书吊销列表）——CA定期发布的吊销证书序列号列表，由客户端下载验证，开销大且有更新延迟；（2）OCSP（在线证书状态协议）——客户端实时查询指定证书是否已吊销，HTTP通信低延迟；OCSP Stapling——服务器在TLS握手中附带一个CA签名的时间戳OCSP响应，降低客户端查询开销和隐私泄露
- 域名验证（DV）、组织验证（OV）和扩展验证（EV）证书：DV证书仅验证域名控制权（自动化，如ACME协议，几秒内签发，免费）；OV证书需CA人工验证组织注册信息；EV证书有最严格的身份验证（法律实体验证）。DV证书能被广泛使用的推动力量是Let's Encrypt（免费、自动化、支持ACME v2协议）
- 证书透明（Certificate Transparency, CT）是Google推动的安全机制：CA在签发证书时必须将证书提交到公共的CT日志服务器（由独立运营的日志监控和审计），所有提交都有公开的时间戳和不可否认的加密证明。如果CA签发假冒证书，CT日志会留下不可篡改的证据，让域主和安全研究者能够检测
- 根证书存储：浏览器和操作系统维护自己的根证书库（如Mozilla NSS、Microsoft Root Program、Apple Root Certificate Program）。要成为预置根CA，需要满足CA/B Forum的基准要求并通过审计。世界各大根CA约有上百个

## 易错点

1. **自签名证书不等于"不安全"**：在CA不可用的私有环境（内部网络、开发测试），自签名证书是可以使用的——只要所有客户端都将该自签名证书添加为信任。但在公共互联网中，自签名证书无法被陌生人验证，浏览器会显示不安全警告。

2. **证书中的CN已逐渐被SAN取代**：X.509证书中的Common Name（CN）字段曾用于指示域名，但现在已被Subject Alternative Name（SAN）扩展字段取代。浏览器优先检查SAN中的域名，如果SAN存在而CN不匹配也不影响验证。现代证书必须包含SAN。

3. **根证书是自签名的，中间证书不是**：这个容易将两个概念混淆。根CA证书是自签名的（颁发者和主体是同一个CA），中间CA证书是由上一级CA签发的。信任锚是根本身，中间证书通过根信任链传递信誉。

4. **证书到期后不更新会中断服务**：Let's Encrypt证书有效期仅90天，需要定期使用自动化工具（如Certbot）更新部署。如果网站证书过期，浏览器会拒绝访问并显示全屏安全警告，用户无法绕过。

## 例题

**例题1**：浏览器在访问https://example.com时的证书验证全过程是什么？

**解答**：（1）TLS握手时服务器发送证书链（服务器证书+中间CA证书→根CA证书通常不发送因为浏览器已信任）；（2）浏览器取出服务器证书，检查证书域名（SAN或CN）与访问域名example.com是否一致；（3）检查有效期是否在Not Before和Not After之间；（4）检查证书用途扩展——服务器证书必须包含Server Authentication（TLS Web Server Authentication）用途；（5）获取签发该证书的中间CA证书，用中间CA公钥验证服务器证书的签名——如果签名有效，记录该环节通过；（6）对中间CA证书，找到签发它的根CA证书（浏览器内置信任库中查找），用根CA公钥验证中间CA证书的签名；（7）检查各环节证书的吊销状态（CRL/OCSP/OCSP Stapling）；（8）所有环节验证通过，浏览器显示安全锁图标。

**例题2**：Let's Encrypt的ACME协议如何实现域名验证（Domain Validation），为什么这个过程保证了安全性？

**解答思路**：ACME（自动证书管理环境）协议通过在域名的Web服务器或DNS系统上放置一个CA指定的挑战令牌（challenge token）来验证客户端对该域名的控制权。HTTP-01挑战：客户端在http://<domain>/.well-known/acme-challenge/<token>路径放置指定内容；DNS-01挑战：客户端在域名下创建TXT记录_acme-challenge.<domain>。安全性保障：能完成这些操作的实体必定对该域名有控制权（管理着Web服务器文件系统或DNS记录），从而证明其是该域名的合法管理者。验证通过后ACME客户端即可自动获取证书并续签。

## 代码示例

```bash
# OpenSSL查看证书详情
openssl x509 -in certificate.crt -text -noout
openssl s_client -connect example.com:443 -showcerts </dev/null

# 生成自签名证书（用于测试环境）
openssl req -x509 -newkey rsa:2048 -keyout key.pem -out cert.pem -days 365 -nodes

# 使用Certbot获取Let's Encrypt证书
certbot certonly --webroot -w /var/www/html -d example.com
certbot renew --dry-run  # 测试证书更新

# 构建CA并签发证书（私有PKI）
openssl genrsa -out ca-key.pem 2048
openssl req -new -x509 -key ca-key.pem -out ca-cert.pem -days 3650
openssl genrsa -out server-key.pem 2048
openssl req -new -key server-key.pem -out server.csr
openssl x509 -req -in server.csr -CA ca-cert.pem -CAkey ca-key.pem -CAcreateserial -out server-cert.pem -days 365
```

## 关联页面

[[数字签名]] [[非对称加密-RSA]] [[SSL-TLS]] [[应用层-HTTPS]]
