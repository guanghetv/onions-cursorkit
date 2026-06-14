## Context

`workspace-specflow` 已在 `workspace-specflow-plan-b-upgrade` 中落地 `/pm-proto`、`/pm-spec`（MODULE 五块 + AI Review）。产品团队实际 PRD 撰写仍遵循飞书 [标准模板](https://guanghe.feishu.cn/docx/S38Id4fxAofdz8xsWCVcRkHjnHg)，且存在 **5稿 → 交互评审 → 9稿** 的版本节奏。

本变更在 plan-b 成果之上做 **模板对齐 + 阶段拆分**，不重复实现飞书镜像同步。

## Goals / Non-Goals

**Goals**

- `prd.md` 章节结构与飞书模板一致（一~七 + 3.3/3.4）
- 新增 `/pm-spec-5`，升级 `/pm-spec` 为 9稿定稿
- 5稿/9稿确认快照与版本表追溯
- 保留 MODULE 锚点、AI Review、brainstorming 门禁
- 下游 `/qa-spec`、`/dev-start` 无破坏性变更
- 需求目录采用中文名，提升文件管理器可发现性

**Non-Goals**

- 飞书文档双向同步 / CI 镜像
- 1稿独立技能或模板
- metadata 复杂状态机（评审评分、开发关联等）
- 修改业务代码仓库
- 批量迁移既有英文目录为中文名

## Decisions

### 0. 需求目录命名：中文目录 + 稳定英文 `id`（方案 B）

废除原决策 D14（目录名 kebab-case 英文）。`requirements/` 下一级子目录为人读中文名，`metadata.yaml.id` 为机读稳定 slug。

**生成流程**（`/req-new` Step 2）：

```text
输入：飞书标题「订单退款流程优化」或用户一句话
  ↓
name ← 中文显示名（原始标题）
dir  ← 清洗后中文目录名：
       - 去除 /\:*?"<>| 等非法字符
       - 首尾空白裁剪
       - 最长 30 字（超出截断）
  ↓
消歧（扫描 requirements/ 现有目录名）：
  - 无冲突 → requirements/订单退款流程优化/
  - 有冲突 → requirements/订单退款流程优化-2/
  - 仍冲突 → requirements/订单退款流程优化-0612/（MMDD）
  ↓
id ← 英文 kebab-case slug（由标题拼音/关键词生成，创建后不变）
     例：order-refund-flow-opt
```

**字段职责**：

| 字段 | 位置 | 用途 | 可变性 |
|------|------|------|--------|
| 目录名 | `requirements/<中文名>/` | 人找需求 | 创建时确定；禁止随意改名 |
| `metadata.id` | metadata.yaml | openspec `requirement_ref`、脚本、分支关联 | **创建后不变** |
| `metadata.name` | metadata.yaml | 命令列表显示（与目录名通常一致） | 可更新 |

**列表展示**（`req-status`、`dev-start`）：

```
订单退款流程优化（id: order-refund-flow-opt）
  PRD 5稿: confirmed | 9稿: pending
```

**与 openspec 衔接**：`requirement_ref` 使用**实际目录路径** `requirements/订单退款流程优化/`；跨仓库脚本继续用 `metadata.id` 作逻辑键。

**迁移**：既有英文目录（如 `contract-subject-tree/`）保留不动；新需求走中文目录规则。

### 1. 章节映射：飞书为纲，workspace-specflow 为补充

| 飞书章节 | prd.md 映射 | workspace-specflow 补充 |
|----------|-------------|-------------------------|
| 一、需求概述 | 同 | 概述段后嵌入「开发速览」小表（需求类型/影响范围/原型情况/阅读顺序）；复杂流程末尾放 Mermaid |
| 二、版本及进度跟踪 | 同 | `PM` 列产品自填，Agent 不覆盖；`日期`/`版本号`/`变更内容` 仅在 5稿/9稿确认时追加行 |
| 三、背景和价值 | 3.1 背景 + 3.2 价值 | **新增** 3.3 关键关注、3.4 回归范围（callout） |
| 四、需求 Feature List | 同 | 表格增加 `MODULE` 列，与第五章一一对应 |
| 五、需求详情说明 | 3 列表格（模块/页面 \| 图示 \| 说明） | 每 MODULE 独立 `### MODULE-N: <名> [新增/修改]` + 一节 3 列表格；说明列 1.a.b 结构 |
| 六、设计图地址 | 同 | — |
| 七、埋点需求 | 7.1~7.3 | 无埋点时写「本需求无埋点需求」 |

**不采用**：文档顶部「产品同学 / 文档更新日期」独立表（飞书模板无此结构）。

### 2. 5稿 / 9稿 职责分离

| 维度 | 5稿 (`/pm-spec-5`) | 9稿 (`/pm-spec` / `/pm-spec-9`) |
|------|-------------------|--------------------------------|
| 用途 | 内审 + 交互评审会 | 交互评审后需求评审定稿 |
| `[待定]` | 允许 | 禁止（P0） |
| 3.3 关键关注 | 可含开放问题 | 须为已确认风险 |
| 验收标准 | 可写「待交互后补充」 | 完整 checklist |
| AI Review 结论 | 可进入交互评审 / 建议补充后进入 / 暂不建议 | 可开工 / 建议完善后开工 / 不可开工 |
| 评审记录 | `prototypes/ai-review-v5.md` | `prototypes/ai-review.md` |
| 确认后 | `prd.v5.status=confirmed` + v5 快照 | `prd.status=confirmed` + v9 快照 |

### 3. 活跃稿 + 快照存档

```
requirements/
  订单退款流程优化/              # 中文目录名（人读）
    metadata.yaml                # id: order-refund-flow-opt（机读 slug）
    prd.md
    snapshots/
    prototypes/
    test/
  contract-subject-tree/         # 既有英文目录（不迁移，共存）
```

- 5稿确认后 → 产品可**直接手工修改** `prd.md`（会中批注、补交互结论）
- 9稿 `/pm-spec` Step 1 读取：当前 `prd.md` + `snapshots/` 最新 `prd-v5-*.md`，输出 5→9 差异摘要

### 4. 版本表写入策略（决策 A）

- Agent **每次**改写正文：**不**动第二章版本表
- 仅在 `/pm-spec-5` 或 `/pm-spec-9` **用户确认通过**时追加一行：

```markdown
| 2026-06-12 | 5-1 | 张三 | 结构化增强；MODULE 初拆；待定项 2 处 | snapshots/prd-v5-2026-06-12.md |
| 2026-06-15 | 9-1 | 张三 | 交互评审后定稿；消除待定项 | snapshots/prd-v9-2026-06-15.md |
```

### 5. metadata 最小扩展

```yaml
prd:
  stage: v5_pending | v5_confirmed | v9_pending | confirmed
  status: pending          # 仅 9稿 confirmed 后 = confirmed
  confirmed_at: null
  v5:
    status: pending | confirmed
    confirmed_at: null
    snapshot: snapshots/prd-v5-2026-06-12.md
  v9:
    status: pending | confirmed
    confirmed_at: null
    snapshot: snapshots/prd-v9-2026-06-15.md
```

`prd.status = confirmed` 语义不变 → `/qa-spec`、`/dev-start` 无需改门禁逻辑。

### 6. 飞书拉取章节映射

`/pm-spec-5` 与 `/pm-spec` Step 1 使用 `lark-cli docs +fetch` 按 h2 标题匹配：

```
一、需求概述 → ## 一、需求概述
二、版本及进度跟踪 → ## 二、版本及进度跟踪
…（一至七）
```

本地有实质内容时仍采用 plan-b 条件化优先策略。

### 7. AI Review 锚点迁移

| 旧锚点 | 新锚点 |
|--------|--------|
| `## 开发速览` | `## 一、需求概述`（开发速览小表） |
| `## 关键关注（必填）` | `### 3.3 关键关注` |
| `## 回归范围（必填）` | `### 3.4 回归范围` |
| MODULE 五块 | `## 五、需求详情说明` / `MODULE-N` / 说明列 |

## Architecture

### A. 产品主流程

```text
/req-new（Agent 补齐飞书骨架，stage=v5_pending）
    ↓
/pm-proto（可选）
    ↓
/pm-spec-5（brainstorming → 结构化 → 轻量 AI Review）
    ↓ 快照 prd-v5-*.md；prd.v5.status=confirmed
[产品内审 + 交互评审会；可手工改 prd.md]
    ↓
/pm-spec（9稿：diff v5 → brainstorming → 结构化 → 严格 AI Review）
    ↓ 快照 prd-v9-*.md；prd.status=confirmed
/qa-spec、/dev-start
```

### B. 模板文件结构

```text
plugins/workspace-specflow/skills/
  pm-spec/
    references/prd-template.md          # 9稿模板
    references/ai-review-rubric.md      # 9稿 rubric（更新锚点）
  pm-spec-5/
    SKILL.md
    references/prd-template-v5.md     # 5稿模板（允许待定）
    references/ai-review-rubric-v5.md   # 5稿 rubric
```

### C. 命令暴露

| 命令 | 技能目录 | 说明 |
|------|----------|------|
| `/pm-spec-5` | `pm-spec-5/` | 新增 |
| `/pm-spec` | `pm-spec/` | 语义升级为 9稿；description 注明「9稿定稿」 |

## Risks / Trade-offs

### [Risk] 第五章表格在 Markdown 中编辑体验差

- **缓解**：每个 MODULE 仅一行 3 列表格；复杂说明用 1.a.b 列表 + `<br/>` 换行（与飞书导出一致）

### [Risk] 5稿待定项残留至 9稿

- **缓解**：9稿 rubric P0 禁止 `[待定]`；Step 1 自动扫描并列入 brainstorming 议题

### [Trade-off] metadata 增加 v5/v9 字段

- **收益**：`req-status` 可展示双阶段进度
- **代价**：略超 plan-b「极简 metadata」；仅 3 个轻量字段，可接受

### [Trade-off] 与 plan-b MODULE 五块结构不兼容

- **收益**：产品阅读体验与飞书一致
- **代价**：需更新 ai-review-rubric 位置锚点；qa-spec 仍按 `MODULE-N` 标题匹配，兼容

### [Risk] 中文路径在终端/脚本中的转义

- **缓解**：所有技能通过扫描目录 + 选择列表定位需求，不要求手打中文路径；文档注明 UTF-8 规范

### [Trade-off] 目录名与 `id` 双轨

- **收益**：人可读 + 机器稳定引用
- **代价**：`req-new` 需同时生成目录名与 slug；禁止创建后修改 `id`

## Migration Plan

1. 新增 OpenSpec 变更（本目录）并评审通过
2. 按 tasks.md 顺序改模板 → pm-spec-5 → pm-spec 9稿 → req-new → req-status → README
3. 选 1 个样例需求跑通 5稿→9稿 E2E
4. 既有 `prd.md`（旧 MODULE 五块格式）不自动迁移；新需求用新模板，旧需求下次 `/pm-spec` 时按 9稿重写
5. 既有英文需求目录不批量改名；新需求使用中文目录 + slug `id`

## Open Questions

1. 是否需要在 `/pm-spec` 命令别名层面同时暴露 `/pm-spec-9`（本期先只更新 description，不新增重复命令）
2. 旧格式 prd.md 批量迁移脚本是否必要（本期建议按需迁移，不做批量工具）
3. `id` slug 生成策略：**英文关键词**（已确认；Step 3 可修正）
