---
title: 服务网格Service Mesh
course: 分布式系统
chapter: 分布式服务
difficulty: INTERMEDIATE
tags: [Service Mesh, 服务网格, Istio, Envoy, Sidecar, 数据平面, 控制平面]
aliases: [Service Mesh, 服务网格, Istio, Envoy, Sidecar Proxy]
source:
  - "Istio Documentation"
  - "Envoy Proxy Documentation"
  - "Pattern: Service Mesh, Phil Calçado (2017)"
updated_at: 2026-05-03
---

## 核心定义

Service Mesh（服务网格）是一种**基础设施层**，负责处理服务间通信。它通过在每个服务实例旁部署一个**Sidecar代理**（如Envoy），将网络通信的复杂性从应用代码中剥离出来。

**架构**：
- **数据平面（Data Plane）**：由一组智能代理（Envoy）组成，拦截服务间的所有网络通信，执行负载均衡、熔断、重试、mTLS等策略
- **控制平面（Control Plane）**：管理和配置数据平面代理，如Istio的istiod。负责服务发现、配置分发、证书管理

**核心功能**：
- **流量管理**：路由规则、流量分割（金丝雀发布）、故障注入、超时重试
- **安全**：服务间mTLS加密、认证授权（RBAC）
- **可观测性**：自动收集Metrics、Traces、Logs，无需修改应用代码
- **策略执行**：限流、访问控制、配额管理

**工作原理**：
1. 应用Pod中注入Sidecar代理（Envoy）
2. 所有入站和出站流量经过Sidecar
3. Sidecar根据控制平面下发的策略执行流量管理
4. 应用代码无感知，无需修改

**代表实现**：
- **Istio**：最流行的Service Mesh，基于Envoy，功能全面
- **Linkerd**：轻量级Service Mesh，性能好
- **Consul Connect**：HashiCorp的Service Mesh方案

## 关键结论

- Service Mesh的核心价值是**将网络通信逻辑从业代码中剥离**，实现关注点分离
- **Sidecar模式**的代价是**额外的延迟和资源开销**——每个请求多经过两次代理
- Service Mesh与**Kubernetes**深度集成——通过CRD定义流量规则，通过Admission Controller自动注入Sidecar
- **eBPF**技术可能改变Service Mesh的实现方式——在内核层实现流量拦截，减少Sidecar开销
- Service Mesh适合**大规模微服务**（>50个服务），小规模系统使用SDK（如Spring Cloud）更简单

## 易错点

1. **过度使用Service Mesh**：小规模系统引入Service Mesh会增加运维复杂度，收益不大
2. **忽视Sidecar的延迟开销**：每个请求多经过两次Sidecar（出站+入站），增加约1-3ms延迟
3. **配置复杂**：Istio的流量规则（VirtualService、DestinationRule）学习曲线陡峭

## 例题

**题目**：某公司有100个微服务，需要实现以下需求：
1. 服务间通信加密
2. 金丝雀发布（新版本先接收5%流量）
3. 自动收集分布式追踪数据
4. 熔断和重试策略

比较使用Service Mesh（Istio）和传统SDK（Spring Cloud）的方案。

**解答**：

**方案一：Service Mesh（Istio）**

| 需求 | Istio实现方式 | 应用修改 |
|------|-------------|---------|
| 通信加密 | 自动mTLS，零信任网络 | 无 |
| 金丝雀发布 | VirtualService配置流量权重 | 无 |
| 分布式追踪 | Sidecar自动注入Trace上下文 | 无 |
| 熔断重试 | DestinationRule配置熔断策略 | 无 |

**优势**：应用代码零修改，所有功能在基础设施层实现
**劣势**：运维复杂度高，需要Kubernetes专业知识

**方案二：Spring Cloud SDK**

| 需求 | Spring Cloud实现 | 应用修改 |
|------|-----------------|---------|
| 通信加密 | 手动配置TLS证书 | 需要修改代码 |
| 金丝雀发布 | 自定义负载均衡规则 | 需要修改代码 |
| 分布式追踪 | Sleuth + Brave | 需要添加依赖 |
| 熔断重试 | Resilience4j | 需要添加注解 |

**优势**：灵活，可定制
**劣势**：每个服务都需要修改，多语言支持困难

**推荐**：
- 100个微服务、多语言环境 → **Istio**（统一治理）
- 10个微服务、单语言 → **Spring Cloud**（简单灵活）

## 关联页面

[[服务发现与注册]] [[负载均衡算法]] [[熔断与降级]] [[分布式追踪]] [[API网关设计]]
