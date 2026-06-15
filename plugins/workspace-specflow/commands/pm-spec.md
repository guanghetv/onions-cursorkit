---
name: pm-spec
description: 9稿 PRD 定稿（交互评审后）：结构化增强、消除待定项、严格 AI Review；确认后 prd.status=confirmed，解锁 qa-spec/dev-start。
---

# /pm-spec（9稿定稿）

交互评审后的 **9稿** 结构化增强 `prd.md`。须先 **Read 并遵循 `superpowers:brainstorming`**，确认待定项已决议、MODULE 与回归范围后，才可改写并执行 AI Review。

读取最新 `snapshots/prd-v5-*.md` 与当前 `prd.md` 做 5→9 差异摘要。禁止残留 `[待定]`。

严格 AI Review（`ai-review-rubric.md`）。确认后快照 `snapshots/prd-v9-<date>.md`，`prd.status = confirmed`。

典型顺序：`/pm-spec-5` → 交互评审 → `/pm-spec`。
