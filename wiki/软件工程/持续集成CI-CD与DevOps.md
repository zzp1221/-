---
title: "CI/CD持续集成与持续交付"
course: 软件工程
chapter: 软件开发过程
difficulty: INTERMEDIATE
tags: [软件工程, CI/CD, DevOps, 自动化, 部署]
aliases: [Continuous Integration, Continuous Delivery]
source: "Continuous Delivery (Humble & Farley); DevOps Handbook; GitHub Actions/Jenkins文档"
updated_at: 2026-05-02
---

## 核心定义

CI/CD管道(Pipeline)：代码提交→构建→静态分析(lint/SAST)→单元测试→集成测试→构建镜像→部署到非生产环境→验收测试→生产部署(CD或手动审批)。CI(持续集成)：频繁合并代码到主干，自动化构建+测试，快速反馈。CD(持续交付)：随时可通过一键部署到生产。CD(持续部署)：每次通过流水线的变更自动部署到生产。DevOps文化：打破开发-运维壁垒，自动化一切。

## 关键结论

1. Trunk-Based Development+Feature Flag替代长期分支 2. 蓝绿部署/金丝雀发布降低部署风险 3. IaC(基础设施即代码)是CI/CD的延伸(Terraform, Pulumi) 4. GitHub Actions/GitLab CI/Jenkins是主流CI/CD工具

## 关联页面

[[敏捷Scrum与Kanban]] [[版本控制与分支策略]] [[Docker容器技术]]
