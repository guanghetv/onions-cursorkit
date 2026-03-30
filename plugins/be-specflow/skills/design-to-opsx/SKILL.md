---
name: design-to-opsx
description: >-
  Use when brainstorming design is confirmed and needs to be persisted into
  OpenSpec change directory. Writes design.md + plan.md (templates below)
  plus proposal.md + specs/*/spec.md. Called by dev-workflow after design
  approval, not directly by user.
---

# Brainstorming → OpenSpec 转场

将 Superpowers brainstorming 的设计结论写入 OpenSpec 变更目录。**不**在 `docs/superpowers/specs/` 产出任何文件。

与 **`dev-workflow`** 内嵌**「OpenSpec + Superpowers 强制纪律」**对齐：变更目录内除 `proposal.md`、`specs/**/spec.md`、`tasks.md` 外，还须包含 **`design.md`** 与 **`plan.md`**（模板见下文「阶段 1.5 模板」；制品确认卡点见该纪律阶段 2.3）。

## 前置条件

- Brainstorming 已完成，用户已确认设计方案
- 当前对话上下文中包含：Why、What Changes、**服务端 API 契约**、Capabilities、Impact、**后端灰区决策**（若未跳过）

## 流程

### 步骤 1：确定 change-id

从设计结论中提取关键词，生成 kebab-case 动词开头的 change-id。

示例：`add-refund-detail-api`、`fix-order-payment-webhook`

### 步骤 2：创建 OpenSpec 变更目录

**标准模式**（openspec CLI 已安装）：

提示用户在终端执行：
```bash
openspec new change "<change-id>"
```
等待用户确认执行完毕，通过 `ls openspec/changes/<change-id>/` 验证。

**降级模式**（CLI 未安装）：
```bash
mkdir -p openspec/changes/<change-id>/specs/<capability-name>/
```

### 步骤 3：写入 design.md 与 plan.md

#### 阶段 1.5 模板（须按此结构写入）

**`design.md`** — `openspec/changes/<change-id>/design.md`：

```markdown
# [接口名] 设计文档

## 澄清问题及结论
<!-- 记录 Brainstorming 中的关键问题和结论 -->

## 候选方案对比
<!-- 2-3 个方案，含优缺点和推荐理由 -->

## 最终选择及理由

## 技术设计
### 架构分层
### 关键决策
### 风险与约束
### Open Questions（供 Code Review 阶段补充）
```

**`plan.md`** — `openspec/changes/<change-id>/plan.md`：

```markdown
# [接口名] 实现计划

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** [一句话描述目标]

**Architecture:** [2-3 句描述方案]

**Tech Stack:** `<按仓库实际栈填写，如 Go (Kratos)、GORM、protobuf>`

---

### Task 1: [组件名]

**Files:**
- Create/Modify: `exact/path/to/file.go`

**Step 1: Write the failing test**
...

**Step 2: Run test to verify it fails**
...

**Step 3: Write minimal implementation**
...

**Step 4: Run test to verify it passes**
...

**Step 5: Commit**
...
```

> **注意**：brainstorming 与 writing-plans 的历史路径 `docs/plans/…` **不**再使用；设计文档**只**进 OpenSpec change 目录。`plan.md` 与 `tasks.md`：前者为**可执行计划叙述**，后者为 **OpenSpec 勾选清单**；须一致或可追踪，避免矛盾。

### 步骤 4：写入 proposal.md

从对话上下文提取设计结论，结构化写入：

```markdown
# <change-id>

## Why
<!-- 从 brainstorming 中提取问题背景与动机 -->

## What Changes
<!-- 从确认的方案中提取变更内容清单 -->

## API 契约（服务端对外）
<!-- 对外暴露的 HTTP/gRPC 等契约 -->
### <接口名或 RPC>
- 请求: <字段列表>
- 响应: <字段列表>
- 错误码: <错误码列表>

## Capabilities
### New Capabilities
- `<capability-name>`: <简述>

### Modified Capabilities
- （如有）

## Impact
- **后端**: <影响描述>
- **前端/调用方**: <影响描述>
- **依赖**: <依赖说明>

## References
- 需求文档: <飞书链接>
- 设计输入: <OpenAPI/proto 链接，如有>

## Decisions
<!-- 记录 brainstorming 与灰区中已澄清的关键决策 -->

## 后端实现决策（灰区）

<!-- 来自步骤 1e 灰区讨论的结论，仅包含本次讨论中涉及的维度；若跳过了灰区讨论则删除此 section -->

### API 与兼容性
- 版本与 breaking change：<决策描述>

### 数据与一致性
- 事务与幂等：<决策描述>

### 安全与权限
- 鉴权与鉴权粒度：<决策描述>

### 可观测性
- 日志与 trace：<决策描述>

<!-- 按实际涉及的维度裁剪 -->
```

### 步骤 5：写入 specs/\*/spec.md

将设计中的行为规格转化为 OpenSpec Scenario 格式：

```markdown
# <capability-name>

<一段概述>

## ADDED Requirements

### Requirement: <行为描述>

<详细说明，使用 SHALL / MUST / MUST NOT>

#### Scenario: <场景名>

- **WHEN** <前置条件>
- **AND** <附加条件>（如有）
- **THEN** <期望行为>
- **AND** <附加期望>（如有）
```

**灰区场景覆盖**：若步骤 1e 产出了决策，须将其中涉及 API 幂等、错误码、分页、事务边界等转化为可验证 Scenario。

**注意**：spec.md 必须在 `specs/<capability-name>/spec.md` 路径下，不能直接放变更目录根。

### 步骤 6：可选 Spec Review

若 Superpowers 的 spec-document-reviewer 可用，派发 subagent 审阅 `design.md`、`plan.md`、`proposal.md`、`spec.md`。

### 步骤 7：用户确认

向用户展示已创建的文件清单和核心内容，等待确认后返回 `dev-workflow` 进入阶段 2（任务规划）。

**与 `dev-workflow` 强制纪律阶段 2.3 对齐**：**制品人工确认**不可跳过。本步骤结束时须确认 **`proposal` / `spec` / `design` / `plan`**；**`tasks.md` 在阶段 2 创建后**须再经 **2.3 第二轮**（或合并轮次）确认，**全部确认完毕后**方可进入实现（阶段 3）。

## 产出物

```
openspec/changes/<change-id>/
├── design.md
├── plan.md
├── proposal.md
└── specs/
    └── <capability-name>/
        └── spec.md
```

`tasks.md` 在阶段 2 由 `openspec instructions` 或 Agent 按 **`dev-workflow`** 强制纪律**阶段 2** 创建。
