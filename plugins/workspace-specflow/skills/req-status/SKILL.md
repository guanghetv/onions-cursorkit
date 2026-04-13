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

提示用户在 specs 仓库目录执行 `git pull`，确保查看的进度数据是团队最新版本。可通过 `git status` 检测是否 behind remote，若 behind 则**必须先提示 pull**。

### Step 1: 扫描需求层

扫描 `requirements/` 下所有需求目录的 `metadata.yaml`。

收集每个需求的：
- 需求名称和 ID
- prd 状态（pending / confirmed）
- 测试 spec 状态（pending / confirmed）
- 关联的 changes 列表

### Step 2: 扫描执行层（可选）

如果 `metadata.yaml` 中有 `changes` 字段，通过 `workspace-repos.json` 解析各仓库路径，扫描对应的 `openspec/changes/<change-id>/` 目录。

推断 change 进度：
- 无 change 目录 → 未开始
- 有 `proposal.md` 无 `tasks.md` → 设计中
- 有 `tasks.md` → 统计完成/总数
- 有 `e2e-report.md` → 待归档
- change 已归档 → 完成

### Step 3: 输出

**按角色最终产出状态汇总**：

```
需求进度总览

example-feature-a (示例需求 A)
  PRD:      confirmed (MM-DD)
  测试用例:  pending
  开发:
    frontend-app  tasks 3/7
    backend-api   tasks 5/8

example-feature-b (示例需求 B)
  PRD:      pending
  测试用例:  pending
  开发:     未开始
```

## 约束

- 只读操作，不修改任何文件
- `_archive/` 与 `requirements/` 同级，不在扫描范围内（决策 D16）
- 对方仓库不可访问时（未克隆），标记为"不可达"而非报错
