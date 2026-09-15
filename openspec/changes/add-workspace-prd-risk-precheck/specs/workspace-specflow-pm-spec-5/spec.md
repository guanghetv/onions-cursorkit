# Workspace Specflow PM Spec 5（风险预检门禁）

## MODIFIED Requirements

### Requirement: 5稿确认状态与快照

系统 SHALL 在 5稿确认时更新 metadata 并生成快照。**在写入快照与 v5 confirmed 之前，MUST 先完成产品需求风险预检且结论为规则预检通过。**

#### Scenario: 更新 v5 状态

- **WHEN** 用户确认 5稿 AI Review 通过 **且** 风险预检结论为规则预检通过
- **THEN** 系统设置 `prd.v5.status = confirmed`、`prd.v5.confirmed_at`、`prd.v5.snapshot`，`prd.stage = v5_confirmed`

#### Scenario: 版本表记录 5-n

- **WHEN** 5稿确认且风险预检已通过
- **THEN** 系统在第二章版本表追加 `5-n` 版本行，含快照路径引用

#### Scenario: Step 6 自动预检

- **WHEN** 用户在 `/pm-spec-5` Step 6 明确确认 5稿
- **THEN** 系统在写快照前调用与 `/prd-risk` 相同的预检
- **AND** 将报告写入 `prototypes/prd-risk-precheck.md`

#### Scenario: HIT 或待补硬阻断确认

- **WHEN** 自动预检结论为「需调整」或「待补信息」
- **THEN** 系统 MUST NOT 设置 `prd.v5.status = confirmed`
- **AND** MUST NOT 追加版本表行、MUST NOT 写入 `snapshots/prd-v5-*.md`
- **AND** 向用户展示报告路径与下一步（补信息 / 调整方案 / 例外申请包）
