---
title: "欧拉函数与RSA密码原理"
course: 离散数学
chapter: 数论
difficulty: INTERMEDIATE
tags: [离散数学, 欧拉函数, RSA, 密码学]
aliases: [Euler's Totient, RSA]
source: "A Method for Obtaining Digital Signatures and Public-Key Cryptosystems (RSA 1978); Rosen 第4章"
updated_at: 2026-05-02
---

## 核心定义

欧拉函数φ(n)：1到n中与n互素的数的个数。若n=pq(p,q素数)：φ(n)=(p-1)(q-1)。RSA密钥生成：1.选大质数p,q 2.n=pq, φ(n)=(p-1)(q-1) 3.选e(与φ(n)互素) 4.求d=e^(-1) mod φ(n)。公钥(e,n)，私钥(d)。加密c=m^e mod n，解密m=c^d mod n。安全性基于大数因式分解的困难性。

## 关键结论

1. 欧拉定理a^φ(n)≡1 (mod n)(gcd=1)→RSA正确性基础 2. 费马小定理是欧拉定理p素数时特例(p∤a→a^(p-1)≡1 mod p) 3. RSA需填padding(OAEP)防选择密文攻击

## 关联页面

[[同余与模运算]] [[群论基础]]
