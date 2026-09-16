# Workspace Specflow PM Spec 5 (5稿) Specification

## Purpose

定义 `/pm-spec-5` 5稿流程：内审与交互评审前的 PRD 结构化增强、轻量 AI Review 与 v5 快照。
## Requirements
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
- **THEN** `prd.status` 保持 `pending`；`/qa-spec` 与代码仓库开发消费仍被阻断

### Requirement: 5稿确认状态与快照

系统 SHALL 在 5稿确认时更新 metadata 并生成快照。**写入快照与 v5 confirmed 之前，MUST 已有针对当前 5稿的风险预检；结论为「需调整」时 MUST NOT 确认。**

#### Scenario: 更新 v5 状态（通过）

- **WHEN** 用户确认 5稿 AI Review 通过 **且** 最新风险预检结论为「规则预检通过」
- **THEN** 系统设置 `prd.v5.status = confirmed`、`prd.v5.confirmed_at`、`prd.v5.snapshot`，`prd.stage = v5_confirmed`

#### Scenario: 更新 v5 状态（待补可确认）

- **WHEN** 用户确认 5稿 **且** 最新风险预检结论为「待补信息」
- **THEN** 系统 MAY 设置 confirmed 与快照（软提醒不阻断）
- **AND** 确认前 MUST 向用户展示待补清单与报告路径，并提示信息不完整

#### Scenario: 版本表记录 5-n

- **WHEN** 5稿确认且未被「需调整」硬阻断
- **THEN** 系统在第二章版本表追加 `5-n` 版本行，含快照路径引用

#### Scenario: Step 4.5 自动预检

- **WHEN** `/pm-spec-5` Step 4 已写出 5稿 `prd.md`
- **THEN** 系统在进入 Step 5 AI Review 之前调用与 `/prd-risk` 相同的预检
- **AND** 按结论更新 `prototypes/prd-risk-precheck.md`（含运行时间与结论历史）

#### Scenario: 无报告或结论过期不得当通过

- **WHEN** 用户确认 5稿，但不存在预检报告、读不到结论、或 `prd.md` 修改时间晚于上次预检
- **THEN** 系统 MUST 先执行与 `/prd-risk` 相同的预检
- **AND** MUST NOT 在预检完成前设置 `prd.v5.status = confirmed`

#### Scenario: 需调整硬阻断确认

- **WHEN** 最新预检结论为「需调整」
- **THEN** 系统 MUST NOT 设置 `prd.v5.status = confirmed`
- **AND** MUST NOT 追加版本表行、MUST NOT 写入 `snapshots/prd-v5-*.md`
- **AND** Agent MUST 显著展示报告路径与下一步（调整方案 / 例外申请包）

#### Scenario: AI Review 只展示预检结论

- **WHEN** 写入 `prototypes/ai-review-v5.md`
- **THEN** 须含「风险预检」小节，只写结论（通过 / 待补信息 / 需调整）与报告路径
- **AND** MUST NOT 内嵌规则原文、命中明细或调整要求全文

### Requirement: 5 稿确认后按门控同步

系统 SHALL 在 `/pm-spec-5` 确认后，仅当尚未完成 9 稿飞书同步时自动/引导同步飞书。

#### Scenario: 未 v9 时同步

- **WHEN** `/pm-spec-5` 确认通过且 `feishu.v9_synced` 为 false
- **THEN** 系统调用或明确引导 `/prd-feishu-sync push --stage v5`

#### Scenario: 已 v9 时跳过

- **WHEN** `/pm-spec-5` 确认通过且 `feishu.v9_synced` 为 true
- **THEN** 系统跳过默认同步，并提示仅在产品强制时使用 `push --stage v5 --force`

