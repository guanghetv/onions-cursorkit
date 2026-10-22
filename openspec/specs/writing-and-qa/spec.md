# writing-and-qa Specification

## Purpose
TBD - created by archiving change workspace-specflow-prd-flow-upgrade. Update Purpose after archive.
## Requirements
### Requirement: 不单设验收章

系统 MUST 按《产品组 PRD 写作规范》生成飞书正文和 `prd.md`，不单设验收章节。

#### Scenario: 生成需求详情

- **WHEN** Agent 写入需求详情
- **THEN** 规则、状态和异常写在对应模块
- **AND** 正文没有独立验收章节或把同一规则再写一遍的验收清单

#### Scenario: /prd-check

- **WHEN** `/prd-check` 检查文档，且缺少旧模板要求的验收 checklist，但需求详情中的规则可判断
- **THEN** 不因此判定失败

### Requirement: 测试从需求详情提取

`/qa-spec` MUST 从需求详情中的规则、状态和异常提取可测点。

#### Scenario: 读取 prd.md

- **WHEN** 用户对已有 `prd.md` 执行 `/qa-spec`
- **THEN** 用例来自需求详情中的可判断规则
- **AND** 不依赖单独验收章节

### Requirement: 飞书链接可作为输入

`/qa-spec` MUST 能用飞书 CLI 读取用户给出的飞书需求文档链接。

#### Scenario: revision 与基线一致

- **WHEN** 用户给出飞书链接
- **AND** 当前 `revision_id` 等于 `prd.baseline.revision_id`
- **AND** 本地 `prd.md` 正文与基线快照一致
- **THEN** 按当前正文生成测试用例

#### Scenario: 有本地快照且正文已漂移

- **WHEN** 存在上一版基线快照
- **AND** 飞书序号不等于基线，或本地 `prd.md` 正文偏离快照
- **THEN** 用例按该快照生成
- **AND** 结果提示正文已超前

### Requirement: 测试生成不被门禁阻断

`/qa-spec` MUST 在未确认、一致性失败、无基线或正文已漂移时仍生成用例，并给出风险提示。本条只放宽 `/qa-spec`。

#### Scenario: 没有基线

- **WHEN** 没有本地基线快照，或需求尚未第一次发布
- **THEN** 仍按当前可读正文生成用例
- **AND** 提示内容可能含未发布改动，建议先 `/prd-publish`

#### Scenario: 其他下游

- **WHEN** 消费者不是 `/qa-spec` 且需求尚未第一次发布成功
- **THEN** 仍不得把该需求当作已确认需求消费

#### Scenario: 用例状态看来源

- **WHEN** `/qa-spec` 写完 `test/test-spec.md`
- **AND** 来源已发布、未漂移，且 `consistency.status` 为 `pass` 或 `warn`
- **THEN** `test_spec.status` 为 `confirmed`
- **AND** 来源未发布、已漂移，或一致性为 `fail`、缺失、`unknown` 时，文件仍写入，状态为 `pending`

