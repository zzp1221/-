---
title: "Go语言-网络编程net/http"
course: Go语言
chapter: 网络编程
difficulty: INTERMEDIATE
tags: [Go语言, net/http, HTTP/2, 中间件, ServeMux]
aliases: [Go HTTP, net/http, Middleware]
source: "Go标准库net/http文档; RFC 7540 (HTTP/2); Go Blog: HTTP/2 in Go"
updated_at: 2026-05-02
---

## 核心定义

""Go的net/http包提供生产级HTTP客户端和服务器实现。Server结构体包含Handler字段(接口,含ServeHTTP方法)。DefaultServeMux是全局路由,可通过http.HandleFunc注册。http.HandlerFunc(f)将普通函数适配为Handler。http.ListenAndServe(':8080', nil)使用DefaultServeMux启动服务器。http.Transport管理连接池和HTTP/2多路复用。

## 中间件模式

""Go的HTTP中间件通过Handler包装实现：func middleware(next http.Handler) http.Handler。常见模式：logMiddleware→authMiddleware→rateLimitMiddleware→actualHandler。http.TimeoutHandler包装超时控制。第三方库如chi/gorilla/mux提供更灵活的路由。http/httputil.ReverseProxy提供反向代理能力。Go 1.22的新ServeMux支持方法路由和方法变量。

## 关键结论

""1. 默认HTTP服务器不支持优雅关闭——需shutdown context 2. http.Client不设置Timeout可能导致goroutine泄漏 3. Response.Body必须关闭 4. 生产环境建议使用http.Server结构体而非http.ListenAndServe快捷函数

## 关联知识点

""[[Go语言-Context与取消传播]] [[计算机网络-HTTP协议与HTTPS]] [[Go语言-错误处理哲学]]
