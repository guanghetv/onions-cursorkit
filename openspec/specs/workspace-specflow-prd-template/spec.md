# Workspace Specflow PRD Template (Feishu Alignment) Specification

## Purpose

定义 `prd.md` 与飞书 PRD 标准模板的章节对齐、workspace-specflow 补充字段、版本表与快照约定。
## Requirements
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

### Requirement: workspace-specflow 字段融入飞书章节

系统 SHALL 将研发协作用字段融入既有飞书章节，不新增独立「研发区」。

#### Scenario: 开发速览融入第一章

- **WHEN** Agent 输出开发速览（需求类型、影响范围、原型情况、阅读顺序）
- **THEN** 以小表格形式置于 `## 一、需求概述` 概述段之后，不单独成章

#### Scenario: 关键关注与回归范围写入第三章

- **WHEN** Agent 输出关键关注或回归范围
- **THEN** 分别写入标题含「关键关注」「回归」的小节（常见展示号可为 3.3 / 3.4，仅兼容），使用 callout 格式；定位以关键词为准

#### Scenario: MODULE 锚点通过第四、五章表达

- **WHEN** Agent 拆分 MODULE
- **THEN** `## 四、需求 Feature List` 表格包含 `MODULE` 列；`## 五、需求详情说明` 下每个 MODULE 以 `### MODULE-N: <名> [新增/修改]` 为节标题，节内为飞书 3 列表格（模块/页面 | 图示 | 说明）

### Requirement: 版本表仅在阶段确认时追加

系统 SHALL 仅在 `/pm-spec-5` 或 `/pm-spec`（9稿）用户确认通过时向第二章版本表追加一行。

#### Scenario: 确认时追加版本行

- **WHEN** `/pm-spec-5` 或 `/pm-spec`（9稿）完成用户确认
- **THEN** 系统在 `## 二、版本及进度跟踪` 追加一行，含当天日期、版本号（`5-n` 或 `9-n`）、变更摘要与快照路径

#### Scenario: 日常改写不追加版本行

- **WHEN** Agent 在确认前改写 `prd.md` 正文
- **THEN** 系统不自动向版本表追加或修改行

### Requirement: 5稿/9稿快照存档

系统 SHALL 在 5稿/9稿确认时将 `prd.md` 快照至 `snapshots/` 目录。

#### Scenario: 5稿确认快照

- **WHEN** `/pm-spec-5` 确认通过
- **THEN** 系统将当前 `prd.md` 复制为 `snapshots/prd-v5-<YYYY-MM-DD>.md` 并在 metadata 记录路径

#### Scenario: 9稿确认快照

- **WHEN** `/pm-spec`（9稿）确认通过
- **THEN** 系统将当前 `prd.md` 复制为 `snapshots/prd-v9-<YYYY-MM-DD>.md` 并在 metadata 记录路径

### Requirement: req-new 初始化飞书骨架

系统 SHALL 在 `/req-new` 时创建飞书七章空骨架而非旧版「需求背景/功能描述」模板。

#### Scenario: 新建需求目录结构

- **WHEN** `/req-new` 创建需求目录
- **THEN** 系统创建含飞书七章占位内容的 `prd.md`、`snapshots/.gitkeep`，以及含 `prd.stage/v5/v9` 的 `metadata.yaml`

#### Scenario: Agent 补齐 1稿等价内容

- **WHEN** 用户提供飞书链接或一句话需求
- **THEN** Agent 自动补齐飞书骨架各章占位，不要求产品单独维护 1稿

### Requirement: 讲解层归属飞书

系统 SHALL 将需求背景与价值叙事的权威维护面定为飞书，不要求 Agent 下游读取这些段落。

#### Scenario: 下游只读契约

- **WHEN** `/qa-spec` 或代码仓库开发流程读取产品 PRD
- **THEN** 以瘦身后的 9 稿 `prd.md` 与原型为输入，不依赖本地讲解层背景/价值

