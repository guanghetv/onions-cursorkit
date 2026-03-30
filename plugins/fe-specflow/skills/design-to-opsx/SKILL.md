---
name: design-to-opsx
description: >-
  Use when brainstorming design is confirmed and needs to be persisted into
  OpenSpec change directory. Converts brainstorming conclusions into
  proposal.md + specs/*/spec.md. Called by dev-workflow after design approval,
  not directly by user.
---

# Brainstorming → OpenSpec 转场

将 Superpowers brainstorming 的设计结论写入 OpenSpec 变更目录。**不**在 `docs/superpowers/specs/` 产出任何文件。

## 前置条件

- Brainstorming 已完成，用户已确认设计方案
- 当前对话上下文中包含：Why、What Changes、API 契约、Capabilities、Impact

## 流程

### 步骤 1：确定 change-id

从设计结论中提取关键词，生成 kebab-case 动词开头的 change-id。

示例：`add-refund-detail-only-refund-pad`、`fix-agency-payment-display`

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

### 步骤 3：写入 proposal.md

从对话上下文提取设计结论，结构化写入：

```markdown
# <change-id>

## Why
<!-- 从 brainstorming 中提取问题背景与动机 -->

## What Changes
<!-- 从确认的方案中提取变更内容清单 -->

## API 契约（前端期望）
<!-- 从设计阶段产出的 API 契约 -->
### <接口名>
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
- **前端**: <影响描述>
- **依赖**: <依赖说明>

## References
- 需求文档: <飞书链接>

## Decisions
<!-- 记录 brainstorming 中已澄清的关键决策 -->

## 前端实现决策（灰区）

<!-- 来自步骤 1e 灰区讨论的结论，仅包含本次讨论中涉及的维度；若跳过了灰区讨论则删除此 section -->

### UI 状态
- 空状态：<决策描述>
- 加载态：<决策描述>
- 错误态：<决策描述>

### 交互行为
- 表单验证：<决策描述>
- 防重复提交：<决策描述>
- 数据更新策略：<决策描述>

### 数据展示
- 长文本处理：<决策描述>
- 分页策略：<决策描述>
- 数值格式：<决策描述>

<!-- 按实际涉及的维度裁剪，未讨论的维度不写入 -->
```

### 步骤 4：写入 specs/\*/spec.md

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

**灰区场景覆盖**：若步骤 1e 灰区讨论产出了决策，须将其中涉及 UI 状态（空状态、加载态、错误态）、交互边界（防重复、表单验证）等的决策转化为对应的 Scenario，确保灰区行为有可验证的规格。示例：

```markdown
#### Scenario: 退款列表空状态展示
- **WHEN** 用户进入退款列表页
- **AND** 该用户无任何退款记录
- **THEN** 展示空状态占位图与"暂无退款记录"文案
- **AND** 不展示分页组件
```

**注意**：spec.md 必须在 `specs/<capability-name>/spec.md` 路径下，不能直接放变更目录根。

### 步骤 5：可选 Spec Review

如果 Superpowers 的 spec-document-reviewer 可用，派发 subagent 审阅 `proposal.md` + `spec.md`。审阅对象是 OpenSpec 格式文档，不是 Superpowers 格式。

### 步骤 6：用户确认

向用户展示已创建的文件清单和核心内容，等待确认后返回 `dev-workflow` 进入阶段 2。

## 产出物

```
openspec/changes/<change-id>/
├── proposal.md
└── specs/
    └── <capability-name>/
        └── spec.md
```
