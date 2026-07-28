---
name: prd-publish
description: >-
  一键编排：先 /prd-feishu-sync push，再 /prd-consistency-check。
  Use when: 一键发布 PRD、发布到飞书并校验、prd-publish。
---

# /prd-publish — sync → check

## 流程

1. 定位需求目录与 `metadata.yaml`。
2. 解析 `--stage v5|v9|auto`（默认 `auto`）：
   - `auto`：若 `feishu.v9_synced` 或 `prd.stage` ∈ {`v9_pending`, `confirmed`} → `v9`，否则 `v5`
3. 执行 `/prd-feishu-sync push --stage <resolved>`（含该技能内的预览确认、**XML** 增量写、排版与回读；**若解析为 v9 且本地仍有 `narrative.*` → sync 会 REJECT**，此时停止，提示先完成 `/pm-spec` Step 4 瘦身）。
4. sync **失败**（含上述 REJECT）→ 停止；**不得**跑 check，不得写「通过」。
5. sync 成功后执行 `/prd-consistency-check`（默认进开发前阶段，除非用户指定评审前；结论以 **XML callout** 回写飞书）。
6. 汇总：飞书链接、是否 XML、sync 变更摘要、consistency 结论、报告路径。

## 约束

- 本技能只编排，不重复实现同步细则（XML / 禁裸 marker 以 `prd-feishu-sync` 为准）。
- critical fail → 整体失败。
- 9 稿确认后、git commit 前应执行本命令（或等价分步 sync+check）。
