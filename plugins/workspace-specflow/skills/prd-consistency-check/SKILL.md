---
name: prd-consistency-check
description: >-
  校验工作区契约 prd.md 与绑定飞书文档的一致性（结构 A + 语义 B），落盘报告并回写飞书结果。
  Use when: 一致性校验、PRD 自检、能否开工、评审就绪、进开发前自检、prd-consistency-check。
  禁止用对话口头清单代替真跑。不负责推送正文。
---

# /prd-consistency-check — 契约层一致性出口门

## 硬规则

命中触发词（一致性校验 / 能否开工 / 评审就绪 / 进开发前自检等）→ **必须真跑本流程并落盘报告**，禁止口头打勾清单。

本技能 **不修改** MODULE 契约正文；仅写报告、`metadata.consistency`、飞书机器区结论、「已跳过」留痕。

## 校验范围

只比对**契约层** unit（见 `prd-feishu-sync/references/chapter-map.md`）：

`contract.overview` / `versions` / `critical` / `regression` / `features` / `MODULE-N` / `details` / `design` / `tracking`（后二者按需）。

**忽略**飞书与本地在讲解层（`narrative.background` / `narrative.value`，标题含「背景」「价值」）上的差异——不构成 fail。

**定位**：unit key → 标题关键词 → 序号兼容；禁止只靠 `3.1`/`3.2` 等数字判断。

**C6（讲解层回流）适用条件**（满足任一即启用；与 `prd.stage` 是否已写成 `confirmed` **无关**——`/pm-spec` 是在 check **之后**才写 confirmed）：

- 自检阶段为「进开发前」/ T4 / `/qa-spec` 前；或
- `prd.stage` ∈ {`v9_pending`, `confirmed`}；或
- `feishu.v9_synced == true`；或
- 本地开发速览「当前阶段」为 9稿

启用时：本地 **不得**再存在 `narrative.*`（含空壳或「见飞书」指针）；也不得把 `contract.critical` / `regression` 改写成更小的展示序号或前移四～七。  
**不适用**：纯「评审前」5 稿自检（本地可仍含背景/价值）。

## Critical / Warning

**Critical**

| ID | 通过条件 |
|---|---|
| C1 | `feishu.doc_token` 可 fetch |
| C2 | 契约 unit / MODULE-N 在飞书与本地按语义对齐 |
| C3 | 每 MODULE 有说明、验收、原型锚点或「无原型（原因）」 |
| C4 | Feature 清单中的 MODULE 列与详情中的 MODULE-N 一致 |
| C5 | 进开发前/T4：各 MODULE 意图一致（允许措辞差） |
| C6 | **见上方适用条件**：无 `narrative.*`；契约展示序号未为「补洞」而重排 |
| C7 | T4：相对 last_synced 无未推送契约改动，且非 fail |

**Warning**

| ID | 项 |
|---|---|
| W1 | 评审前阶段的语义差异（同 C5，阶段降级） |
| W2 | 飞书契约区连续正文 >6 行 |
| W3 | last_synced 过旧或 revision 漂移 |
| W4 | 声明有原型但锚点失效 |
| W5 | 飞书讲解层（背景/价值）仍为占位 |

阶段：评审前 C5→W1 且**不跑 C6**；进开发前 / commit 前 / qa-spec：C5 与 C6 均为 critical。

## 流程

### Step 0：范围

确认需求目录；确认阶段（评审前 / 进开发前）。

### Step 1：绑定与漂移

- 无 token → C1 fail，提示先 `/prd-feishu-sync create`
- 飞书契约超前未 reconcile → 进开发前 critical；评审前 warning
- 本地新于 last_synced 未 push → 进开发前/T4 要求先 `/prd-publish` 或 `push`

### Step 2：拉取与比对

1. 完整读本地 `prd.md`
2. `lark-cli docs +fetch`（优先 user；失败则标注，T4 视为未通过）
3. 按 chapter-map **语义定位**后跑 C/W；`narrative.*` diff 跳过
4. 语义 B：逐 MODULE 意图比对

飞书回写时：定位 `[PRD-SYNC:CONSISTENCY:v1:BEGIN]…END`（或历史「一致性校验结果」行），局部替换；禁止整篇 overwrite。若区缺失则在文档末尾插入整段再写入结论。

### Step 3：输出

1. 写入 `prototypes/prd-consistency-check-YYYY-MM-DD.md`（同日覆盖）
2. 更新 `metadata.consistency`：`status`（`pass`/`warn`/`fail`）/ `checked_at` / `report_path` / `source_commit`
3. **覆盖**飞书 CONSISTENCY 区（替换 create 时的「⏳ 未校验」占位）为最新结论：

```text
[PRD-SYNC:CONSISTENCY:v1:BEGIN]
一致性校验结果：✅|⚠️|❌ · YYYY-MM-DD
报告：<路径>
对应 commit：<sha 或 工作区未提交>
说明：由 /prd-consistency-check 机器维护；请勿手改
[PRD-SYNC:CONSISTENCY:v1:END]
```

映射：无 critical 且无未跳过 warning → ✅ + `pass`；仅 warning → ⚠️ + `warn`；有 critical → ❌ + `fail`。

4. 回读确认飞书已不再显示「⏳ 未校验」（除非本次未能写入飞书，则对话标明失败且本地 status 不得伪造成 pass）。
5. 对话紧凑摘要；critical → 明确阻断 confirmed / 提交 / qa-spec

### Step 4：warning 跳过

仅 warning 可跳过并留痕；critical 不可跳过。

## 报告模板字段

- 需求目录、阶段、飞书 URL、时间、commit
- 总体结论
- 逐条 ID / 等级 / 状态 / 摘要 / 证据（证据须写 unit key + 命中标题，不只写序号）
- 已跳过 warning
- 建议下一步

## 协作

| 命令 | 关系 |
|---|---|
| `/prd-feishu-sync` | 推送/回收 |
| `/prd-publish` | 编排 sync→本技能 |
| `/pm-spec` | confirmed 前须无 critical |
| `/qa-spec` | 启动前读 `consistency.status`，fail 默认阻断 |
