# Workspace Specflow PM Spec 5 (5稿)

## ADDED Requirements

### Requirement: `/pm-spec-5` 5稿结构化增强

系统 SHALL 提供 `/pm-spec-5` 技能，用于内审与交互评审会前的 PRD 结构化增强。

#### Scenario: 前置 brainstorming 门禁

- **WHEN** 执行 `/pm-spec-5`
- **THEN** 系统须先 Read 并遵循 `superpowers:brainstorming`，完成 MODULE 初拆与灰区澄清，用户明确放行后才可改写 `prd.md`

#### Scenario: 飞书章节映射拉取

- **WHEN** `prd.md` 为空且存在 `metadata.feishu_doc`
- **THEN** 系统使用 `lark-cli docs +fetch` 按 h2 标题（一~七）映射回填；本地有实质内容时本地优先

#### Scenario: 允许待定标记

- **WHEN** 5稿阶段方案尚未确定
- **THEN** 系统允许在第五章说明列使用 `[待定]` 或 `[待交互确认]` 标记

#### Scenario: 3.3 可含开放问题

- **WHEN** 5稿输出 `### 3.3 关键关注`
- **THEN** 允许包含待交互评审决议的开放问题

#### Scenario: 5稿确认后活跃稿可手工修改

- **WHEN** `/pm-spec-5` 确认通过
- **THEN** `prd.md` 不锁定；产品可在交互评审会中直接手工修改

### Requirement: 5稿轻量 AI Review

系统 SHALL 对 5稿执行轻量 AI Review，结论面向交互评审而非开发开工。

#### Scenario: 5稿评审结论措辞

- **WHEN** 5稿 AI Review 完成
- **THEN** 结论为「可进入交互评审 / 建议补充后进入交互评审 / 暂不建议进入交互评审」三者之一

#### Scenario: 5稿评审记录外置

- **WHEN** 5稿 AI Review 完成
- **THEN** 详细记录写入 `prototypes/ai-review-v5.md`，`prd.md` 仅保留结论性信息

#### Scenario: 5稿不触发下游开工门禁

- **WHEN** 仅 `/pm-spec-5` 确认通过
- **THEN** `prd.status` 保持 `pending`；`/qa-spec` 与 `/dev-start` 仍被阻断

### Requirement: 5稿确认状态与快照

系统 SHALL 在 5稿确认时更新 metadata 并生成快照。

#### Scenario: 更新 v5 状态

- **WHEN** 用户确认 5稿 AI Review 通过
- **THEN** 系统设置 `prd.v5.status = confirmed`、`prd.v5.confirmed_at`、`prd.v5.snapshot`，`prd.stage = v5_confirmed`

#### Scenario: 版本表记录 5-n

- **WHEN** 5稿确认
- **THEN** 系统在第二章版本表追加 `5-n` 版本行，含快照路径引用
