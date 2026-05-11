---
title: "证书透明度Certificate Transparency"
course: 信息安全
chapter: PKI安全
difficulty: INTERMEDIATE
tags: [信息安全, Certificate Transparency, CT, PKI]
aliases: [Certificate Transparency, CT Logs, SCT]
source: "RFC 6962 (Certificate Transparency); Google CT project; SSLMate CT monitoring"
updated_at: 2026-05-02
---

## 核心定义

Certificate Transparency(CT)是公开可审计的证书签发日志框架，旨在检测错误签发或恶意签发的TLS证书。原理：CA将每个签发的证书提交到CT Log服务器(分布式、仅追加、密码学保证的Merkle tree日志)。日志返回SCT(Signed Certificate Timestamp)嵌入到证书扩展中——浏览器只接受包含有效SCT的证书。Merkle树保证日志行为的一致性——定期发布的Signed Tree Head(STH)锚定当前日志内容(cryptographic commitment)。监视器(Monitors)持续扫描日志寻找可疑证书(如未经授权的domains)。

## 运作与影响

审计者(Auditors)验证CT Logs的合规性(一致性证明consistency proof——新旧STH间的唯一追加路径)和包含证明(inclusion proof——某个证书在Merkle树中)。如果CA私下签发证书(未记录在CT)，则audit时被检测出(因为浏览器需要SCT)。Chrome自2018年对所有TLS证书强制CT(Apple自2021年)。全球有约20个CT Log运行(Couldflare Nimbus/Google Argon)。crt.sh是对公众的可查询CT日志搜索界面(查询一个域的所有签发证书)。

## 关键结论

1. CT不能阻止CA错误签发证书——但能让此类行为公开可见(make it public) 2. CT+HPKP(证书钉扎)/Expect-CT组合增强防御 3. 私有的证书(内部CA)可以通过域验证的CT去验证公共签发的证书 4. SCT的签名确保日志无法在证书提交后篡改 5. 日志的bloom filter/查询认证(Merkle proof)支持高效不信任验证(browser完全不需要信任日志)

## 关联知识点

[[计算机网络-TLS与HTTPS]] [[信息安全-PKI与信任模型]] [[信息安全-硬件安全模块HSM]]
