---
title: "硬件安全模块HSM"
course: 信息安全
chapter: 硬件安全
difficulty: INTERMEDIATE
tags: [信息安全, HSM, 硬件安全, 密钥管理, SGX]
aliases: [Hardware Security Module, HSM, TEE, SGX]
source: "FIPS 140-3 (Security Requirements for Cryptographic Modules); Intel SGX developer guide; AWS CloudHSM/Nitro Enclaves"
updated_at: 2026-05-02
---

## 核心定义

硬件安全模块(HSM)是专门保护密钥和密码运算的物理硬件设备。HSM提供：1.)密钥生成(在硬件中的真随机数发生器——TRNG) 2.)密钥存储(私钥永不离硬件——永不暴露在明文中) 3.)加密/签名运算(在硬件内执行)。FIPS 140-3 Level 3认证要求硬件对篡改的检测和响应(钥匙删除)。TEE(Trusted Execution Environment)是CPU中的安全飞地(enclave)——Intel SGX/AMD SEV/ARM TrustZone在不可信OS中提供可信执行环境(加密的内存区域)。Nitro Enclaves(AWS)在EC2实例中提供无外部连接的虚拟机。

## PKI与HSM

证书机构(CA)使用HSM保护根私钥——这是PKI信任链的物理基础。HSM支持PKCS#11(Cryptoki)标准——C库API的统一操作接口(C_GenerateKey/C_Sign/C_Encrypt)。Cloud HSM(如AWS CloudHSM/GCP Cloud KMS with HSM)通过多租户架构(分区)提供FIPS 140-3认证的HSM服务而不需物理硬件。KMS(Key Management Service)在HSM前增加一层——通过数据密钥(data key)与主密钥(master key)分离，定期轮换(master key rotation自动——数据密钥使用envelope encryption)。

## 关键结论

1. HSM保护的最核心资源是根私钥(RCA的private key) 2. SGX enclave受内存加密保护——即使系统管理员/dump内存也无法读明文 3. BIP32/HSM硬件钱包安全实现比特币(cryptocurrency)的密钥管理(冷存储——永不暴露/联网) 4. TPM可被视为计算机内置的轻量HSM(提供密钥密封和平台证明——seal/bind/unseal) 5. 密钥安全的原则——密钥永不离开安全模块(签名在模块内完成)

## 关联知识点

[[信息安全-密码学基础]] [[操作系统-安全启动与TPM]] [[信息安全-安全多方计算SMPC]]
