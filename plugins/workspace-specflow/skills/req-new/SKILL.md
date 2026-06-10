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
- 若用户未提供飞书链接：直接基于用户输入的需求想法继续初始化，不额外提示补链

### Step 2: 生成目录信息

自动生成：
- `id`: kebab-case 英文目录名（决策 D14）
- `name`: 中文显示名
- `module`: 业务模块名（扫描已有 `metadata.yaml` 自动识别，或用户指定新模块）

### Step 3: 用户确认

展示生成结果（标题、ID、模块、目录结构），用户确认或修正。

### Step 4: 创建目录和文件

按 `references/templates.md` 中的模板创建：
- `metadata.yaml`（prd: pending, test_spec: pending）
- `prd.md`（空模板，不预设 MODULE 结构）
- `prototypes/`（空目录含 .gitkeep）
- `test/test-spec.md`（空模板）

### Step 5: 提示下一步

默认流程：`/req-new` → `/pm-proto`（原型生成/完善）→ `/pm-spec`（补充并结构化 `prd.md`）。

## 约束

- 目录名 kebab-case 英文（决策 D14）
- prd.md 空模板不预设 MODULE（由 /pm-spec 增强时生成）
- 不记录 feishu_task（决策 D17）、不记录 created_by（决策 D18）
