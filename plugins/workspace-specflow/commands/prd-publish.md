---
name: prd-publish
description: 一键将 PRD 同步到飞书并做一致性校验（sync → check；飞书侧 XML）。
---

# /prd-publish

编排 `/prd-feishu-sync push`（**XML**）与 `/prd-consistency-check`（结论回写 callout）。可选 `--stage v5|v9|auto`（默认 auto）。

详见技能 `prd-publish`。