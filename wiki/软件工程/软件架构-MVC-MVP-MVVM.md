---
title: 软件架构-MVC-MVP-MVVM
course: 软件工程
chapter: 软件架构
difficulty: INTERMEDIATE
tags: [软件架构, MVC, MVP, MVVM, 架构模式, 表现层模式, GUI架构]
aliases: [Model-View-Controller, Model-View-Presenter, Model-View-ViewModel]
source:
  - Martin Fowler《Patterns of Enterprise Application Architecture》
updated_at: 2026-05-02

---

## 核心定义

MVC、MVP、MVVM 是三种经典的表现层架构模式，用于将用户界面（UI）逻辑与业务逻辑分离，实现关注点分离（Separation of Concerns）和高可测试性。

**MVC**（Model-View-Controller），由 Trygve Reenskaug 于 1979 年为 Smalltalk 设计，是最早的 GUI 架构模式。(a) **Model**：管理应用程序的数据和业务逻辑，独立于 UI。Model 不依赖 View 或 Controller。(b) **View**：将 Model 的数据呈现给用户，负责 UI 渲染。View 观察 Model 变化并更新。(c) **Controller**：接收用户输入（键盘、鼠标），将其转换为对 Model 的操作或视图切换。Controller 充当中介——它不渲染 UI，不包含业务逻辑。

交互流程：用户操作 → Controller（处理输入）→ Model（更新数据）→ Model 通知 View（数据变化）→ View 重新渲染。MVC 中 View 和 Controller 都依赖 Model，但 View 和 Controller 之间通常解耦。

**MVP**（Model-View-Presenter）是 MVC 的变体，由 Taligent 公司在 1990 年代提出。(a) Model 与 MVC 中相同。(b) View 更"被动"——它仅定义接口（IView），所有 UI 逻辑移入 Presenter。(c) **Presenter** 承担了 MVC 中 Controller 和部分 View 的职责——它从 Model 获取数据，格式化后通过 IView 接口传递给 View。View 和 Presenter 通过接口双向通信。

MVP 的核心优势是**可测试性极高**——Presenter 不依赖具体 UI 框架，可纯代码单元测试。View 可通过 Mock IView 替代。

**MVVM**（Model-View-ViewModel），由 Microsoft 的 John Gossman 于 2005 年为 WPF 设计。(a) Model 同上。(b) **ViewModel** 是 View 的抽象——它暴露 Model 数据和命令，但不持有 View 引用。ViewModel 通过**数据绑定**（Data Binding）机制与 View 自动同步。(c) View 通过声明式绑定（如 XAML, Vue/React 的模板）与 ViewModel 关联，不需要手动更新 UI。

MVVM 的关键技术是响应式数据绑定（Reactive Data Binding）——ViewModel 的属性变化时，绑定系统自动更新 View；View 的用户输入自动写回 ViewModel。

## 关键结论

- MVC 是最古老、最基本的分离模式——Model 是核心，Controller 处理输入，View 渲染输出
- MVP 中 Presenter 是"中间人"，承担了 View 和 Model 之间的双向格式转换
- MVVM 依赖数据绑定框架（如 Vue, React, Angular, WPF），减少了样板代码
- 三者的共同目标：让 Model 独立于 UI，使业务逻辑不受 UI 技术变更影响
- Web 框架对照：Spring MVC（服务端 MVC）、Angular（MVVM + 依赖注入）、React + Redux（单向数据流的 MVVM 变体）
- MVVM 中 ViewModel 不应包含视图引用——这是与 Presenter 的关键区别

## 易错点

1. MVC 在 Web 与桌面应用中的差异：Web MVC 中 Controller 通常返回 View 名称和 Model 数据（如 Spring MVC）；桌面 MVC 中 View 观察 Model 变化主动更新
2. MVP 中 View 接口过臃：如果把所有 UI 控件的细节都写入 IView 接口会导致接口过大——应定义面向业务的方法而非 UI 控件操作
3. MVVM 数据绑定的过度使用——将复杂逻辑放入 XAML 绑定表达式使调试困难

## 例题

**例题1**：为"待办事项应用"设计 MVVM 架构。列出 Model、ViewModel、View 各自的职责。

**解答**：
- Model：`TodoItem`（task 文本、是否完成、创建日期），`TodoStore`（增删改查、持久化）
- ViewModel：`TodoListViewModel`（暴露可观察的 `todos[]`、当前过滤条件、`addTodo()`、`toggleTodo(id)`、`remainingCount` 计算属性）
- View（如 Vue/React 组件）：绑定 `todos[]` 到列表模板，绑定输入框到 `newTaskText`、按钮点击到 `addTodo()` 命令，通过 `v-for/v-if` 响应数据变化自动渲染

**例题2**：比较 MVC 和 MVP 架构中谁控制什么。

**解答**：
MVC：Controller 处理输入，Model 存储状态，View 读取 Model 并渲染。View 直接依赖 Model。用户输入流程：Controller → Model → View。
MVP：View 完全不接触 Model。用户操作 → View 通知 Presenter → Presenter 更新 Model → Presenter 通过 IView 更新 View。Presenter 是唯一的逻辑中心。

## 关联页面

[[微服务架构]] [[分层架构]] [[设计模式-观察者]] [[系统设计]]
