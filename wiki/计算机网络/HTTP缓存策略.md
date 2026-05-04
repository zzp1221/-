---
title: "HTTP缓存策略详解"
course: 计算机网络
chapter: 应用层
difficulty: INTERMEDIATE
tags: [计算机网络, HTTP, 缓存, ETag, Cache-Control]
aliases: [HTTP Caching]
source: "RFC 9111 (HTTP Caching); MDN HTTP Caching文档"
updated_at: 2026-05-02
---

## 核心定义

HTTP缓存通过复用已有响应减少请求和延迟。浏览器缓存：强缓存(Cache-Control: max-age/Expires，不发送请求直接使用)→协商缓存(ETag/If-None-Match 或 Last-Modified/If-Modified-Since，带条件请求验证资源是否更新，304 Not Modified则用缓存)。Cache-Control指令：public/private、no-cache(协商)、no-store(不缓存)、s-maxage(共享缓存优先)、stale-while-revalidate(先给缓存后异步更新)。

## 关键结论

1. 强缓存优先于协商缓存 2. ETag比Last-Modified更精确（秒级精度不够）3. Webpack/CRA通过contenthash实现文件级别缓存失效 4. CDN缓存策略（遵循源站Cache-Control但可覆盖）

## 关联页面

[[HTTP协议基础]] [[CDN内容分发网络]] [[Web性能优化]]
