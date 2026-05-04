---
title: HTTP协议详解
course: 计算机网络
chapter: 应用层
difficulty: INTERMEDIATE
tags: [HTTP, 超文本传输协议, 请求方法, 状态码, 请求头, 响应头, Cookie, 缓存]
aliases: [Hypertext Transfer Protocol, HTTP Methods, HTTP Status Codes]
source:
  - 谢希仁《计算机网络》第8版
  - RFC 7230-7235, RFC 7540
updated_at: 2026-05-02

---

## 核心定义

HTTP（Hypertext Transfer Protocol，超文本传输协议）是万维网（World Wide Web）的核心应用层协议，定义了客户端（通常是浏览器）与Web服务器之间请求和响应数据的格式与交互规则。HTTP采用典型的客户端-服务器模型，基于TCP协议（端口80），遵循请求-响应的无状态通信模式。HTTP请求由请求行（方法+URL+版本）、请求头部（Host、User-Agent、Accept等）和可选的请求体（POST方法中的表单数据或JSON/XML载荷）组成；HTTP响应由状态行（版本+状态码+原因短语）、响应头部（Content-Type、Content-Length、Set-Cookie等）和响应体（HTML、图片、JSON等资源数据）组成。HTTP的设计简洁灵活、易于扩展，使其从最初的简单文档检索协议发展成为当今承载视频、API、实时通信等多元应用的基础性通用传输协议。

## 关键结论

- HTTP请求方法：GET（获取资源，幂等安全）、POST（提交数据创建资源，非幂等）、PUT（整体更新资源，幂等）、DELETE（删除资源，幂等）、HEAD（仅返回头部不返回体）、PATCH（部分更新）、OPTIONS（查询服务器支持的方法，CORS预检）、CONNECT（建立隧道）、TRACE（回显请求，用于诊断）
- HTTP状态码分类：1xx信息提示（100 Continue）、2xx成功（200 OK, 201 Created, 204 No Content）、3xx重定向（301永久移动, 302临时移动, 304 Not Modified, 307/308保留方法不变的重定向）、4xx客户端错误（400 Bad Request, 401 Unauthorized, 403 Forbidden, 404 Not Found, 405 Method Not Allowed, 429 Too Many Requests）、5xx服务器错误（500 Internal Server Error, 502 Bad Gateway, 503 Service Unavailable, 504 Gateway Timeout）
- HTTP的Cookie机制用于保持无状态HTTP的会话状态：服务器通过Set-Cookie响应头向客户端设置Cookie（包含name=value、Domain、Path、Expires/Max-Age、HttpOnly、Secure、SameSite等属性），后续请求中浏览器自动附加Cookie请求头。Cookie解决了HTTP无状态的固有局限，实现了用户登录会话、个性化偏好、跟踪分析等功能
- HTTP缓存机制：通过Cache-Control（no-cache, no-store, max-age, public/private）、ETag/If-None-Match（实体标签版本验证）、Last-Modified/If-Modified-Since（时间验证）、Expires等头部字段，HTTP实现了精细的缓存控制，减少网络传输和服务端负载。304 Not Modified响应是缓存验证的典型结果
- HTTP的内容协商：客户端通过Accept（媒体类型）、Accept-Language（语言）、Accept-Encoding（压缩算法）、Accept-Charset（字符集）头表达自己支持的内容格式偏好；服务器通过Content-Type、Content-Language、Content-Encoding等头告知实际使用的格式。Vary响应头指定了服务器在选择响应版本时参考了哪些请求头

## 易错点

1. **GET和POST的"安全性"和"幂等性"**：safe methods是指不修改服务器资源（GET/HEAD/OPTIONS），idempotent methods是指执行一次或多次效果相同（GET/PUT/DELETE）。POST不是安全的（创建资源）也不是幂等的（发两次POST可能创建两个资源）。这不是安全性(firewall)的概念，而是协议语义的定义。

2. **HTTP是无状态的，但Cookie和Session不等于"有状态"**：HTTP协议本身不保存对话状态——每个请求独立。Cookie和Session在应用层模拟了有状态的会话，但每次HTTP请求/响应仍然是独立的，只是利用Cookie中的Session ID在服务端查找恢复会话数据。协议层依然无状态。

3. **301和302的区别需要仔细理解**：301表示资源被永久移动到新的URL，搜索引擎会更新索引指向新URL；302表示临时移动，搜索引擎保留原URL。在实践中浏览器经常把302当成303（GET重定向，丢失原方法和请求体）来处理，因此有了307（临时重定向保持方法不变）和308（永久重定向保持方法不变）。

4. **HTTPS状态码和错误页面**：浏览器显示的"ERR_CERT_AUTHORITY_INVALID""ERR_CONNECTION_TIMED_OUT"等错误并非HTTP状态码，而是浏览器层面的网络错误。HTTP状态码只有从服务器返回的响应中才存在——连不上服务器就根本没有HTTP响应码。

## 例题

**例题1**：用户登录一个网站，服务器返回Set-Cookie: sessionid=abc123; HttpOnly; Secure; SameSite=Strict。说明这些Cookie属性的作用。

**解答**：sessionid=abc123是会话标识符；HttpOnly——禁止JavaScript通过document.cookie读取此Cookie，防止XSS攻击窃取Cookie；Secure——仅在HTTPS连接中传输此Cookie，防中间人拦截；SameSite=Strict——仅在从同一站点发起的请求中发送此Cookie，防止CSRF跨站请求伪造攻击（但可能导致从外部链接点击进入时Cookie丢失导致用户未登录）。

**例题2**：描述浏览器的HTTP缓存工作流程：用户第二次访问同一个URL。

**解答思路**：浏览器检查本地HTTP缓存中是否有该URL的缓存条目。如果有且未过期，则从缓存直接提供资源（"from disk cache"）。如果已过期，使用ETag（If-None-Match头）或Last-Modified（If-Modified-Since头）向服务器发送条件请求验证。服务器如果资源未改变，返回304 Not Modified（无响应体），浏览器刷新缓存中的过期条目继续使用缓存。如果资源已改变，服务器返回200 OK + 新资源+新缓存控制头部，浏览器缓存新资源。如果无缓存条目，直接发送GET请求获取资源并根据响应头的缓存策略（max-age等）决定是否缓存。

## 代码示例

```bash
# 使用curl测试HTTP请求
curl -v http://www.example.com                    # 详细输出
curl -I http://www.example.com                    # 仅响应头部
curl -X POST -d '{"key":"value"}' \
     -H 'Content-Type: application/json' \
     http://api.example.com/resource              # POST JSON数据
curl -o output.html http://www.example.com        # 保存到文件
curl -L http://short.link                         # 跟随重定向
```

```python
import http.server
import socketserver

# Python简易HTTP服务器
PORT = 8080
Handler = http.server.SimpleHTTPRequestHandler

# 启动服务器（当前目录作为文档根目录）
# with socketserver.TCPServer(("", PORT), Handler) as httpd:
#     print(f"HTTP服务器运行在端口 {PORT}")
#     httpd.serve_forever()

# 使用requests库发送HTTP请求
import requests

response = requests.get('http://www.example.com')
print(f"状态码: {response.status_code}")
print(f"Content-Type: {response.headers['Content-Type']}")
print(f"响应长度: {len(response.text)}")

# POST请求
resp = requests.post('http://httpbin.org/post',
                     json={'name': 'test', 'value': 123},
                     headers={'X-Custom': 'my-header'})
print(resp.json())
```

## 关联页面

[[应用层-HTTPS]] [[应用层-HTTP各版本对比]] [[应用层-DNS]] [[SSL-TLS]] [[TCP三次握手]]
