# Workspace Specflow Requirement Naming

## ADDED Requirements

### Requirement: 中文目录名提升可发现性

系统 SHALL 使用清洗后的中文标题作为 `requirements/` 下一级目录名，便于产品在文件管理器中定位需求。

#### Scenario: 从飞书标题生成中文目录名

- **WHEN** `/req-new` 从飞书文档提取标题「订单退款流程优化」
- **THEN** 系统生成目录名 `订单退款流程优化`（去除非法文件名字符、裁剪首尾空白、最长 30 字）

#### Scenario: 从用户输入生成中文目录名

- **WHEN** 用户未提供飞书链接，直接输入中文需求描述
- **THEN** 系统从描述提取或归纳中文目录名，并在 Step 3 供用户确认或修正

### Requirement: 稳定英文 slug 作为 metadata.id

系统 SHALL 为每个需求生成稳定的英文 kebab-case `id`，写入 `metadata.yaml`，创建后不变。

#### Scenario: id 与目录名分离

- **WHEN** `/req-new` 创建 `requirements/订单退款流程优化/`
- **THEN** `metadata.yaml` 中 `id` 为英文 slug（如 `order-refund-flow-opt`），`name` 为中文显示名

#### Scenario: id 创建后不可变

- **WHEN** 需求目录已创建
- **THEN** Agent 不得修改 `metadata.id`；目录改名须显式用户确认并同步更新所有引用

#### Scenario: Step 3 允许用户修正 id

- **WHEN** `/req-new` Step 3 展示生成结果
- **THEN** 用户可修正 `id` slug 后确认创建

### Requirement: 中文目录名重名消歧

系统 SHALL 在目录名冲突时使用可读的序号或日期后缀，不使用随机数。

#### Scenario: 首次创建无冲突

- **WHEN** `requirements/订单退款/` 不存在
- **THEN** 系统创建 `requirements/订单退款/`

#### Scenario: 序号后缀消歧

- **WHEN** `requirements/订单退款/` 已存在
- **THEN** 系统尝试 `requirements/订单退款-2/`、`-3/` … 直至无冲突

#### Scenario: 日期后缀兜底

- **WHEN** 序号后缀至 `-9` 仍冲突
- **THEN** 系统使用 `订单退款-<MMDD>/` 格式（如 `订单退款-0612/`）

### Requirement: 命令列表优先显示中文名

系统 SHALL 在 `req-status` 与 `dev-start` 的需求列表中优先展示中文目录名，并附带 `id` slug。

#### Scenario: req-status 展示格式

- **WHEN** 执行 `/req-status`
- **THEN** 每行显示 `订单退款流程优化（id: order-refund-flow-opt）` 及 PRD/测试状态

#### Scenario: dev-start 选择列表

- **WHEN** 执行 `/dev-start` 自动扫描需求
- **THEN** 列表项以中文目录名为主标识，`id` 为辅助标识

### Requirement: 与既有英文目录共存

系统 SHALL 兼容既有 kebab-case 英文目录，不强制迁移。

#### Scenario: 扫描混合目录

- **WHEN** `requirements/` 下同时存在 `contract-subject-tree/` 与 `订单退款/`
- **THEN** 所有扫描类技能正常列出两类目录，读取各自 `metadata.yaml`

## MODIFIED Requirements

### Requirement: 废除目录名 kebab-case 约束（原决策 D14）

系统 SHALL 不再要求 `requirements/` 目录名为 kebab-case 英文。

#### Scenario: req-new 约束更新

- **WHEN** 更新 `req-new` 技能
- **THEN** 移除「目录名 kebab-case 英文」约束；改为「目录名中文、id 英文 slug」

#### Scenario: workspace-awareness 规则同步

- **WHEN** 更新 `workspace-awareness.mdc`
- **THEN** 文档与规则反映中文目录 + slug `id` 命名策略
