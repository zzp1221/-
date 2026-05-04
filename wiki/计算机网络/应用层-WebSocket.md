---
title: WebSocket协议
course: 计算机网络
chapter: 应用层
difficulty: INTERMEDIATE
tags: [WebSocket, 全双工通信, 实时通信, HTTP升级, 帧协议]
aliases: [WebSocket Protocol, RFC 6455, Full-Duplex, WebSocket Frame]
source:
  - 谢希仁《计算机网络》第8版
  - RFC 6455
updated_at: 2026-05-02

---

## 核心定义

WebSocket是HTML5规范的一部分，是一种在单个TCP连接上提供全双工、持久化通信的应用层协议。与HTTP传统的"请求-响应"单向模式不同，WebSocket建立连接后，客户端和服务器之间可以随时互相发送数据（双向推送），无需每次通信都重建连接或携带完整的HTTP头部。WebSocket的建连过程通过HTTP协议升级完成：客户端发送一个特殊的HTTP Upgrade请求（Connection: Upgrade + Upgrade: websocket），服务器同意升级后返回101 Switching Protocols状态码，之后该TCP连接从HTTP协议切换为WebSocket协议，后续的数据交换使用WebSocket的轻量级帧格式（最小仅2字节的帧头开销）。WebSocket的端口默认与HTTP共用（80/443），ws://表示非加密，wss://表示基于TLS的加密WebSocket。WebSocket广泛应用于Web实时通信场景（在线聊天、协作编辑、实时数据面板、多人在线游戏、金融行情推送）。

## 关键结论

- WebSocket通过HTTP Upgrade握手建立连接：客户端请求含Upgrade: websocket, Connection: Upgrade, Sec-WebSocket-Key（随机Base64编码的16字节密钥）, Sec-WebSocket-Version: 13等头部；服务器回复101 Switching Protocols, Sec-WebSocket-Accept（由客户端Key+固定GUID做SHA-1哈希后Base64编码）。握手设计确保WebSocket连接不会被误解析为HTTP请求
- WebSocket帧结构：操作码（4bit，文本帧/二进制帧/关闭帧/Ping帧/Pong帧/连接关闭等）、掩码标志（1bit，客户端→服务器必须掩码，防止缓存投毒攻击）、载荷长度（7bit+可选扩展16/64bit）、掩码密钥（4字节，仅客户端→服务器存在）、载荷数据。帧的最小开销仅2-6字节，远小于HTTP每请求几百字节的头部
- WebSocket的心跳检测机制：Ping帧和Pong帧（控制帧，操作码9和10）用于应用层心跳检测——发送方发Ping帧，接收方必须以Pong帧回应。心跳机制用于保持NAT/防火墙的连接跟踪不被清除，也用于检测对端是否存活（用于连接的优雅/非优雅断线处理）
- WebSocket和HTTP/2 Server Push的区别：WebSocket是全双工双向实时通道，客户端和服务器可以随时发起数据传送；HTTP/2 Server Push仅是服务器在客户端请求前"预先推送"相关资源（如CSS/JS），不具有WebSocket的即时交互性。两者的使用场景完全不同：前者用于交互式实时应用，后者用于请求-响应场景的预加载优化
- 与轮询（Polling）和长轮询（Long Polling）的对比：传统HTTP轮询需要周期性地发请求检查新数据（浪费带宽和服务器资源）；长轮询减少请求次数但仍在有数据时需要额外往返开销。WebSocket消除了轮询带来的延迟和带宽浪费，是真正的事件驱动通信模型

## 易错点

1. **WebSocket不是"基于HTTP的"**：WebSocket仅在建立连接阶段借用HTTP协议进行升级握手。握手完成后"脱离"了HTTP，后续的数据传输使用WebSocket自己的帧协议，不受HTTP的请求-响应模型约束和头部开销限制。客户端也无法在同一个WebSocket连接上再发送HTTP请求。

