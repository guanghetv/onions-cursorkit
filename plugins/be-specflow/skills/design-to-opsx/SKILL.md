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

**如果有需求层上下文**（由 `/dev-start` 传递，对话中包含 `requirement_ref` 路径和 `requirement_repo`）：
- 建议使用 `<requirement-id>-<repo-name>` 格式（如 `req-example-123-backend-api`）
- 这样可以在工作区内自动发现跨仓库的对方 spec

**无需求层上下文时**：保持原有方式。

示例：`add-invoice-export-api`、`fix-cart-checkout-webhook`、`req-example-123-backend-api`

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

从对话上下文提取设计结论，结构化写入。

**如果有需求层上下文**，在 proposal.md 顶部注入 YAML frontmatter：

```markdown
---
requirement_ref: requirements/<requirement>
requirement_repo: <specs-repo-name>
modules: [MODULE-1, MODULE-3]
---
```

- `requirement_ref`：指向 specs 仓库中的需求路径（两层连接点，决策 D3）
- `requirement_repo`：specs 仓库的逻辑名称（人类可读标识；specs 仓库自身不在注册表 JSON 的条目列表中，实际定位通过扫描 **`workspace-repos.json`（仓库根或 `scripts/`）** 与 `requirements/`，与 **`pull-spec`** / `references/workspace-native.md` 一致）
- `modules`：本次变更覆盖的 MODULE 列表（用于 `pull-spec` 的 MODULE 切片）

**无需求层上下文时**：不注入 frontmatter，保持原有格式。

proposal.md 正文结构：

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

### 步骤 6：回写 specs 仓库的 metadata.yaml（有需求层上下文时）

如果 proposal.md 中有 `requirement_ref` 和 `requirement_repo`：

1. 定位 specs 仓库：在多根工作区中查找 specs 根（含 `requirements/`），且可解析 **`workspace-repos.json`（仓库根或 `scripts/workspace-repos.json`）**（specs 仓库自身不在注册表 JSON 的条目列表中，它是包含该 JSON 的仓库；与 `references/workspace-native.md`「前置检查」一致）
2. 定位 `requirements/<requirement>/metadata.yaml`
3. 在 `changes` 字段中追加本次创建的 change 信息：
   ```yaml
   changes:
     - repo: <当前仓库逻辑名>
       change_id: <change-id>
       created_at: <YYYY-MM-DD>
   ```
4. 写入前确认 `metadata.yaml` 存在且 `prd.status` 为 `confirmed`

**无需求层上下文时**：跳过此步骤。

⚠️ 这是**唯一允许开发角色修改 `requirements/` 的场景**（决策 D33）。

### 步骤 7：可选 Spec Review

若 Superpowers 的 spec-document-reviewer 可用，派发 subagent 审阅 `design.md`、`plan.md`、`proposal.md`、`spec.md`。

### 步骤 8：用户确认

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
