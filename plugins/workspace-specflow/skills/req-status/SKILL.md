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

### Step 2: 输出

**按角色最终产出状态汇总**：

```
需求进度总览

example-feature-a (示例需求 A)
  PRD:      confirmed (MM-DD)
  测试用例:  pending

example-feature-b (示例需求 B)
  PRD:      pending
  测试用例:  pending
```

## 约束

- 只读操作，不修改任何文件
- `_archive/` 与 `requirements/` 同级，不在扫描范围内（决策 D16）
- 对方仓库不可访问时（未克隆），标记为"不可达"而非报错
