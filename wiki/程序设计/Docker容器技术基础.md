---
title: "Docker容器技术原理"
course: 程序设计
chapter: 云原生
difficulty: INTERMEDIATE
tags: [Docker, 容器, 镜像, Container, 虚拟化]
aliases: [Docker]
source: "Docker官方文档; Understanding Docker (Nigel Poulton); Docker in Practice"
updated_at: 2026-05-02
---

## 核心定义

Docker容器是轻量级、可移植的软件运行环境。核心概念：镜像(Image)——分层的只读文件系统(Union FS/Overlay2)，每层是Dockerfile的一个指令。容器(Container)——镜像的可运行实例+可写容器层。Dockerfile指令：FROM继承基础镜像、RUN执行命令(在构建时创建新层)、COPY/ADD复制文件、CMD/ENTRYPOINT定义启动命令、EXPOSE声明端口。多阶段构建(Multi-stage Build)分离构建环境和运行环境减小镜像体积。

## 关键结论

1. 容器不是虚拟机(共享宿主机内核，通过namespace隔离) 2. 镜像分层→相同基础层的多个镜像共享存储 3. .dockerignore和层缓存策略加速构建 4. Distroless镜像+非root用户是最小化攻击面的实践

## 关联页面

[[Cgroups与容器资源隔离]] [[虚拟化技术对比]] [[CI/CD]]
