---
title: "特性开关FeatureFlag"
course: 软件工程
chapter: DevOps
difficulty: INTERMEDIATE
tags: [软件工程, FeatureFlag, 特性开关, 渐进部署]
aliases: [Feature Toggles, Feature Flags, Canary Releases]
source: "Fowler 2010 (FeatureToggle); LaunchDarkly文档; Google SRE Book Ch 16 (Canarying)"
updated_at: 2026-05-02
---

## 核心定义

特性开关(feature flag/toggle)是在运行时决定是否启用某个功能片段的开关。四类活用：1.)发布开关(release toggles)——允许代码部署到生产但不马上激活(持续部署的使能器——解耦deployment和release) 2.)实验开关(experiment toggles)——A/B测试——根据用户分组展示不同版本收集反馈。3.)运维开关(ops toggles)——运维在系统压力大时关闭非关键功能。4.)权限开关(permission toggles)——仅特定用户(如内部用户)可见的preview功能。Trunk-Based Development + Feature Flag使得分支无需维持过长的生命周期。

## 实现原则

特性标志管理平台(LaunchDarkly/ConfigCat/OpenFeature)提供集中管理、targeting规则(A/B/n% rollout)和多语言SDK。基于服务端而非客户端的flags更安全。Flag应该尽量短期存活(否则flag removal债务累积——旗标坟墓)。避免两个flags交互导致不可测状态(组合爆炸——可以通过设计不相交flags或集成测试覆盖关键组合)。Multivariate flags支持多值(非binary——如蓝色/红色/绿色三组A/B/C)。动态flag evaluation促进runtime变更(不重启服务)。

## 关键结论

1. 每个flag有明确的主人(owner)和清除计划(sunset date) 2. flag的过度嵌套(super flags)导致维护灾难 3. stale flags(无人维护)引入安全和技术债务 4. 错误处理flag——若flag service不可用应fallback到安全默认值(default safe) 5. Canarying通过flag为新的部署逐步增加流量分配(并结合监控自动回滚)

## 关联知识点

[[软件工程-持续集成与持续部署]] [[软件工程-混沌工程]] [[分布式系统-灰度发布与流量管理]]
