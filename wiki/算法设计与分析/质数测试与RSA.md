---
title: "质数测试与RSA"
course: 算法设计与分析
chapter: 数论算法
difficulty: ADVANCED
tags: [算法, 质数测试, RSA, 数论, Miller-Rabin]
aliases: [Primality Testing, Miller-Rabin, RSA]
source: "Rivest, Shamir & Adleman 1978 (RSA); Miller 1976 & Rabin 1980; CLRS §31"
updated_at: 2026-05-02
---

## 核心定义

质数测试(primality testing)判断一个大整数是否为质数。Miller-Rabin概率测试(O(k log^3 n))：利用费马小定理(a^(p-1)≡1 mod p)的细化版本——将n-1分解为d*2^s，若a^d≠1(mod n)且a^(d*2^r)≠-1(mod n)对所有r<s，则n为合数(否则'可能是质数')。k轮后错误概率<(1/4)^k，通常使用k=40达到<2^-80。RSA密钥生成依赖寻找大质数(p和q, 2048-4096 bits)——通过Miller-Rabin筛选候选。

## RSA与数论

RSA安全性基于大整数分解难题。核心计算：选定大质数p,q → n=pq → φ(n)=(p-1)(q-1) → 选公钥e满足gcd(e,φ(n))=1(常用65537) → 计算私钥d≡e^(-1) mod φ(n)(扩展的欧几里得算法)。加密c=m^e mod n，解密m=c^d mod n。中国剩余定理(CRT)加速解密(分开模p和模q)。AKS(Agrawal-Kayal-Saxena, 2002)是里程碑——第一个确定性质数测试算法(O(log^7.5 n))。

## 关键结论

1. Miller-Rabin单轮极快(约微秒级对1024位) 2. 质数在整数中密度~1/ln(n)——筛选1/ln(n)个随机数可找到一个质数(需检查) 3. Pollard's rho和P-1算法分解中等的合数 4. 整数分解至今无多项式算法——Shor的量子算法(量子计算威胁) 5. RSA padding(OAEP)防止直接RSA的语义安全攻击

## 关联知识点

[[算法设计与分析-图算法总览]] [[信息安全-密码学基础]] [[离散数学-数论基础]]
