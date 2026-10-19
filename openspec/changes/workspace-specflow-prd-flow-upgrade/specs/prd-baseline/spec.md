# prd-baseline

取消 5 稿 / 9 稿，用一次确认加后续基线指针维护同一份需求。

## ADDED Requirements

### Requirement: 单一需求文档

系统 MUST 把一份飞书需求文档和对应的 `prd.md` 当作同一需求的持续文档，不再使用 v5/v9 稿次阶段。

#### Scenario: 新建需求没有稿次

- **WHEN** 产品创建新需求
- **THEN** `metadata` 不进入 `v5_pending`、`v5_confirmed`、`v9_pending`
- **AND** 飞书文档只有一份绑定

#### Scenario: 历史稿次可读

- **WHEN** 已有需求目录仍带 v5 或 v9 阶段字段
- **THEN** 读取时把已确认的 9 稿映射为 `prd.status=confirmed` 和最近一次快照
- **AND** 不要求重写历史飞书正文

### Requirement: 首次发布确认

系统 MUST 在第一次 `/prd-publish` 成功后把 `prd.status` 设为 `confirmed`。此后状态保持 `confirmed`。

#### Scenario: 第一次发布

- **WHEN** `prd.status` 不是 `confirmed` 且 `/prd-publish` 成功
- **THEN** 状态变为 `confirmed`
- **AND** 写入基线快照、飞书版本表新行，以及版本表写入完成之后回读到的 `revision_id`

#### Scenario: 再次发布

- **WHEN** `prd.status` 已是 `confirmed` 且 `/prd-publish` 再次成功
- **THEN** 状态仍是 `confirmed`
- **AND** 基线指针改为新快照、新版本表行和新的 `revision_id`

### Requirement: 漂移时下游读基线

除 `/qa-spec` 外，下游 MUST 在飞书当前 `revision_id` 不等于 `prd.baseline.revision_id`，或当前 `prd.md` 正文与基线快照不一致时，读取上一版基线快照。只多出版本表那一行不算不一致。

#### Scenario: 开发读取漂移中的需求

- **WHEN** 飞书当前 `revision_id` 不等于发布后回读的基线序号，或本地 `prd.md` 正文偏离快照
- **AND** 消费者不是 `/qa-spec`
- **THEN** 读取上一版基线快照
- **AND** 不把当前飞书正文或未发布的 `prd.md` 当作已发布需求

## REMOVED Requirements

### Requirement: 5 稿与 9 稿分阶段确认

**Reason**: 团队只维护一份飞书需求文档，稿次边界无法执行。
**Migration**: 首次发布即 `confirmed`；历史 v9 已确认文档映射为基线。
