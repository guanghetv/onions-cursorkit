---
name: pm-spec
description: 9稿 PRD 定稿（交互评审后）：结构化增强、消除待定项、严格 AI Review；push v9 → consistency-check 通过后才 prd.status=confirmed。
---

# /pm-spec（9稿定稿）

交互评审后的 **9稿** 结构化增强 `prd.md`。须先 **Read 并遵循 `superpowers:brainstorming`**，确认待定项已决议、MODULE 与回归范围后，才可改写并执行 AI Review。

读取最新 `snapshots/prd-v5-*.md` 与当前 `prd.md` 做 5→9 差异摘要。禁止残留 `[待定]`。

**`v9_pending` 时机**：仅在 Step 4 **瘦身完成**（本地已无讲解层）后写入；脑暴/瘦身前不得写，以免中途误推 v9。

严格 AI Review（`ai-review-rubric.md`）。

**硬门禁（用户确认后必须按序；任一步失败禁止 confirmed）**：

1. `/prd-feishu-sync push --stage v9`（或 `/prd-publish --stage v9` 覆盖 1–2；本地仍有 narrative → REJECT）
2. `/prd-consistency-check`（进开发前）；存在 critical → **停止**
3. 成功后再：追加版本行 `9-n`、快照 `snapshots/prd-v9-<date>.md`、`prd.status = confirmed` / `prd.stage = confirmed`

完整规程见技能 `pm-spec`。

典型顺序：`/pm-spec-5` → 交互评审 → `/pm-spec`。
