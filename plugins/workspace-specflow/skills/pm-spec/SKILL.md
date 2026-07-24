---
name: pm-spec
description: >-
  Use when user mentions: 9稿/pm-spec-9/产品spec/pm-spec/转换需求/增强prd/spec转换/PRD评审/定稿。
  Triggers when requirements directory exists and prd needs 9稿 finalization after interaction review.
---

# /pm-spec — 9稿定稿：结构化增强与 AI Review

<HARD-GATE>
在 Step 3 Brainstorming 完成且用户**明确确认**之前，**禁止**：

- 写入或大幅改写 `prd.md` 的结构化内容（Step 4）
- 执行 AI Review 并更新 `metadata.yaml.prd.status`（Step 5–6）
- 以「prd 已有内容 / 飞书已拉取」为由跳过澄清

必须 **Read 并遵循** `superpowers:brainstorming` 的 SKILL.md 全流程。
</HARD-GATE>

## 前置条件

- 需求目录已创建（`/req-new` 已执行）
- 建议已完成 `/pm-spec-5`（5稿）与交互评审；非强制但 Step 1 会对比 v5 快照
- 目标目录存在 `prd.md` 与 `metadata.yaml`

## 核心原则

**9稿**为交互评审后的需求评审定稿；`prd.md` 确认后即为下游权威输入。

- 模板见 `references/prd-template.md`（飞书一~七；关键关注/回归按语义定位）
- **禁止**残留 `[待定]` / `[待交互确认]`（P0）
- 飞书读取：`lark-cli` 优先；按 h2 **一~七** 映射；本地优先策略同 plan-b
- AI Review 见 `references/ai-review-rubric.md`（9稿）
- 确认后 `prd.status = confirmed` → 解锁 `/qa-spec` 与代码仓库开发消费

## 流程

### Step 1: 定位需求 & 读取输入

扫描 `requirements/` 下目标需求，读取 `prd.md`。

若 `snapshots/prd-v5-*.md` 存在：读取**最新** v5 快照，与当前 `prd.md` 对比，输出 **5→9 差异摘要**（待定项是否已决议、交互结论是否已写入）。

- 本地有内容：直接使用（含会中手工修改）
- 空模板 + `feishu_doc`：拉取飞书按章节映射回填

### Step 2: 读取原型与引用（可选）

若 `prototypes/`、`assets/` 存在，作为增强输入。

### Step 3: Brainstorming【阻断】

**REQUIRED SUB-SKILL:** `superpowers:brainstorming`（一次一问）

澄清重点：

- 消除所有 `[待定]` 项（交互评审结论）
- 确认 MODULE 拆分与验收标准
- 需求类型、影响范围；迭代时**本轮变更 MODULE 清单**
- 回归范围（`contract.regression`，标题含「回归」）：需回归项 + 不纳入项

用户确认后进入 Step 4。

### Step 4: 结构化增强 `prd.md`（含瘦身）

按 `references/prd-template.md` 输出：

- **一、需求概述**：开发速览表含 `当前阶段: 9稿`；复杂流程 Mermaid 放本节末尾
- **二、版本及进度跟踪**：PM 不覆盖；**本步不追加版本行**
- **三、背景和价值**：保留「关键关注」「回归范围」（`contract.critical` / `regression`）必填 callout；**按语义删除讲解层**（标题含「背景」「价值」的 `narrative.*` 整节删除，禁止「见飞书」指针）；**不得**为补洞改写契约小节展示序号或前移四～七


- **四、Feature List**：含 `MODULE` 列
- **五、需求详情说明**：每 MODULE 3 列表格 + 完整验收 checklist；**无待定**；保留原型锚点
- **六、设计图地址** / **七、埋点需求**

### Step 5: AI Review（9稿）

读取 `references/ai-review-rubric.md`：

1. 按开发速览需求类型确定深审范围
2. P0 阻断（含「残留待定」规则 6）
3. 五维评分 + P0/P1 问题项 → `prototypes/ai-review.md`
4. `prd.md` **二、变更内容** 记结论摘要

### Step 6: 确认、同步、校验、快照与状态

用户确认通过后，**按序**执行（任一步 critical 失败则**不得**将 `prd.status` 设为 `confirmed`）：

1. **二、版本表** 追加：`9-n`、当天日期、`AI Review: 可开工`（等）、`snapshots/prd-v9-<date>.md`
2. 复制 `prd.md` → `snapshots/prd-v9-<YYYY-MM-DD>.md`
3. `/prd-feishu-sync push --stage v9`（失败则明确报错并停止 confirmed）
4. `/prd-consistency-check`（进开发前）；存在 critical fail → 停止 confirmed
5. 更新 `metadata.yaml`：
   - `prd.status = confirmed`
   - `prd.confirmed_at = <date>`
   - `prd.v9.status = confirmed`
   - `prd.v9.snapshot = snapshots/prd-v9-<date>.md`
   - `prd.stage = confirmed`

也可在本步用 `/prd-publish --stage v9` 覆盖上述第 3–4 步（push + check）。

### Step 7: 提示下一步

- 测试 → `/qa-spec`（将检查 `consistency.status`）
- 开发 → 代码仓库流程直接读瘦身后的 `prd.md`
- 提交 specs 仓前若又改契约：先 `/prd-publish`（T4）

## 约束

- 增强而非覆盖产品原始决策
- 产品 spec 只描述需求本质，不涉及技术实现
- MODULE ID 稳定锚点；版本表仅在 Step 6 确认时追加