2. **客户端→服务器数据必须掩码的原因**：WebSocket协议要求客户端发送的帧必须使用32位掩码密钥进行简单的XOR掩码处理，而服务器→客户端数据不强制掩码。原因是防止缓存投毒攻击——攻击者在共享网络中间通过伪造WebSocket帧注入恶意脚本，代理/缓存服务器将其误识别为HTTP响应部分而缓存，将恶意脚本投递到其他用户。掩码随机化使攻击者无法精准控制中间设备的缓存解释。

3. **WebSocket的关闭过程也是双向的**：一方发送Close帧申请关闭，另一方回复Close帧确认。Close帧可携带状态码（1000正常关闭/1001端点离开了/1002协议错误/1008违反策略等）。TCP的FIN/Wavehand仅表示底层连接不再有数据，WebSocket的应用层Close帧提供更明确的关闭原因。

4. **wss://不是HTTPS的WebSocket**：严格来说wss://是WebSocket over TLS，类似于HTTPS是HTTP over TLS。wss://使用与HTTPS相同的端口号约定（默认443），但协议握手和后续通信都是不同的协议。

## 例题

**例题1**：WebSocket的HTTP Upgrade握手请求中的Sec-WebSocket-Key字段的作用及其生成和验证机制。

**解答**：Sec-WebSocket-Key是客户端随机生成的16字节值（Base64编码后约24个字符），其作用：（1）防止缓存代理服务器错误处理WebSocket升级——该字段必须存在且服务端验证计算正确否返回101；（2）防止旧版HTTP服务器误将WebSocket请求当作普通HTTP处理但不发送必要头部（攻击向量）。验证流程：客户端：Key = Base64(random(16))；服务器：计算Accept = Base64(SHA-1(Key + "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"))，此GUID是RFC 6455定义的固定魔术字符串。服务器返回的Sec-WebSocket-Accept必须等于客户端期望的计算结果。客户端验证通过后切换协议。

**例题2**：比较在实时数据推送场景中WebSocket和HTTP/2流式响应的优势与劣势。

**解答思路**：WebSocket优势：（1）双向推送（服务器→客户端推送 + 客户端→服务器上行）——HTTP/2流式响应本质是单向服务器推送；（2）WebSocket帧开销极低（2-6字节vs HTTP/2帧至少9字节+头压缩）；（3）WebSocket支持原生心跳和超时机制——HTTP流难以识故意断开和网络断开的区别。HTTP/2优势：（1）可以在同一个HTTP/2连接上复用Web请求和流；（2）自动获得了HTTP生态的缓存、CDN、负载均衡支持；（3）HTTP/2的Server-Sent Events（SSE）更简单——仅服务器到客户端单向。结论：需要全双工交互优选WebSocket；单纯服务器推数据可用SSE或gRPC流。

## 代码示例

```javascript
// 浏览器端JavaScript WebSocket API
const ws = new WebSocket('wss://example.com/socket');

ws.onopen = () => {
    console.log('WebSocket连接已建立');
    ws.send(JSON.stringify({ type: 'subscribe', channel: 'news' }));
};

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log('收到消息:', data);
};

ws.onclose = (event) => {
    console.log(`连接关闭, 码=${event.code}, 原因=${event.reason}`);
};

ws.onerror = (error) => {
    console.error('WebSocket错误:', error);
};

// 心跳维持
setInterval(() => {
    if (ws.readyState === WebSocket.OPEN) {
        ws.send('ping');
    }
}, 30000);
```

```python
# Python WebSocket简单示例
# 使用websockets库 (pip install websockets)
# import asyncio, websockets
# async def handler(websocket, path):
#     async for message in websocket:
#         await websocket.send(f"Echo: {message}")
# start_server = websockets.serve(handler, "localhost", 8765)
# asyncio.get_event_loop().run_until_complete(start_server)
# asyncio.get_event_loop().run_forever()
```

## 关联页面

[[应用层-HTTP]] [[应用层-HTTPS]] [[TCP三次握手]] [[TCP四次挥手]]
