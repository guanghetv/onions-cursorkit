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
- `prd.stage`、`prd.v5.status`、`prd.v9.status`、`prd.status`
- `prd.v5.snapshot`、`prd.v9.snapshot`（如有）
- `test_spec.status`

### Step 2: 输出

```
需求进度总览

订单退款流程优化（id: order-refund-flow-opt）
  PRD 5稿:  confirmed (06-10) → snapshots/prd-v5-2026-06-10.md
  PRD 9稿:  pending
  测试用例: pending

contract-subject-tree（id: contract-subject-tree）  # 既有英文目录
  PRD 5稿:  —
  PRD 9稿:  confirmed (05-20)
  测试用例: confirmed
```

**显示规则**：

- 主标识：`name` 或目录名（中文优先）
- 辅助：`id: <slug>`
- 5稿/9稿：读 `prd.v5` / `prd.v9`；旧 metadata 无 v5/v9 时仅显示 `prd.status`

## 约束

- 只读，不修改文件
- `_archive/` 不在扫描范围（D16）
