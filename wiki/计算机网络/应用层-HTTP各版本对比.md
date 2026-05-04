---
title: HTTP各版本对比
course: 计算机网络
chapter: 应用层
difficulty: ADVANCED
tags: [HTTP/1.0, HTTP/1.1, HTTP/2, HTTP/3, QUIC, 队头阻塞, 多路复用]
aliases: [HTTP Versions, HTTP/2, HTTP/3, QUIC, HTTP/1.1 vs HTTP/2]
source:
  - 谢希仁《计算机网络》第8版
  - RFC 1945, 2616, 7230, 7540, 9114
updated_at: 2026-05-02

---

## 核心定义

HTTP协议经历了三个重大版本的演进：HTTP/1.0（1996，RFC 1945）、HTTP/1.1（1997/1999，RFC 2616 / 7230-7235）、HTTP/2（2015，RFC 7540）和HTTP/3（2022，RFC 9114）。每个版本的改进都针对前一版本在性能、效率和安全上的瓶颈。HTTP/1.0使用短连接模式（每次请求-响应后关闭TCP连接），缺乏缓存和内容协商的标准化支持。HTTP/1.1引入了持久连接（Keep-Alive，默认复用TCP连接）、管道化（Pipelining，减少网络往返但因队头阻塞问题未得到广泛实施）、分块传输编码（Chunked Transfer Encoding，不需要预先知道Content-Length）、增强的缓存机制（Cache-Control/ETag）和Host头部支持虚拟主机。HTTP/2是革命性升级：引入二进制分帧层（所有通信分割为更小的二进制帧），支持真正的多路复用（Multiplexing，在单个TCP连接上并发交错的多个请求/响应流），解决了HTTP/1.1的队头阻塞问题但受到TCP队头阻塞的限制。HTTP/3基于QUIC协议（Quick UDP Internet Connections），将传输层由TCP更换为基于UDP的QUIC，解决了TCP队头阻塞，同时提供更快的连接建立（0-RTT）和内置TLS 1.3加密。

## 关键结论

- HTTP/1.1的持久连接和管道化的失败：持久连接是成功的（复用TCP连接避免重复三次握手和慢启动），但管道化（在同一个连接上连续发送多个请求不等待应答）由于队头阻塞问题（前面的请求处理慢会卡住后面所有响应）在实践中被广泛禁用，浏览器使用并行连接代替管道
- HTTP/2的核心创新——Stream多路复用：将一个TCP连接抽象为多个双向字节流（Stream），每个Stream承载一个请求-响应交互。多个Stream的帧在TCP连接上交错传输（可任意混合），通过31位的Stream ID进行区分（客户端发起的Stream ID为奇数、服务器推送的为偶数）。这彻底解决了HTTP/1.1的应用层队头阻塞
- HTTP/2服务器推送（Server Push）：服务器可以在客户端尚未请求的情况下主动推送相关资源（如HTML引用的CSS/JS）。Push帧携带PUSH_PROMISE告诉客户端将要推送的资源URL，客户端可缓存或拒绝（RST_STREAM帧）。实践中Server Push效果有限，Chrome等已逐步放弃
- HTTP/3 = HTTP/2语义 + QUIC传输层：HTTP/3保留了HTTP/2的二进制帧格式和流多路复用概念，但将传输层从TCP+TLS替换为QUIC（基于UDP）。QUIC的特性：连接独立于IP地址（Connection ID机制，移动网络中切换IP无需重新连接）、0-RTT握手（TLS 1.3 + 缓存）、无TCP队头阻塞、内置前向纠错
- HTTP/3解决的关键问题——消除TCP队头阻塞：TCP保证数据按序交付，如果某个TCP报文段丢失，之后到达的报文段即使属于其他HTTP/2 Stream也必须在内核缓冲区等待丢失的报文段重传（TCP必须保持有序）。QUIC在UDP之上实现了可靠传输，但每条Stream独立控制——一个Stream的丢失不影响其他Stream的数据投递

