# Workspace Specflow PRD Template (Feishu Alignment)

## ADDED Requirements

### Requirement: PRD 章节对齐飞书标准模板

系统 SHALL 使 `prd.md` 章节结构与飞书 PRD 模板（https://guanghe.feishu.cn/docx/S38Id4fxAofdz8xsWCVcRkHjnHg）一致，并仅允许在第三章补充 workspace-specflow 必需的子节。

#### Scenario: 标准章节顺序

- **WHEN** Agent 生成或增强 `prd.md`
- **THEN** 文档包含以下顶层章节（按序）：
  - `## 一、需求概述`
  - `## 二、版本及进度跟踪`
  - `## 三、背景和价值`（含 `3.1` `3.2` `3.3` `3.4`）
  - `## 四、需求 Feature List`
  - `## 五、需求详情说明`
  - `## 六、设计图地址`
  - `## 七、埋点需求`（含 `7.1` `7.2` `7.3`）

#### Scenario: 不在文档顶部加元信息表

- **WHEN** Agent 初始化或增强 `prd.md`
- **THEN** 系统不在 `# 标题` 与 `## 一、需求概述` 之间插入「产品同学 / 文档更新日期」独立表格

#### Scenario: PM 与日期写入版本表

- **WHEN** 需要记录产品同学或文档日期
- **THEN** 系统使用 `## 二、版本及进度跟踪` 表格的 `PM` 与 `日期` 列；`PM` 默认空且 Agent 不覆盖已有值

### Requirement: workspace-specflow 字段融入飞书章节

系统 SHALL 将研发协作用字段融入既有飞书章节，不新增独立「研发区」。

#### Scenario: 开发速览融入第一章

- **WHEN** Agent 输出开发速览（需求类型、影响范围、原型情况、阅读顺序）
- **THEN** 以小表格形式置于 `## 一、需求概述` 概述段之后，不单独成章

#### Scenario: 关键关注与回归范围作为 3.3 / 3.4

- **WHEN** Agent 输出关键关注或回归范围
- **THEN** 分别写入 `### 3.3 关键关注` 与 `### 3.4 回归范围`，使用 callout 格式

#### Scenario: MODULE 锚点通过第四、五章表达

- **WHEN** Agent 拆分 MODULE
- **THEN** `## 四、需求 Feature List` 表格包含 `MODULE` 列；`## 五、需求详情说明` 下每个 MODULE 以 `### MODULE-N: <名> [新增/修改]` 为节标题，节内为飞书 3 列表格（模块/页面 | 图示 | 说明）

### Requirement: 版本表仅在阶段确认时追加

系统 SHALL 仅在 `/pm-spec-5` 或 `/pm-spec-9` 用户确认通过时向第二章版本表追加一行。

#### Scenario: 确认时追加版本行

- **WHEN** `/pm-spec-5` 或 `/pm-spec-9` 完成用户确认
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

- **WHEN** `/pm-spec-9`（`/pm-spec`）确认通过
- **THEN** 系统将当前 `prd.md` 复制为 `snapshots/prd-v9-<YYYY-MM-DD>.md` 并在 metadata 记录路径

### Requirement: req-new 初始化飞书骨架

系统 SHALL 在 `/req-new` 时创建飞书七章空骨架而非旧版「需求背景/功能描述」模板。

#### Scenario: 新建需求目录结构

- **WHEN** `/req-new` 创建需求目录
- **THEN** 系统创建含飞书七章占位内容的 `prd.md`、`snapshots/.gitkeep`，以及含 `prd.stage/v5/v9` 的 `metadata.yaml`

#### Scenario: Agent 补齐 1稿等价内容

- **WHEN** 用户提供飞书链接或一句话需求
- **THEN** Agent 自动补齐飞书骨架各章占位，不要求产品单独维护 1稿
