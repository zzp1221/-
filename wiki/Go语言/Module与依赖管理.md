---
title: "Go语言-Module与依赖管理"
course: Go语言
chapter: 工程构建
difficulty: BASIC
tags: [Go语言, go.mod, modules, 依赖管理, GOPROXY]
aliases: [Go Modules, Semantic Import Versioning, GOPROXY]
source: "Go官方文档 Modules; Go Blog: Using Go Modules; Go Wiki: Modules"
updated_at: 2026-05-02
---

## 核心定义

""Go Modules是Go 1.11引入的依赖管理系统(Go 1.16后默认启用)。模块由go.mod文件定义：module声明模块路径,go声明Go版本,require列出直接依赖,replace(gomod补丁),exclude(排除版本)。语义化导入版本(semantic import versioning)：大版本号>=2时路径必须包含/vN后缀(github.com/foo/bar/v2)。

## 最小版本选择MVS

""Go使用最小版本选择(Minimal Version Selection, MVS)而非SAT求解器。MVS规则：选择所有require中出现的最低符合版本。当存在多个依赖不同版本时，选择最高者(保守升版)。go.sum文件保存所有依赖内容的哈希值确保可重现构建。GOPROXY(如goproxy.cn)缓存模块下载加速。GONOSUMDB跳过私有模块校验。

## 关键结论

""1. go mod tidy清理未使用的依赖并添加缺失的 2. go mod vendor创建vendor目录做离线构建 3. semantic import versioning >v2时必须更改import路径 4. 使用replace指令替代fork 5. go clean -modcache清理mod缓存

## 关联知识点

""[[Go语言-编译与链接过程]] [[软件工程-版本控制与Git]] [[Rust语言-cargo与依赖管理]]
