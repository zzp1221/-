---
title: 持续集成CI-CD与DevOps实践
course: 软件工程
chapter: 敏捷开发
difficulty: INTERMEDIATE
tags: [持续集成, CI/CD, DevOps, Jenkins, 自动化部署, 流水线, 基础设施即代码]
aliases: [Continuous Integration, Continuous Delivery, CI/CD Pipeline]
source:
  - Jez Humble & David Farley《Continuous Delivery》
  - Gene Kim et al.《The Phoenix Project》《The DevOps Handbook》
updated_at: 2026-05-02

---

## 核心定义

**持续集成**（CI, Continuous Integration）是一种软件开发实践：团队成员频繁（每日多次）将代码变更合并到主干，每次合并触发自动化构建和测试，以尽早发现集成问题。CI 的核心原则：(a) 所有代码在版本控制仓库中；(b) 每次提交触发自动化构建；(c) 构建包括编译和单元测试；(d) 构建失败立即修复——"失败构建是最高优先级"。CI 服务器工具：Jenkins、GitHub Actions、GitLab CI、CircleCI、Travis CI。

**持续交付**（CD, Continuous Delivery）在 CI 基础上扩展：每次构建通过自动化测试后，代码处于**随时可部署到生产环境**的状态（但部署按钮由人工触发的）。持续交付要求完整的自动化测试套件（单元、集成、API、性能）和部署流水线（Deployment Pipeline）。

**持续部署**（Continuous Deployment）更进一步——通过流水线所有阶段的代码自动部署到生产环境，无需人工批准。Pinterest、Netflix 等高科技公司每天部署数百次。

CI/CD 流水线（Pipeline）的典型阶段：代码提交 → 编译 → 单元测试 → 代码质量检查（SonarQube/Lint）→ 集成测试 → 构建镜像（Docker）→ 部署到测试环境 → API/UI 自动化测试 → 性能测试 → 部署到预发/灰度环境 → 审批门 → 部署到生产 → 监控告警。

**DevOps**（Development + Operations）是打破开发（Dev）和运维（Ops）之间隔阂的文化运动，通过自动化工具链实现快速、高频、高可靠的软件交付。CALMS 框架：Culture（文化）、Automation（自动化）、Lean（精益）、Measurement（度量）、Sharing（共享）。DevOps 的关键技术实践：CI/CD、基础设施即代码（IaC, Terraform/Ansible）、容器化（Docker/Kubernetes）、可观测性（Observability：监控/日志/追踪 Prometheus + Grafana + ELK + Jaeger）、混沌工程（Chaos Engineering）。

## 关键结论

- CI 使得集成不再是一场"大爆炸"的噩梦
- CD 要求"主干始终处于可发布状态"
- Webhook 和事件驱动触发是 CI/CD 的自动化引擎
- 蓝绿部署（Blue-Green）和金丝雀发布（Canary Release）降低了部署风险
- IaC 使基础设施的变更可审查、可版本化、可重复——"像对待代码一样对待基础设施"
- DevOps 不是工具也不是职位（虽然后来出现了 DevOps Engineer），而是一种协作文化

## 易错点

1. 将 CI 简单等同于"装一个 Jenkins"：CI 的核心是**团队频繁集成**的纪律，工具只是支撑
2. CI 构建时间过长：若构建+测试耗时超过 10-15 分钟，团队集成的频率会下降——应优化慢测试、并行执行
3. DevOps 转型中忽视文化变革——引入工具但没有改变"开发和运维各自为政"的组织结构，转型流于表面

## 例题

**例题1**：设计一个基于 GitHub Actions 的 CI/CD 流水线。

**解答**：
```yaml
name: CI/CD Pipeline
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - run: npm install && npm test
      - run: npm run lint
  build-and-deploy:
    needs: test
    if: github.ref == 'refs/heads/main'
    steps:
      - run: docker build -t myapp .
      - run: docker push myregistry/myapp
      - run: kubectl apply -f deployment.yaml
```
该流水线在每次 push 和 PR 时运行测试和 lint；合并到 main 时自动构建镜像并部署到 Kubernetes。

**例题2**：解释"主干始终处于可发布状态"意味着什么，实践中怎么做到。

**解答**：意味着在任何时刻，主干的 HEAD 都应该能够被安全地部署到生产环境——没有未完成的功能、没有"还在修"的 bug。实践中：(a) 功能通过 Feature Flag 控制可见性（未完成功能隐藏在 Flag 后）；(b) 小变更高频集成（每天至少一次）；(c) Feature Branch 生命周期短（不超过 1-2 天）；(d) 全面的自动化测试提供了安全网；(e) 如果主干的构建失败，团队停止一切新开发优先修复。

## 关联页面

[[版本控制与分支策略]] [[敏捷开发]] [[软件开发全生命周期]]
