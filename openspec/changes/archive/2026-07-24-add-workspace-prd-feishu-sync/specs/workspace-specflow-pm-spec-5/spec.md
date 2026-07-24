# Workspace Specflow PM Spec 5 Delta

挂接 5 稿飞书同步与 v9 后门控。

## ADDED Requirements

### Requirement: 5 稿确认后按门控同步

系统 SHALL 在 `/pm-spec-5` 确认后，仅当尚未完成 9 稿飞书同步时自动/引导同步飞书。

#### Scenario: 未 v9 时同步

- **WHEN** `/pm-spec-5` 确认通过且 `feishu.v9_synced` 为 false
- **THEN** 系统调用或明确引导 `/prd-feishu-sync push --stage v5`

#### Scenario: 已 v9 时跳过

- **WHEN** `/pm-spec-5` 确认通过且 `feishu.v9_synced` 为 true
- **THEN** 系统跳过默认同步，并提示仅在产品强制时使用 `push --stage v5 --force`
