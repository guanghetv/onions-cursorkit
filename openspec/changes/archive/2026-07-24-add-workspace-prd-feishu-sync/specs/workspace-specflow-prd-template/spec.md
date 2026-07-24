# Workspace Specflow PRD Template (Delta)

调整 9 稿本地契约子集；飞书七章产品模板保持不变。章节定位 **语义 unit + 标题关键词优先，序号仅兼容**。

## MODIFIED Requirements

### Requirement: PRD 章节对齐飞书标准模板

系统 SHALL 使飞书侧 PRD 继续对齐飞书七章产品模板；本地 `prd.md` 在 5 稿阶段可对齐全章，在 **9 稿确认后**仅保留契约层子集。讲解层以 `narrative.background` / `narrative.value`（标题含「背景」「价值」）识别，不得再作为 Agent 输入保留在本地。

#### Scenario: 飞书仍为七章产品模板

- **WHEN** `/prd-feishu-sync create` 或产品在飞书维护讲解内容
- **THEN** 飞书文档可包含完整七章（含背景/价值讲解），不要求删减飞书产品模板

#### Scenario: 9 稿本地瘦身且不重排序号

- **WHEN** `/pm-spec` 完成 9 稿确认
- **THEN** 本地须按语义删除全部 `narrative.*` 小节（禁止「见飞书」指针）；须保留概述、版本、关键关注、回归、Feature、详情 MODULE 等契约 unit
- **AND** 系统不得为补洞改写契约小节展示序号或前移四～七（与 sync unit key 对齐）

#### Scenario: 5 稿仍可含背景

- **WHEN** 需求仍处于 5 稿阶段
- **THEN** 本地允许含讲解层背景/价值，便于同步前整理；升 9 稿时迁出到飞书并从 md 按语义删除

#### Scenario: 章节按语义定位

- **WHEN** sync / check / 瘦身需要定位「背景」「关键关注」等小节
- **THEN** 须按 unit key + 标题关键词匹配；不得将「标题里的 3.1」作为唯一判据

#### Scenario: 原型属于契约层

- **WHEN** 需求包含 UI 原型
- **THEN** 9 稿瘦身不得移除 `prototypes/` 引用与 MODULE 锚点；无原型时须写明「无原型（原因）」

## ADDED Requirements

### Requirement: 讲解层归属飞书

系统 SHALL 将需求背景与价值叙事的权威维护面定为飞书，不要求 Agent 下游读取这些段落。

#### Scenario: 下游只读契约

- **WHEN** `/qa-spec` 或代码仓库开发流程读取产品 PRD
- **THEN** 以瘦身后的 9 稿 `prd.md` 与原型为输入，不依赖本地讲解层背景/价值
