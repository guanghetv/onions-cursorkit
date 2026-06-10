---
name: dev-start
description: >-
  Use when user mentions: 开始开发/dev-start/启动开发/开发这个需求/从需求开始。
  Triggers when prd.status is confirmed and developer wants to start coding.
---

# /dev-start — 读取需求并启动开发流程

## 前置条件

- `metadata.yaml` 中 `prd.status` 为 `confirmed`
- 测试 spec 不要求（开发不等测试 spec，决策 D7）

## 定位

轻量上下文准备 + 开发流程启动器。

**不创建需求层目录，不包含 brainstorming，不写入任何文件。**

## 权限约束

⛔ **严禁修改 requirements/ 下的任何文件**（决策 D33）。

## 流程

### Step 0: 确保 specs 仓库最新

提示用户在 specs 仓库目录执行 `git pull`，确保 `requirements/` 下的 prd.md 和 metadata.yaml 是团队最新版本。可通过 `git status` 检测是否 behind remote，若 behind 则**必须先提示 pull**。

### Step 1: 定位需求

**自动模式**：扫描 `requirements/` 下 `prd.status = confirmed` 的需求，列出供选择。
**手动模式**：用户直接指定路径。

读取完整的 `prd.md` 内容。

### Step 2: AI 扫描可能涉及的服务

基于 prd.md 内容，扫描 `workspace-repos.json` 中所有仓库。分析可能受影响的服务，分三级展示：

```
扫描结果：
  ✓ admin-web (前端)   — 管理端页面与交互直接相关
  ✓ order-api (后端)   — 订单与领域接口
  ? order-core         — 可能涉及核心领域模型
  ✗ analytics-service — 数据分析，本次不涉及
  ...
```

开发确认选择哪个项目，或补充遗漏的项目。

### Step 3: AI 匹配 MODULE

开发用自然语言描述本次迭代范围，例如：
- "做订单列表筛选的后端接口"
- "先做管理端列表页的前端改造"
- "全部都做"

AI 自动匹配 prd.md 中的 MODULE，展示匹配结果：

```
匹配结果：
  ✓ MODULE-1: 列表筛选增强 — 与「筛选」高度匹配
  ? MODULE-2: 导出报表     — 可能相关，请确认
```

开发确认。

### Step 4: 检测工作区

检测目标仓库是否在当前 Cursor 工作区中。

- **已在工作区**：直接继续
- **不在工作区**：提示建议操作

### Step 5: 启动开发流程

在同一会话中切换到目标仓库上下文：

1. 将以下信息作为上下文传递给开发流程：
   - prd.md 全文（已读取）
   - 匹配的 MODULE 列表
   - 需求层路径（`requirements/<requirement>/`）
   - specs 仓库逻辑名称
   - specs 仓库的工作区根路径（`/dev-start` 运行于 specs 仓库内，可直接获取当前仓库根路径；用于后续读取测试 spec）

2. 开发流程检测到上下文中有需求层信息 → 跳过"询问需求来源" → 直接进入 brainstorming

3. 后续流程完全由目标仓库内的开发流程接管

## 多仓库场景

如需为多个仓库并行开发：在不同会话中分别执行 `/dev-start`。

## 约束

- **不写入任何文件**
- **不创建需求层目录**
- **不做 brainstorming**（由后续开发流程负责）
- **禁止修改 requirements/**（决策 D33）
