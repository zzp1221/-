---
title: "Docker与Kubernetes部署实践"
course: 软件工程
chapter: 云原生
difficulty: INTERMEDIATE
tags: [Docker, K8s, 容器编排]
aliases: [Docker, Kubernetes]
source: "Kubernetes官方文档; Docker文档; Kubernetes in Action (Luksa)"
updated_at: 2026-05-02
---

## 核心定义

Kubernetes是容器编排平台。核心资源：Pod(最小部署单元，1+容器共享网络/存储)、Deployment(副本管理/滚动更新/回滚)、Service(稳定的IP/DNS+负载均衡)、ConfigMap/Secret(配置/敏感信息外置)、Ingress(HTTP路由外部入口)。调度：Label+Selector实现松耦合关联。存储：PVC/PV抽象底层存储。Helm：K8s包管理。Kustomize：声明式配置定制。

## 关联结论

1. Pod是原子的——紧密耦合的容器放同一Pod 2. liveness/readiness/startup探针控制容器生命周期 3. Service Mesh(Istio/Linkerd)处理服务间通信、安全、监控

## 关联页面

[[Docker容器技术基础]] [[微服务架构设计]] [[CI/CD]]
