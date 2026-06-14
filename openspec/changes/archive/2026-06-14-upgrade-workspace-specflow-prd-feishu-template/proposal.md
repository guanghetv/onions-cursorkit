# upgrade-workspace-specflow-prd-feishu-template

## Why

`workspace-specflow` 当前 `prd-template.md` 采用「开发速览 + MODULE 五块」结构，与产品团队在飞书沿用的 [PRD 模板](https://guanghe.feishu.cn/docx/S38Id4fxAofdz8xsWCVcRkHjnHg) 差异较大，导致：

1. 产品从飞书迁移到 specs 仓库时心智成本高，章节命名与表格布局不一致。
2. 缺少与产品真实工作流对齐的 **5稿（内审/交互评审）** 与 **9稿（需求评审定稿）** 阶段能力，无法保留历史存档。
3. `MODULE` 锚点与 QA/Dev 协作仍需要，但不能以牺牲飞书模板可读性为代价。
4. `requirements/` 下目录名均为英文 kebab-case，产品在文件管理器中难以快速定位需求（中文 `name` 仅存在于 `metadata.yaml`）。

本期目标：在保留 `MODULE` 锚点、AI Review 门禁与下游 `/qa-spec`、`/dev-start` 兼容的前提下，将 PRD 结构对齐飞书模板，引入 5稿/9稿双阶段技能与快照存档，并将需求目录改为**中文目录名 + 稳定英文 `id` slug**（方案 B）。

## What Changes

- **PRD 模板对齐飞书七章**
  - 章节映射以飞书模板为准：一~七 + `3.3 关键关注` / `3.4 回归范围`（workspace-specflow 补充）
  - 不在文档顶部新增元信息表；产品同学与日期写入 **二、版本及进度跟踪** 表的 `PM` / `日期` 列
  - `开发速览` 融入 **一、需求概述**（概述段后小表，不单独成章）
  - `MODULE` 锚点：`四、Feature List` 增加 `MODULE` 列；`五、需求详情说明` 每 MODULE 一节 + 飞书 3 列表格（模块/页面 | 图示 | 说明）
- **5稿 / 9稿 双阶段**
  - 新增 `/pm-spec-5`：内审 + 交互评审材料；允许 `[待定]` / `[待交互确认]`；AI Review 结论为「可进入交互评审」系列
  - 升级 `/pm-spec` 为 **9稿**（`/pm-spec-9` 语义）：交互评审后定稿；严格 AI Review；`prd.status = confirmed` 门禁不变
  - ~~1稿~~ 忽略：`/req-new` Agent 自动补齐飞书骨架
- **存档机制**
  - `prd.md` 为唯一活跃工作稿（5稿确认后允许产品手工修改）
  - 确认时快照：`snapshots/prd-v5-<YYYY-MM-DD>.md`、`snapshots/prd-v9-<YYYY-MM-DD>.md`
  - **二、版本表** 仅在 `/pm-spec-5` 或 `/pm-spec-9` **确认时**追加一行（版本号 `5-n` / `9-n`），Agent 日常改写不自动追加
- **metadata 轻量扩展**
  - 增加 `prd.stage`、`prd.v5`、`prd.v9` 最小字段；`prd.status = confirmed` 仍表示 9稿定稿（兼容 `/qa-spec`、`/dev-start`）
- **需求目录中文命名（方案 B）**
  - 目录名：清洗后的中文标题（飞书标题或用户输入），便于文件管理器查找
  - `metadata.yaml.id`：稳定英文 kebab-case slug，创建后不变，供 openspec / 脚本引用
  - 重名消歧：`-2`、`-3` 序号后缀；仍冲突时用日期后缀 `-MMDD`；**不使用随机数**
  - 废除决策 D14「目录名 kebab-case」；现有英文目录不迁移，新旧共存
- **配套更新**
  - `req-new` 初始化模板改为飞书七章骨架 + 中文目录命名规则
  - `req-status` / `dev-start` 列表优先显示中文目录名与 `name`
  - `req-status` 展示 5稿/9稿双状态
  - `ai-review-rubric` 拆分为 v5（轻量）/ v9（严格），章节锚点更新为 `### 3.3` / `### 3.4`

## Capabilities

### New Capabilities

- `workspace-specflow-prd-template`: 飞书 PRD 模板对齐、req-new 骨架、章节映射与快照约定
- `workspace-specflow-pm-spec-5`: 5稿结构化增强与交互评审前 AI Review
- `workspace-specflow-req-naming`: 中文目录名 + 稳定英文 `id` slug 命名规则

### Modified Capabilities

- `workspace-specflow-pm-spec`: 升级为 9稿定稿流程，读取 v5 快照 diff，严格评审与 confirmed 门禁
- `workspace-specflow-req-new`: 目录创建逻辑从 kebab-case 改为中文目录 + slug `id`（隐含于 req-new 技能更新）

## Impact

- 影响目录：
  - `plugins/workspace-specflow/skills/pm-spec/`（9稿）
  - `plugins/workspace-specflow/skills/pm-spec-5/`（新增）
  - `plugins/workspace-specflow/skills/req-new/`
  - `plugins/workspace-specflow/skills/req-status/`
  - `plugins/workspace-specflow/commands/`（`pm-spec-5.md` 新增，`pm-spec.md` 更新）
  - `plugins/workspace-specflow/README.md`
  - `plugins/workspace-specflow/rules/workspace-awareness.mdc`
- **不破坏**下游：`/qa-spec`、`/dev-start` 仍以 `prd.status = confirmed`（9稿）为门禁
- **不实现**飞书双向镜像同步（延续 plan-b 非目标）

## References

- 飞书 PRD 模板: https://guanghe.feishu.cn/docx/S38Id4fxAofdz8xsWCVcRkHjnHg
- 前置变更: `openspec/changes/workspace-specflow-plan-b-upgrade/`

## Decisions

| # | 决策 | 说明 |
|---|------|------|
| D1 | 严格飞书一~七章节映射 | 不新增文档顶部元信息表 |
| D2 | 3.3/3.4 作为第三章补充子节 | 关键关注、回归范围独立 callout，便于 AI Review 锚定 |
| D3 | 版本表仅在 5稿/9稿确认时追加行 | 选项 A；手工改 prd.md 不自动动表 |
| D4 | 5稿确认后允许手工改 prd.md | 活跃稿模式，会中改动不阻断 |
| D5 | snapshots/ 目录存确认快照 | 支持 5-2、9-2 多次迭代 |
| D6 | MODULE 通过第四章 + 第五章锚定 | 兼容 qa-spec / dev-start |
| D7 | 1稿由 req-new Agent 代写 | 产品不再单独维护 1稿 |
| D8 | 中文目录 + 英文 slug `id`（方案 B） | 目录可读；`id` 稳定供机器引用；重名用序号/日期后缀 |
