---
title: API网关设计
course: 分布式系统
chapter: 分布式服务
difficulty: INTERMEDIATE
tags: [API网关, 网关, 路由, 认证, 限流, 反向代理]
aliases: [API Gateway, 网关设计, 反向代理, Kong, Spring Cloud Gateway]
source:
  - "Microservices Patterns, Chris Richardson, Chapter 8"
  - "Kong Documentation"
  - "Spring Cloud Gateway Documentation"
updated_at: 2026-05-03
---

## 核心定义

API网关（API Gateway）是微服务架构的**统一入口**，所有外部请求先经过网关，再路由到后端服务。API网关封装了内部服务的复杂性，为客户端提供统一的API接口。

**核心功能**：
- **请求路由**：根据URL、Header等将请求路由到不同的后端服务
- **协议转换**：将外部HTTP请求转换为内部gRPC/Thrift等协议
- **认证授权**：统一的JWT验证、OAuth2认证、API Key校验
- **限流熔断**：保护后端服务不被过载
- **请求/响应转换**：修改请求参数、聚合多个服务的响应
- **日志监控**：记录请求日志、收集Metrics

**设计模式**：

**单体网关**：一个网关处理所有API请求。简单但可能成为瓶颈和单点故障。

**BFF（Backend for Frontend）**：为不同类型的客户端（Web、Mobile、IoT）提供专门的网关。每个BFF针对特定客户端优化。

**微网关**：每个服务团队管理自己的网关。去中心化但增加运维复杂度。

**网关的扩展性**：
- **插件机制**：通过插件扩展功能（如Kong的插件系统）
- **过滤器链**：请求经过一系列过滤器（如Spring Cloud Gateway的GatewayFilter）
- **热更新**：路由规则和插件配置支持动态更新，无需重启

**主流实现**：
- **Kong**：基于Nginx/OpenResty，插件丰富
- **Spring Cloud Gateway**：Spring生态，响应式编程
- **Envoy**：高性能代理，Service Mesh数据平面
- **APISIX**：Apache开源，高性能

## 关键结论

- API网关是微服务的**门面（Facade）**，统一了外部访问接口
- **BFF模式**是大型系统的推荐方案——为不同客户端提供定制化的API
- API网关不应包含**业务逻辑**——它只负责横切关注点（认证、限流、路由等）
- **高可用**是网关的核心要求——通常部署多个实例，前面放负载均衡器
- 网关的**性能**直接影响整个系统的响应时间——选择高性能实现（如基于Nginx/Envoy）

## 易错点

1. **网关包含过多业务逻辑**：网关应该只做路由、认证、限流等横切关注点，业务逻辑应该在后端服务中实现
2. **单点故障**：单实例网关是系统可用性的瓶颈。必须部署多实例+负载均衡
3. **忽视网关的延迟开销**：网关增加了请求链路的长度，每次请求多经过网关一次。需要选择高性能实现

## 例题

**题目**：某公司的微服务系统需要支持Web端和移动端两种客户端，API需求如下：
- Web端需要完整的商品详情页数据（包含商品信息、库存、评价）
- 移动端需要精简的商品数据（只包含基本信息和价格）
- 所有请求需要JWT认证

请设计API网关架构。

**解答**：

**推荐架构：BFF模式**

```
客户端
├── Web端 → Web BFF → 后端服务
└── Mobile端 → Mobile BFF → 后端服务

后端服务：商品服务、库存服务、评价服务
```

**Web BFF**：
- 路由：`/api/web/products/{id}` → 聚合商品、库存、评价数据
- 认证：JWT验证
- 响应格式：完整商品详情（大JSON）
- 缓存：CDN缓存静态数据

**Mobile BFF**：
- 路由：`/api/mobile/products/{id}` → 只请求商品服务
- 认证：JWT验证
- 响应格式：精简数据（小JSON）
- 压缩：GZIP压缩响应

**公共网关层**（可选）：
- 统一认证（JWT验证）
- 限流（按API Key限制QPS）
- 日志收集
- 负载均衡

**架构图**：
```
Web端 → [公共网关] → Web BFF → 商品服务
                              → 库存服务
                              → 评价服务

Mobile端 → [公共网关] → Mobile BFF → 商品服务
```

**优势**：
- 每个BFF针对特定客户端优化
- 后端服务保持简单，只提供基础API
- 认证在公共网关层统一处理

## 关联页面

[[服务发现与注册]] [[负载均衡算法]] [[熔断与降级]] [[服务网格Service Mesh]] [[分布式追踪]]