## 易错点

1. **HTTP/2的多路复用不等于解决了所有阻塞问题**：HTTP/2确实解除了HTTP/1.1首部行的队头阻塞（多个请求不需等服务端处理顺序），但它仍运行在TCP之上——TCP的字节顺序交付语义意味着丢失一个TCP报文段会阻塞所有Stream。这就是为什么需要QUIC/HTTP3来做最终的解决。

2. **HTTP/1.1的Host头不是HTTP/2不需要的***：HTTP/2请求中有伪头（Pseudo Header Fields）如:authority代替HTTP/1.1的Host头，但工作原理相同——指示请求属于哪个虚拟主机。伪头部以":"开头，属于帧格式的一部分而非传统KEY:VALUE请求头。

3. **HTTP/2的HPACK头部压缩和HTTP/3的QPACK**：HTTP/2使用HPACK（基于静态/动态字典和Huffman编码的头部压缩算法）来减少头部传输量（典型减少80%以上）。HPACK依赖于TCP有序交付的特性，HTTP/3因此需要设计QPACK（针对QUIC的HPACK变种）来适应Stream独立的交付特性。

4. **HTTP/3不一定比HTTP/2快在所有场景中**：QUIC在CPU利用上比TCP高（因为UDP没有硬件卸载支持），在低丢包率高带宽的有线网络中HTTP/2和HTTP/3性能相当；但在高丢包率的无线/移动网络中，HTTP/3的QUIC无队头阻塞特性带来显著的体验提升。

## 例题

**例题1**：一个网页包含1个HTML文件和5张图片。用户在浏览器中打开该网页，分别描述HTTP/1.0、HTTP/1.1（有持久连接但无管道）、HTTP/2和HTTP/3的请求过程及关键区别。

**解答**：HTTP/1.0——6个独立的TCP连接（每个请求-响应后关闭），6次三次握手+四次挥手，TCP慢启动使每个连接都从低窗口开始，效率低下。HTTP/1.1持久连接——浏览器一般开6个并行TCP连接（域名的并行连接上限），持续复用这些连接，先请求HTML，解析后陆续请求5张图片，每个连接的请求是串行的（HTTP/1.1无管道），多个连接并行加速。HTTP/2——仅需1个TCP连接，所有请求（HTML和5张图）以不同Stream交错发起，服务端可并行处理和响应，首包HTML的Stream先有数据返回解析，期间图片Stream已同时开始接收数据。HTTP/3——1个QUIC连接（基于UDP），与HTTP/2类似的Stream行为，但消除TCP队的头阻塞，且首次连接可0-RTT（若缓存了服务器配置）。

**例题2**：HTTP/2的二进制帧格式中，一个HTTP/2帧包含哪些字段？什么是PRIORITY和流量控制窗口（WINDOW_UPDATE）？

**解答思路**：HTTP/2帧格式：长度(24bit) + 类型(8bit) + 标志(8bit) + Stream ID(31bit) + 载荷。帧类型包括：DATA（传输HTTP体数据）、HEADERS（请求/响应头）、PRIORITY（设置Stream优先级和依赖关系）、RST_STREAM（终止Stream）、SETTINGS（连接级参数协商）、PUSH_PROMISE（服务器推送承诺）、PING（心跳/往返时间测量）、GOAWAY（优雅关闭）、WINDOW_UPDATE（流量控制窗口更新）、CONTINUATION（大型头部块的继续）。PRIORITY帧允许指定Stream之间的依赖树（如HTML的Stream先于图片Stream）和权重（分配带宽的权重）。HTTP/2在连接级和Stream级都实现了流量控制——WINDOW_UPDATE帧用于增减接收窗口大小避免接收方缓冲区溢出。

## 关联页面

[[应用层-HTTP]] [[应用层-HTTPS]] [[传输层-TCP首部]] [[传输层-UDP]] [[SSL-TLS]]
