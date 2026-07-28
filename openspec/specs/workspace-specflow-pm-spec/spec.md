# Workspace Specflow PM Spec (9稿) Specification

## Purpose

定义 `/pm-spec` 9稿定稿流程：交互评审后结构化增强、严格 AI Review、`prd.status = confirmed` 门禁与 v9 快照。
## Requirements
### Requirement: `/pm-spec` 升级为 9稿定稿流程

系统 SHALL 将 `/pm-spec` 定位为交互评审后的 9稿定稿技能，是 `prd.status = confirmed` 的唯一触发入口。

#### Scenario: 读取 v5 快照并输出差异

- **WHEN** 执行 `/pm-spec`（9稿）且存在 `snapshots/prd-v5-*.md`
- **THEN** 系统读取最新 v5 快照与当前 `prd.md`，输出 5→9 差异摘要供 brainstorming 确认

#### Scenario: 启动写入 v9_pending

- **WHEN** 执行 `/pm-spec` 且 `prd.status` 尚未为 `confirmed`
- **THEN** 系统在定位需求后将 `prd.stage` 设为 `v9_pending`（不等于 confirmed；供 sync/publish auto 与 C6 启用）

#### Scenario: 禁止残留待定标记

- **WHEN** 9稿结构化增强或 AI Review
- **THEN** 系统禁止 `prd.md` 中残留 `[待定]` 或 `[待交互确认]`；命中则 P0 阻断

#### Scenario: 9稿确认触发下游门禁

- **WHEN** `/pm-spec` 9稿确认通过
- **THEN** 系统设置 `prd.status = confirmed`，允许 `/qa-spec` 与代码仓库开发消费

### Requirement: PRD 输出需具备高可读性（强规则门禁）

系统 SHALL 输出「阅读友好 + 结构清晰」的 PRD，并将可读性作为 `confirmed` 前置质量门禁。

#### Scenario: 关键关注与回归范围锚点迁移

- **WHEN** `/pm-spec` 完成结构化增强
- **THEN** 关键关注写入 `### 3.3 关键关注`，回归范围写入 `### 3.4 回归范围`；不得仅出现在 AI Review 结论区

#### Scenario: 开发速览锚点迁移

- **WHEN** AI Review 需读取需求类型与影响范围
- **THEN** 从 `## 一、需求概述` 内嵌开发速览小表读取，而非独立 `## 开发速览` 章节

#### Scenario: MODULE 详情锚点迁移

- **WHEN** AI Review 定位 MODULE 问题
- **THEN** 位置锚点使用 `## 五、需求详情说明 / MODULE-N / 说明列` 或图示列

#### Scenario: 复杂流程 Mermaid 位置

- **WHEN** 需求命中复杂流程条件
- **THEN** Mermaid 流程图置于 `## 一、需求概述` 末尾，或变更 MODULE 的第五章说明列（迭代+模块级影响时）

### Requirement: MODULE 结构对齐飞书第五章

系统 SHALL 使用飞书 3 列表格表达 MODULE 详情，保留 `MODULE-N` 稳定锚点。

#### Scenario: MODULE 节标题规范

- **WHEN** 生成第五章 MODULE 节
- **THEN** 使用 `### MODULE-N: <模块名> [新增/修改]` 标题，节内为单行 3 列表格

#### Scenario: 说明列结构

- **WHEN** 填写第五章说明列
- **THEN** 采用飞书 1.a.b 结构：1.功能说明 / 2.交互说明 / 3.补充规则；9稿验收标准以 checklist 嵌入说明列或补充规则段

#### Scenario: MODULE 标签不决定评审范围

- **WHEN** MODULE 标题带 `[新增/修改]`
- **THEN** 评审范围仍由 `一、需求概述` 开发速览中的需求类型与 Step 3 本轮变更 MODULE 清单决定

### Requirement: 9稿确认快照与版本表

系统 SHALL 在 9稿 **push v9 与 consistency-check 均成功之后** 才生成 v9 快照并追加版本行。

#### Scenario: v9 快照与 metadata

- **WHEN** 9稿确认流程中 sync 与 check 均已成功
- **THEN** 系统复制 `prd.md` 至 `snapshots/prd-v9-<YYYY-MM-DD>.md`，更新 `prd.v9.status`、`prd.v9.snapshot`、`prd.stage = confirmed`

#### Scenario: 版本表记录 9-n

- **WHEN** 9稿 sync 与 check 均成功
- **THEN** 系统在第二章版本表追加 `9-n` 版本行（含 AI Review 结论摘要）

#### Scenario: 失败不落可开工快照

- **WHEN** v9 push 失败或 consistency-check 存在 critical
- **THEN** 系统不得追加暗示可开工的版本行、不得落 v9 快照、不得将 `prd.status` 设为 `confirmed`；`prd.stage` 保持 `v9_pending` 并标明 `push_failed` 或 `check_failed`

### Requirement: 轻量 metadata 扩展

系统 SHALL 扩展 metadata 以支持 5稿/9稿双阶段，同时保持轻量。

#### Scenario: metadata 字段范围

- **WHEN** 实现本变更
- **THEN** 仅新增 `prd.stage`、`prd.v5.*`、`prd.v9.*`；不新增复杂评审状态机或开发关联字段

#### Scenario: 向后兼容 confirmed 语义

- **WHEN** 下游技能检查 `prd.status`
- **THEN** `confirmed` 仍仅表示 9稿定稿；`/qa-spec` 与代码仓库开发流程以此为门禁（不再提供 `/dev-start`）

### Requirement: 9 稿确认时先同步飞书再落状态

系统 SHALL 在 `/pm-spec` 9 稿用户确认通过后、写入 `confirmed` / v9 快照之前，调用 `/prd-feishu-sync push --stage v9`。

#### Scenario: 确认后必推送

- **WHEN** 9 稿用户确认通过并进入收口
- **THEN** 系统先执行 v9 同步；成功后 `feishu.v9_synced` 为 true，再落快照与 `confirmed`

#### Scenario: 同步失败不得假装完成

- **WHEN** v9 同步失败
- **THEN** 系统不得向用户宣称飞书已是最新；不得 `confirmed`；须明确失败并给出重试命令（`/prd-publish` 或 `push --stage v9`）

### Requirement: 9 稿确认执行瘦身

系统 SHALL 在 9 稿结构化收口时移除本地讲解层正文，保留契约层与原型引用。

#### Scenario: 按语义移除讲解层

- **WHEN** 9 稿确认前本地仍含背景/价值章节正文（`narrative.*`，按标题关键词识别）
- **THEN** 系统将讲解内容保留在飞书侧（若不存在则提示补讲解），并从 `prd.md` 整节删除这些讲解小节（禁止「见飞书」指针；不得只靠展示序号判断）

### Requirement: confirmed 前一致性校验

系统 SHALL 在设置 `prd.status = confirmed` 之前执行 `/prd-consistency-check`（或等价经由 `/prd-publish`）。

#### Scenario: critical 阻断 confirmed

- **WHEN** 一致性校验存在 critical fail
- **THEN** 系统不得将 `prd.status` 设为 `confirmed`

