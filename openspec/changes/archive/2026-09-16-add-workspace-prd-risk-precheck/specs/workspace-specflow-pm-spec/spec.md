# Workspace Specflow PM Spec（9稿风险预检）

## ADDED Requirements

### Requirement: 9稿写出后预检与确认门禁

系统 MUST 在 `/pm-spec` 写出 9稿后、AI Review 前执行与 `/prd-risk` 相同的预检。确认 `prd.status=confirmed` 时采用与 5稿相同的方案 C，且无报告或结论过期时必须先预检。

#### Scenario: Step 4.5 自动预检

- **WHEN** `/pm-spec` Step 4 已写出并完成瘦身
- **THEN** 在进入 Step 5 之前调用预检并更新 `prototypes/prd-risk-precheck.md`

#### Scenario: 需调整禁止 9稿 confirmed

- **WHEN** 最新预检结论为「需调整」
- **THEN** MUST NOT 设置 `prd.status = confirmed`，MUST NOT 写入 `snapshots/prd-v9-*.md`

#### Scenario: 无报告必须先预检

- **WHEN** 用户确认 9稿但无报告、结论不可读、或 `prd.md` 已晚于 `last_checked_at`
- **THEN** 必须先执行预检，不得把缺失当成通过
