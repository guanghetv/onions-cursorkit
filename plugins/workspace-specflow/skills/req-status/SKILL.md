---
name: req-status
description: >-
  Use when user mentions: 需求进度/req-status/看看进度/需求状态/进度总览。
  Triggers in specs repo with requirements/ directory.
---

# /req-status — 需求进度总览

## 前置条件

- 当前项目是 specs 仓库（含 `requirements/` 目录）

## 流程

### Step 0: 确保 specs 仓库最新

提示用户 `git pull`。若 behind remote，**必须先提示 pull**。

### Step 1: 扫描需求层

扫描 `requirements/` 下所有子目录的 `metadata.yaml`（跳过 `snapshots` 等非需求目录；兼容中文目录名与既有英文目录）。

收集：

- 目录名（中文或英文）
- `metadata.name`、`metadata.id`（slug）
- `prd.status`、`prd.confirmed_at`
- `prd.baseline.revision_id`、`prd.baseline.snapshot`、`prd.baseline.published_at`
- 旧字段 `prd.stage`、`prd.v9.status`、`prd.v9.snapshot` 仅用于映射，不单列成稿次
- `prd.risk_precheck.last_result` / `last_checked_at`（若有）
- `consistency.status` / `checked_at`（这是 `/prd-check` 的结论，不是另一套检查）
- `test_spec.status`

### Step 2: 输出

```
需求进度总览

订单退款流程优化（id: order-refund-flow-opt）
  PRD:     pending
  基线:    —
  风险预检: 需调整 (2026-09-16T12:00+08:00) → prototypes/prd-risk-precheck.md
  发布前检查: unknown
  测试用例: pending

contract-subject-tree（id: contract-subject-tree）
  PRD:     confirmed (05-20)
  基线:    revision 681 → snapshots/prd-v9-2026-05-20.md
  测试用例: confirmed
```

**显示规则**：

- 主标识：`name` 或目录名（中文优先）
- 辅助：`id: <slug>`
- PRD：按 `references/templates.md` 的「旧稿次怎么读」判断已确认或未确认。不显示 5 稿 / 9 稿
- 基线：`prd.baseline`，否则回落到 v9/v5 快照。没有 revision 时写「快照仍在，revision 未记录」
- 风险预检：优先读 `prd.risk_precheck`（结论 + 时间 + 报告路径）；否则若存在 `prototypes/prd-risk-precheck.md` 则列路径与其中 `precheck_result`；都没有则 `—`
- 发布前检查：读 `consistency.status` 与 `checked_at`。没有该字段时写 `unknown`。这是 `/prd-check` 的结论

## 约束

- 只读，不修改文件
- `_archive/` 不在扫描范围（D16）
