---
title: 非对称加密与RSA算法
course: 计算机网络
chapter: 网络安全
difficulty: ADVANCED
tags: [非对称加密, 公钥加密, RSA, 密钥对, 大素数, 欧拉函数]
aliases: [Asymmetric Encryption, Public Key Cryptography, RSA Algorithm, Public Key, Private Key]
source:
  - 谢希仁《计算机网络》第8版
updated_at: 2026-05-02

---

## 核心定义

非对称加密（Asymmetric Encryption / Public-Key Cryptography）是现代密码学的革命性概念，其核心特征是加密和解密使用两个不同但数学上相关联的密钥——公钥（Public Key）和私钥（Private Key）。公钥可以公开发布（如嵌入在数字证书中），任何持有该公钥的人可以用来加密消息；私钥由所有者秘密保管，用于解密密文。公钥体制的数学基础是单向陷门函数——从公钥推导出私钥在计算上不可行。RSA（Rivest-Shamir-Adleman）是最经典也是使用最广泛的非对称加密算法，其安全性基于大整数因子分解的困难性。RSA密钥生成步骤：（1）随机选择两个大素数p和q（通常各为1024位以上，总模数2048位以上）；（2）计算n=p×q，φ(n)=(p-1)(q-1)为欧拉函数值；（3）选择公钥e满足1<e<φ(n)且gcd(e,φ(n))=1（常用e=65537=2^16+1，素数且只有两个1位，模幂运算快）；（4）计算私钥d = e^(-1) mod φ(n)（模逆元）。加密C = M^e mod n，解密M = C^d mod n。非对称加密解决了对称加密的密钥分发难题（公钥可以公开传播），为数字签名、密钥交换和证书体系提供了理论基础。

## 关键结论

- RSA的核心数学原理：欧拉定理——若gcd(M,n)=1，则M^φ(n) ≡ 1 (mod n)。因此M^(e×d) = M^(1+k×φ(n)) ≡ M (mod n)。解密正确性的保证来自欧拉定理
- 公钥和私钥是成对生成的，公钥公开私钥保密。公钥加密只有对应私钥可解密；反过来，私钥加密（签名）只有对应公钥可验证。这两个操作互为逆运算
- 非对称加密的计算速度比对称加密慢数百至数千倍——RSA-2048的加解密速度为几十KB/s级，而AES可达GB/s级。因此实际应用中通常使用混合加密方案：非对称加密仅用于传递/协商对称会话密钥（如TLS握手），后续海量数据用对称密钥进行
- RSA密钥长度建议：1024位已被弃用（已可被足够决心和资源的攻击者因子分解），2048位是目前最低推荐标准（预计安全至2030年），4096位提供更高安全裕度但性能下降。后量子密码学时代RSA终将被基于格/编码/多变量等新型算法取代
- 除了加密之外，非对称密码体制最重要的应用：数字签名（认证消息来源和完整性）、密钥交换（Diffie-Hellman及基于RSA的密钥传输）、身份认证和数字证书体系

## 易错点

1. **公钥加密并不比对称加密更"安全"**：在相同密钥长度下，对称加密通常提供更高的安全强度（AES-128 ≈ 3072位RSA）。非对称加密的革命性突破在于无需预先共享密钥，而不是"加密更安全"。

2. **RSA加密有长度限制**：RSA能加密的最大明文字节数 = (密钥长度/8) - 11（填充占位）。对于2048位RSA最多加密245字节（使用OAEP填充）。不能直接用RSA加密大文件，应用混合加密。

3. **e=3不是"不安全"而是容易产生实现错误**：小的e值（如3）本身不是安全性漏洞，但在不正确填充的情况下容易受到Coppersmith攻击。标准的e=65537（素数的费马数）在安全性和性能之间取得良好平衡。

4. **RSA私钥加密不是加密操作**：用私钥对数据做模幂运算M^d mod n应该被称为"签名"而不是"加密"。因为任何持有公钥的人都可以"解密"（M^e mod n验证签名），这与保密的语义相悖。

## 例题

**例题1**：给定素数p=61, q=53，公钥e=17。计算RSA的私钥d，并加密明文M=65，验证解密结果。

**解答**：（1）n = 61×53 = 3233；（2）φ(n) = 60×52 = 3120；（3）求d满足 17d ≡ 1 (mod 3120)，使用扩展欧几里得算法：d=2753（验证：17×2753 = 46801 ≡ 1 mod 3120）。（4）加密：C = 65^17 mod 3233，计算得C = 2790。（5）解密：M = 2790^2753 mod 3233 = 65。原始明文正确恢复。

**例题2**：阐述非对称加密在HTTPS建立过程中的应用流程，特别说明RSA在其中的角色（TLS 1.2 RSA密钥交换模式）。

**解答思路**：在TLS 1.2 RSA密钥交换模式下（注意TLS 1.3已去除RSA密钥交换）：（1）客户端发送ClientHello，包含随机数和支持的密码套件列表；（2）服务器发送ServerHello + 证书（包含服务器RSA公钥）+ ServerHelloDone；（3）客户端验证证书，生成预主密钥（Pre-Master Secret, 48字节随机数），用服务器RSA公钥加密后通过ClientKeyExchange发送给服务器；（4）服务器用RSA私钥解密获得预主密钥。双方使用预主密钥+客户端随机数+服务器随机数通过PRF（伪随机函数）计算出对称会话密钥（Master Secret）；（5）之后所有通信使用对称密钥（AES等）加密。在这个过程中，RSA仅用于安全传递48字节的预主密钥——体现了典型的混合加密模式。

## 代码示例

```python
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization

# RSA密钥生成
private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,
)
public_key = private_key.public_key()

# 导出公钥（PEM格式）
pem_public = public_key.public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo
)

# RSA加密（使用OAEP填充）
plaintext = b"Secret message to encrypt"
ciphertext = public_key.encrypt(
    plaintext,
    padding.OAEP(
        mgf=padding.MGF1(algorithm=hashes.SHA256()),
        algorithm=hashes.SHA256(),
        label=None
    )
)

# RSA解密
decrypted = private_key.decrypt(
    ciphertext,
    padding.OAEP(
        mgf=padding.MGF1(algorithm=hashes.SHA256()),
        algorithm=hashes.SHA256(),
        label=None
    )
)

print(f"原始: {plaintext}")
print(f"解密: {decrypted}")
print(f"密文长度: {len(ciphertext)}字节 (固定256字节=2048/8)")
```

## 关联页面

[[网络安全-对称加密]] [[数字签名]] [[数字证书-CA]] [[SSL-TLS]] [[应用层-HTTPS]]
