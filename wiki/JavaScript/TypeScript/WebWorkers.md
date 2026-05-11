---
title: "JavaScript-Web Workers与并行"
course: JavaScript/TypeScript
chapter: 并行与并发
difficulty: BASIC
tags: [JavaScript, Web Worker, 并行, postMessage, SharedArrayBuffer]
aliases: [Web Workers, Dedicated Worker, Service Worker]
source: "HTML Spec §Workers; MDN Web Workers API; Surma《The State of Web Workers》2023"
updated_at: 2026-05-02
---

## 核心定义

HTML Spec定义的Web Workers提供独立于主线程的JavaScript执行环境。const worker = new Worker('worker.js')创建专用Worker——有独立的全局对象(DedicatedWorkerGlobalScope，无window/document)、独立的事件循环、独立的内存堆。与主线程通过结构化克隆(structured clone)传递消息——postMessage(data, [transferList])。Transferable对象(ArrayBuffer/MessagePort/ImageBitmap)在转移后不可在发送端访问(zero-copy transfer)。SharedWorker让多个浏览上下文共享单一worker实例(通过port通信)。Service Worker是特殊的Worker——作为浏览器和网络之间的可编程代理(支持PWA的离线缓存、后台同步、推送通知)。Node.js的worker_threads提供类似能力。

## 关键结论

1.结构化克隆有性能成本——大数组应用Transferable(所有权转移)或SharedArrayBuffer+Atomics(共享内存) 2.Web Worker适用于：CPU密集型计算(图像处理/数据压缩/加解密)、后台数据预取、用户交互干扰隔离 3.Worker内部可用importScripts()同步加载脚本——现在推荐import声明(ES模块Worker: new Worker('w.js',{type:'module'})) 4.错误处理：Worker内部onerror事件+主线程worker.onerror/worker.onmessageerror 5.限制：不能访问DOM/localStorage(用IndexedDB替代)/cookie(可通过CookieStore API) 6.OffscreenCanvas+Worker：允许在Worker线程渲染Canvas——游戏/数据可视化场景 7.Comlink库(Google Chrome Labs): 将postMessage抽象为RPC调用——Comlink.wrap(worker)

## 关联知识点

[[JavaScript-事件循环与Job Queue]] [[JavaScript-内存管理与内存泄漏]] [[Python深入-GIL与并发编程]]
