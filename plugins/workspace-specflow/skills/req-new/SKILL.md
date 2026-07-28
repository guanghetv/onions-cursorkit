---
name: req-new
description: >-
  Use when user mentions: 新需求/创建需求/req-new/初始化需求，
  或提供需求想法/飞书需求文档链接并想创建需求目录。
---

# /req-new — 初始化需求目录

## 前置条件

- 当前项目是 specs 仓库（含 `requirements/` 目录）
- 用户提供需求初步想法或飞书需求文档链接

## 流程

### Step 1: 获取飞书文档

若用户提供飞书链接，优先通过 `lark-cli` 读取文档并提取标题与概要。

- 若 `lark-cli` 不可用：降级使用 `feishu-mcp`（如可用）
- 若两者都不可用：提示建议安装 `lark-cli`
- 若用户未提供飞书链接：直接基于用户输入的需求想法继续初始化

### Step 2: 生成目录信息

自动生成：

- **name**：中文显示名（飞书标题或用户输入归纳）
- **目录名**：清洗后中文（见下方规则）
- **id**：英文关键词 kebab-case slug（从标题提取英文关键词，**创建后不变**）
- **module**：业务模块名（扫描已有 `metadata.yaml` 自动识别，或用户指定）

**中文目录名规则**：

1. 从 `name` 清洗：去除 `\ / : * ? " < > |`、首尾空白
2. 最长 30 字（超出截断）
3. 扫描 `requirements/` 消歧：
   - 无冲突 → 直接用
   - 有冲突 → 追加 `-2`、`-3` …
   - 序号至 `-9` 仍冲突 → 追加 `-MMDD`（如 `订单退款-0612`）
4. **不使用随机数**

**id slug 规则**：

- 从中文标题生成**英文关键词** slug（非拼音），如「订单退款流程优化」→ `order-refund-flow-opt`
- 仅小写字母、数字、连字符；创建后禁止修改

### Step 3: 用户确认

展示并允许修正：

- 中文目录名：`requirements/<目录名>/`
- `id` slug
- `name`、`module`

用户确认后进入 Step 4。

### Step 4: 创建目录和文件

按 `references/templates.md` 创建：

- `requirements/<中文目录名>/`
- `metadata.yaml`（`prd.stage = v5_pending`，`prd.v5/v9` 初始 pending；含 `feishu.*` / `consistency.*` 占位）
- `prd.md`（飞书七章空骨架；Agent 用 Step 1 信息填充标题与概述占位）
- `snapshots/.gitkeep`
- `prototypes/.gitkeep`
- `test/test-spec.md`

### Step 4.5: 创建飞书文档（强制）

目录创建成功后 **必须** 执行 `/prd-feishu-sync create`（按该技能全文规程）：

1. 使用 `lark-cli` **XML** 创建飞书文档（按 `prd-feishu-sync`：同步绑定 callout + 评审区 + 七章 + 一致性 callout「⏳ 未校验」；禁止裸 `[PRD-SYNC:BEGIN/END]`；章节按语义 unit 定位）
2. 回写 `metadata.feishu.doc_url` / `doc_token`，并同步 `feishu_doc`
3. `last_synced_stage=skeleton`，`v9_synced=false`，`consistency.status=unknown`


若 `lark-cli` 不可用或 create 失败：**明确报错**，不得假装已绑定；可提示用户修好环境后手动 `/prd-feishu-sync create`。若用户在 Step 1 已提供飞书链接且希望接管已有文档，改为引导 `rebind`（须用户确认），不要静默覆盖他人文档。

### Step 5: 提示下一步

默认流程：`/req-new`（含飞书 create）→ `/pm-proto`（可选）→ `/pm-spec-5` → 交互评审 → `/pm-spec`（9稿）→ `/prd-publish`（或分步 sync/check）。

## 约束

- 目录名中文、可读；`id` 英文 slug 稳定（废除原 D14「目录 kebab-case」）
- 1稿由 Agent 代写骨架，产品不单独维护
- 不记录 feishu_task（D17）、不记录 created_by（D18）
- 初始化必须留下可用飞书绑定或显式失败提示
