---
title: 物联网协议MQTT与CoAP
course: 计算机网络
chapter: 应用层协议
difficulty: INTERMEDIATE
tags: [计算机网络, MQTT, CoAP, IoT, 物联网]
aliases: [MQTT协议, CoAP协议, 物联网通信]
source:
  - MQTT 5.0规范（OASIS标准）
  - CoAP RFC 7252
  - Eclipse Mosquitto文档
updated_at: 2026-05-03
---

## 核心定义

MQTT（Message Queuing Telemetry Transport）是基于发布/订阅模式的轻量级消息协议，专为低带宽、高延迟、不可靠网络设计。MQTT使用Broker中转消息：发布者（Publisher）向指定主题（Topic）发布消息，订阅者（Subscriber）订阅感兴趣的主题，Broker负责路由。MQTT支持3种QoS：QoS 0（最多一次，可能丢失）、QoS 1（至少一次，可能重复）、QoS 2（恰好一次，4步握手保证）。MQTT 5.0新增：共享订阅、消息过期、用户属性、原因码。CoAP（Constrained Application Protocol）是基于UDP的RESTful协议，专为资源受限设备设计。CoAP的消息格式紧凑（最小4字节头部），使用二进制编码，支持GET/POST/PUT/DELETE方法。CoAP通过Confirmable（CON）和Non-confirmable（NON）消息实现可靠和不可靠传输。CoAP支持观察（Observe）模式，类似MQTT的订阅。CoAP与HTTP语义兼容，可通过代理网关与HTTP互转。

## 关键结论

- MQTT适合一对多的消息分发（如传感器数据上报），CoAP适合请求-响应式的资源访问
- MQTT的持久会话（Clean Session=0）使离线设备上线后能收到离线期间的消息
- MQTT主题支持通配符：`+`匹配单层（如`home/+/temperature`），`#`匹配多层（如`home/#`）
- CoAP的确认消息（CON）通过超时重传实现可靠性，类似TCP但基于UDP
- MQTT和CoAP都支持遗嘱消息（Last Will）：设备异常断开时通知其他设备

## 易错点

1. MQTT不是消息队列：虽然名字有"Queuing"，但MQTT的Broker不保证消息持久化（取决于实现）
2. QoS 2"恰好一次"只在客户端到Broker之间保证，端到端需要应用层去重
3. CoAP不是HTTP的子集：虽然语义兼容，但编码格式完全不同（二进制vs文本）

## 例题

**例1：** 一个智能家居系统有1000个传感器，每分钟上报一次温度数据。对比使用MQTT和HTTP的方案。

**解答：** MQTT方案：传感器连接MQTT Broker，发布到`home/{device_id}/temperature`。每条消息约50字节（MQTT头部2字节+主题+负载），1000设备×1次/分钟×50B=50KB/分钟。TCP长连接保持，无需每次建立连接。支持QoS 1保证至少送达。HTTP方案：每次上报需要TCP 3次握手+HTTP请求，每个请求约200字节+响应100字节，1000设备×300B×1次/分钟=300KB/分钟。如果使用HTTP Keep-Alive可减少握手开销，但仍然是请求-响应模式，服务器无法主动推送。MQTT在带宽、连接数、实时性方面都优于HTTP方案。

## 关联页面

[[应用层-HTTP]] [[WebSocket协议]] [[TCP三次握手]]
