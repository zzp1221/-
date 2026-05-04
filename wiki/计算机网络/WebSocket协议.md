---
title: "WebSocket协议详解"
course: 计算机网络
chapter: 应用层
difficulty: INTERMEDIATE
tags: [计算机网络, WebSocket, 实时通信, 全双工]
aliases: [WebSocket Protocol]
source: "RFC 6455 (WebSocket); MDN WebSocket API文档"
updated_at: 2026-05-02
---

## 核心定义

WebSocket在HTTP升级连接后提供全双工的持久TCP通道。握手：客户端发送Upgrade: websocket+Sec-WebSocket-Key，服务端返回101 Switching Protocols+Sec-WebSocket-Accept(基于Key计算)。之后通信使用WebSocket帧：opcode(文本/二进制/ping/pong/close)、masking key(客户端→服务端必须掩码防中间件缓存投毒)、payload。

## 关键结论

1. 相比HTTP轮询：减少延迟和头部开销 2. 心跳保活：ping/pong帧（应用层或浏览器自动）3. 代理和防火墙可能阻断WS连接（需wss://或回退HTTP长轮询）4. SSE(Server-Sent Events)适合单向推送，WebSocket适合双向

## 关联页面

[[HTTP协议基础]] [[实时通信技术对比]]
