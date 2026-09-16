# Workspace Specflow PM Spec 5（风险预检门禁）

## MODIFIED Requirements

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
