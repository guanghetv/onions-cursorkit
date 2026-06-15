---
name: pm-spec-5
description: >-
  Use when user mentions: 5稿/pm-spec-5/内审prd/交互评审前/结构化5稿。
  Triggers when requirements directory exists and prd needs 5稿 enhancement before interaction review.
---

# /pm-spec-5 — 5稿结构化增强与交互评审前 AI Review

<HARD-GATE>
在 Step 3 Brainstorming 完成且用户**明确确认**之前，**禁止**：

- 写入或大幅改写 `prd.md` 的结构化内容（Step 4）
- 执行 AI Review 并更新 `metadata.yaml.prd.v5`（Step 5–6）

必须 **Read 并遵循** `superpowers:brainstorming` 的 SKILL.md 全流程。
</HARD-GATE>

## 前置条件

- 需求目录已创建（`/req-new` 已执行）
- 目标目录存在 `prd.md` 与 `metadata.yaml`

## 核心原则

- **5稿**用于产品内审与交互评审会；方案可未定
- 允许 `[待定]`、`[待交互确认]`；验收标准可写「待交互后补充」
- 模板见 `references/prd-template-v5.md`（结构与 9稿飞书模板一致，规则更宽松）
- 飞书读取：`lark-cli` 优先，`feishu-mcp` 兜底；按 h2 **一~七** 章节映射回填
- 本地有实质内容时本地优先；空模板时飞书优先
- **不** 设置 `prd.status = confirmed`（下游须等 9稿 `/pm-spec`）

## 流程

### Step 1: 定位需求 & 读取输入

扫描 `requirements/` 下目标需求，读取 `prd.md`：

- 本地有内容：直接使用
- 空模板 + `feishu_doc`：拉取飞书并按章节映射回填
- 本地与飞书差异明显：输出差异摘要，默认本地优先

### Step 2: 读取原型（可选）

若 `prototypes/`、`assets/` 存在，作为增强输入。

### Step 3: Brainstorming【阻断】

**REQUIRED SUB-SKILL:** `superpowers:brainstorming`（一次一问）

澄清重点：

- MODULE 初拆（与第四章 Feature List 对齐）
- 灰区与开放问题清单
- 需求类型（新增/迭代）与影响范围（写入开发速览小表）
- **不** 要求本轮定稿所有方案

用户确认后进入 Step 4。

### Step 4: 结构化增强 `prd.md`

按 `references/prd-template-v5.md` 输出飞书一~七结构：

- **一、需求概述**：开发速览表含 `当前阶段: 5稿`；概述 + 示例 blockquote
- **二、版本及进度跟踪**：PM 列留空不覆盖；**本步不追加版本行**
- **三、背景和价值**：含 `3.3 关键关注`（可含开放问题）、`3.4 回归范围`（可简略）
- **四、需求 Feature List**：含 `MODULE` 列
- **五、需求详情说明**：每 `MODULE-N` 一节 + 3 列表格；说明列允许 `[待定]`
- **六、设计图地址** / **七、埋点需求**

### Step 5: AI Review（5稿）

读取 `references/ai-review-rubric-v5.md`：

- P0 阻断 → 结论「暂不建议进入交互评审」
- 否则输出 P1/P2 与五维评分（可简化维度说明）
- 详细记录 → `prototypes/ai-review-v5.md`

### Step 6: 确认与快照

用户确认通过后：

1. **二、版本表** 追加一行：`5-n`、当天 `YYYY-MM-DD`、`变更内容`（含待定项计数）、`snapshots/prd-v5-<date>.md`
2. 复制 `prd.md` → `snapshots/prd-v5-<YYYY-MM-DD>.md`
3. 更新 `metadata.yaml`：
   - `prd.v5.status = confirmed`
   - `prd.v5.confirmed_at = <date>`
   - `prd.v5.snapshot = snapshots/prd-v5-<date>.md`
   - `prd.stage = v5_confirmed`
4. **不** 修改 `prd.status`（保持 `pending`）

### Step 7: 提示下一步

- 产品内审 + 交互评审会；会中可**直接手工修改** `prd.md`
- 交互评审后 → `/pm-spec`（9稿定稿）

## 约束

- 5稿确认后 `prd.md` 不锁定
- 版本表仅在 Step 6 确认时追加，日常改写不追加
- MODULE ID 是稳定锚点，与第四章对齐
