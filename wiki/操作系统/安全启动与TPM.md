---
title: "安全启动与TPM"
course: 操作系统
chapter: 安全
difficulty: ADVANCED
tags: [操作系统, 安全启动, TPM, 信任链, 硬件安全]
aliases: [Secure Boot, TPM, Trusted Platform Module, Measured Boot]
source: "UEFI Specification §27 Secure Boot; TCG TPM 2.0 Specification; Linux integrity subsystem文档"
updated_at: 2026-05-02
---

## 核心定义

安全启动(Secure Boot)是UEFI固件的安全特性：启动链中的每个组件(固件→bootloader→OS kernel→驱动)的签名在加载前被验证。只有被平台信任的密钥签名的二进制才被允许执行。信任锚是Platform Key(PK)——平台所有者密钥。TPM(Trusted Platform Module, 可信平台模块)是硬件安全元件，通过PCR(Platform Configuration Register)记录系统启动测量链(measured boot)实现远程证明(remote attestation)——向远程方证明系统运行在可信状态。

## 实现与Linux IMA

Linux Integrity Measurement Architecture(IMA)将启动安全扩展到运行时——每个被执行/读取/映射的文件进行哈希验证。EVM(Extended Verification Module)保护文件元数据的完整性。dm-verity提供块设备级别的完整性检查——Android的verified boot使用它。TPM的sealing功能将数据(密钥)绑定到特定的PCR状态(仅在特定系统配置下释放)。硬件TPM被fTPM(固件TPM,Intel PTT/AMD fTPM)补充但fTPM曾有稳定性问题。

## 关键结论

1. Secure Boot ≠ 只运行微软签名代码——用户可以加入自己的MOK(Machine Owner Key) 2. TPM密钥永不离开芯片——私钥密封在硬件的防篡改存储中 3. 远程证明依赖quote——对指定PCR的TPM签名值 4. user-space stack(tss2/tpm2-tools)与TPM交互 5. 完全的安全启动实现非常复杂——许多生产系统仅实现了部分链

## 关联知识点

[[操作系统-容器隔离(cgroups/namespace)深度]] [[信息安全-侧信道攻击防御]] [[计算机组成原理-可信执行环境TEE]]
