---
title: "HTTP状态码全览"
course: 计算机网络
chapter: 应用层
difficulty: BASIC
tags: [计算机网络, HTTP, 状态码, REST]
aliases: [HTTP Status Codes]
source: "RFC 9110 (HTTP Semantics); MDN HTTP Status Codes"
updated_at: 2026-05-02
---

## 核心定义

HTTP状态码分五类：1xx信息(100 Continue, 101 Switching Protocols)。2xx成功：200 OK、201 Created、204 No Content、206 Partial Content(断点续传)。3xx重定向：301永久、302临时、304 Not Modified(协商缓存)、307临时(保持方法)、308永久(保持方法)。4xx客户端错误：400 Bad Request、401 Unauthorized、403 Forbidden、404 Not Found、405 Method Not Allowed、429 Too Many Requests。5xx服务端错误：500 Internal Server Error、502 Bad Gateway、503 Service Unavailable、504 Gateway Timeout。

## 关键结论

1. 301 vs 302: SEO影响（301转移权重，302不转移）2. 401(未认证)vs 403(已认证但无权限) 3. 503应带Retry-After头 4. RESTful API设计应正确使用状态码

## 关联页面

[[HTTP协议基础]] [[RESTful API设计]] [[HTTPS安全超文本传输协议]]
