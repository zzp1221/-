---
title: "安全多方计算SMPC"
course: 信息安全
chapter: 密码协议
difficulty: ADVANCED
tags: [信息安全, SMPC, 安全多方计算, 隐私, 零知识]
aliases: [Secure Multi-Party Computation, SMPC, Garbled Circuits]
source: "Yao 1982 (Millionaires' Problem); Yao 1986 (Garbled circuits); Cramer, Damgard & Nielsen《Secure Multiparty Computation》"
updated_at: 2026-05-02
---

## 核心定义

安全多方计算(SMPC)使n个参与方在私有输入上联合计算函数f(x1,...,xn)而互不泄露自己的输入。通用SMPC基础——Yao的混淆电路(Garbled Circuit, Yao 86)：一个参与方为布尔电路中的每个门创建混淆后真值表并发送给另一方；另一方通过不经意传输(OT/Oblivious Transfer)获取自己的输入电路线对应的混淆值；执行混淆门(不需要电路结构信息尽可得最终输出)。GMW协议(1987)使用秘密共享(secret-sharing)实现多方参与(multi-party)的SMPC。

## 应用与效率

SMPC在以下几个方面有应用：1.)隐私保护的机器学习(训练和推理——模型中各方数据不外泄) 2.)安全拍卖(不需要公开出价就能确定获胜方) 3.)密钥管理(多方签名——将完整私钥的切片分散持有,联合签名无需拼接重建私钥/ECDSA threshold signing) 4.)隐私保护的集合交集PSI(Private Set Intersection——两个组织了解共同客户而不暴露各自的完整客户列表)。当前对SMPC的性能优化：混淆电路的硬件加速、OT extension(扩展少量OT实现大量OT——IKNP 2003)。

## 关键结论

1. SMPC的信息论安全需要大多数参与方诚实(semi-honest/malicious model) 2. 混淆电路的主要成本在AES-based混淆(+网络传输)——但pre-computing可大幅节省在线协商时间 3. 同态加密(HE/FHE)与SMPC互为补充——在不同情境各自优势 4. 恶意模型下的SMPC需额外验证步骤(效度校验) 5. 近年来SMPC已从理论走向实用(在医疗/金融领域出现真实的私有cross-org协作)

## 关联知识点

[[信息安全-密码学基础]] [[信息安全-同态加密与隐私计算]] [[离散数学-安全协议形式化分析]]
