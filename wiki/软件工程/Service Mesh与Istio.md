---
title: Service Mesh与Istio
course: 软件工程
chapter: 微服务架构
difficulty: ADVANCED
tags: [软件工程, Service Mesh, Istio, Sidecar, Envoy]
aliases: [服务网格, Istio, Sidecar模式]
source:
  - Istio官方文档（istio.io）
  - Envoy Proxy文档
  - 《Service Mesh微服务架构设计》
updated_at: 2026-05-03
---

## 核心定义

Service Mesh（服务网格）是处理服务间通信的基础设施层，通过在每个服务实例旁部署代理（Sidecar模式）实现流量管理、安全、可观测性等功能，对应用代码透明。核心组件：(1)数据平面（Data Plane）：由Sidecar代理（如Envoy）组成，拦截服务的所有出入流量；(2)控制平面（Control Plane）：管理和配置数据平面的代理（如Istio的istiod）。Istio是最流行的Service Mesh实现，提供：流量管理（金丝雀发布、A/B测试、故障注入、超时重试）、安全（mTLS双向认证、授权策略、证书自动轮转）、可观测性（分布式追踪、指标采集、访问日志）。Sidecar代理拦截所有Pod的网络流量（通过iptables规则），在代理层实现负载均衡、熔断、限流、重试等功能，应用代码不需要感知。Ambient Mesh是Istio的新模式，用节点级ztunnel替代Sidecar，减少资源开销。

## 关键结论

- Service Mesh将服务治理能力从应用代码下沉到基础设施层，实现语言无关的流量管理
- Sidecar模式的代价：每个Pod多一个Envoy容器（约50-100MB内存），增加约1-3ms延迟
- mTLS是Service Mesh的核心安全能力：自动为每个服务颁发证书，零信任网络
- 金丝雀发布是Service Mesh的杀手级应用：按权重将1%流量路由到新版本
- Service Mesh适合微服务数量>50的大规模系统，小系统使用Spring Cloud等应用层方案更简单

## 易错点

1. Service Mesh不是微服务的必需品：只有当服务数量多到治理困难时才有价值
2. Sidecar代理增加了延迟和资源开销：对于延迟敏感的系统需要评估影响
3. Service Mesh不能解决所有微服务问题：业务逻辑的拆分和API设计仍然是核心

## 例题

**例1：** 使用Istio实现一个金丝雀发布：新版本v2接收10%流量，旧版本v1接收90%流量。描述配置方式。

**解答：** (1)创建两个Deployment：v1（labels: app: myapp, version: v1）和v2（labels: app: myapp, version: v2）。(2)创建一个Service：selector只匹配app: myapp（不包含version），两个版本都被选中。(3)创建VirtualService配置流量分割：hosts: [myapp], http: [route: [destination: myapp, subset: v1, weight: 90], [destination: myapp, subset: v2, weight: 10]]。(4)创建DestinationRule定义subset：subsets: [name: v1, labels: {version: v1}], [name: v2, labels: {version: v2}]。Istio的Pilot组件将流量规则推送到所有Envoy Sidecar，Envoy按权重路由请求。

## 关联页面

[[微服务架构设计]] [[负载均衡技术]] [[Docker与Kubernetes部署]]
