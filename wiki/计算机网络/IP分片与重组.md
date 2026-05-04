---
title: "IP分片与重组"
course: 计算机网络
chapter: 网络层
difficulty: INTERMEDIATE
tags: [计算机网络, IP, 分片, MTU, 路径MTU发现]
aliases: [IP Fragmentation]
source: "RFC 791 (IPv4); RFC 8200 (IPv6); TCP/IP Illustrated (Stevens) 第11章"
updated_at: 2026-05-02
---

## 核心定义

当IP数据报大于链路MTU时需要分片。IPv4分片可在源主机和中间路由器进行，通过Identification标识同一数据报、Flags(DF禁止分片/MF更多分片)、Fragment Offset(偏移量以8字节为单位)。到达目的主机后根据这些字段重组。IPv6禁止中间路由器分片，源主机通过Path MTU Discovery确定最小MTU。

## 关键结论

1. 分片降低效率（丢失一个分片整个数据报重传）2. 通常设置DF=1配合Path MTU Discovery避免分片 3. PMTUD通过ICMP 'Fragmentation Needed'消息探测 4. TCP MSS协商可避免IP层分片

## 关联页面

[[IP协议基础]] [[IPv4与IPv6]] [[ICMP协议]]
