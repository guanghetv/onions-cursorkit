---
name: pm-spec
description: >-
  Use when user mentions: 产品spec/pm-spec/转换需求/增强prd/spec转换/结构化需求。
  Triggers when prd.status is pending and requirements directory exists.
---

# /pm-spec — prd.md 结构化增强

## 前置条件

- 需求目录已创建（`/req-new` 已执行）
- `metadata.yaml` 中 `prd.status` 为 `pending`

## 核心原则

**prd.md 就是产品 spec**（决策 D28）。不生成新文件，在产品已写的 prd.md 上做结构化增强：保留原始内容，叠加 MODULE 结构、验收标准、业务规则。

## 流程

### Step 1: 定位需求 & 读取输入

扫描 `requirements/` 下 `prd.status = pending` 的需求。读取 prd.md，判断场景：

- **prd.md 已有内容**：直接使用
- **prd.md 为空模板**：从 `metadata.yaml` 的 `feishu_doc` 通过 feishu-mcp 拉取。feishu-mcp 不可用时**必须明确提示**。

如有 Figma 链接，更新 `metadata.yaml` 的 `figma` 字段。`prototypes/` 下有原型文件时读取作为补充。

### Step 2: 扫描前后端服务（业务层面）

从 `workspace-repos.json` 解析仓库路径，输出业务层面影响分析。**安全护栏**：只提取业务影响，不提技术实现细节（决策 D6）。

### Step 3: Brainstorming

调用 `superpowers:brainstorming`，引导产品同学：澄清模糊点 → 发现遗漏场景 → 讨论 MODULE 划分 → 确认优先级 → 明确验收标准。

### Step 4: 在 prd.md 上增强为 MODULE 结构

保留产品原始内容，叠加结构化内容。**模板详情**：读取 `references/prd-template.md`。

### Step 5: 逐段 review

分段展示：需求背景 → MODULE 概览 → 逐个 MODULE → 全局约束 → 名词解释。每段可修改。

### Step 6: 完整性校验

AI 对照飞书原文检查未纳入内容、列出新增场景、确认验收标准覆盖。确认后写入 `prd.md`，更新 `metadata.yaml`：`prd.status = confirmed`。

### Step 7: 可选同步回飞书

workspace-specflow 不负责飞书同步（决策 D32）。提示产品同学：

- "prd.md 已确认。如需同步到飞书，可执行 `prd-sync push`。"
- 如 `metadata.yaml` 有 `feishu_doc` 字段 → 展示飞书文档链接，方便确认是更新已有文档还是创建新文档。
- 首次同步时 `prd-sync` 会自动在 `.cursor/prd-sync-mappings.json` 建立映射，后续可增量同步。

### Step 8: 可选生成交互演示

如确认：读取 prd.md → 扫描前端样式（只读） → 生成 `prodspecs/<requirement-id>/index.html`（资源内联）→ 更新索引。**严禁修改代码仓库文件**。

### Step 9: 提示下一步

测试同学 → `/qa-spec`；开发同学 → `/dev-start`（不需要等测试 spec）。

## 约束

- 增强而非覆盖（决策 D30）
- 产品 spec 只描述需求本质，不涉及技术实现（决策 D6）
- demo 只写 specs 仓库的 `prodspecs/`，禁写代码仓库
- MODULE ID 是稳定锚点（决策 D21）
- 增量更新暂不支持（决策 D34）
