---
name: design-to-opsx
description:
  当 Brainstorming 的设计被确认后，使用本技能将其固化到 OpenSpec 变更目录中。
  主要将 Brainstorming 的结论转化为 proposal.md 以及 specs/*/spec.md 文件。该技能由 dev-workflow 在设计审批后调用，用户无需直接使用。
---

# Brainstorming → OpenSpec 转场

将 Superpowers brainstorming 的设计结论写入 OpenSpec 变更目录。**不**在 `docs/superpowers/specs/` 产出任何文件。

## 前置条件

- Brainstorming 已完成，用户已确认设计方案
- 当前对话上下文中包含：Why、What Changes、API 契约、Capabilities、Impact

## 流程

### 步骤 1：确定 change-id

从设计结论中提取关键词，生成 kebab-case 动词开头的 change-id。

**如果有需求层上下文**（由 `/dev-start` 传递，对话中包含 `requirement_ref` 路径和 `requirement_repo`）：

- 建议使用 `<requirement-id>-<repo-name>` 格式（如 `req-example-123-frontend-app`）
- 这样可以在工作区内自动发现跨仓库的对方 spec

**无需求层上下文时**：保持原有方式。

示例：`add-invoice-export-ui`、`fix-cart-empty-state`、`req-example-123-frontend-app`

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

## API 契约（前端期望）

<!-- 从设计阶段产出的 API 契约；涉及接口改动且已拉 YApi 时写目标态，并注明相对 YApi 现状的变更 -->

### <接口名>

- YApi: <链接或 interfaceID；来自飞书时注明「飞书 §章节」>
- 变更类型: 新增 | 修改 | 废弃 | 不变
- 请求: <字段列表>
- 响应: <字段列表>
- 错误码: <错误码列表>
<!-- 新增且 YApi 尚无条目时: yapi_status: pending-create -->

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
- YApi 接口: <链接列表，每行一个；阶段 1 只读拉取过的 interfaceURL 或 interfaceID 对应页面>

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

### 步骤 5：回写 specs 仓库的 metadata.yaml（有需求层上下文时）

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

### 步骤 6：可选 Spec Review

如果 Superpowers 的 spec-document-reviewer 可用，派发 subagent 审阅 `proposal.md` + `spec.md`。审阅对象是 OpenSpec 格式文档，不是 Superpowers 格式。

### 步骤 7：用户确认

向用户展示已创建的文件清单和核心内容，等待确认后返回 `dev-workflow` 进入阶段 2。

## 产出物

```
openspec/changes/<change-id>/
├── proposal.md
└── specs/
    └── <capability-name>/
        └── spec.md
```
