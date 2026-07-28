---
name: prd-consistency-check
description: 校验本地 prd.md 与飞书契约层一致性（结构+语义），落盘报告并以 XML 回写飞书「一致性校验」callout。禁止口头清单代替真跑。
---

# /prd-consistency-check

对当前需求执行契约层一致性校验；飞书结论区用 XML callout（心跳码 `prd-sync:consistency:v1`），禁止裸 marker。完整规程见技能 `prd-consistency-check`。

一键同步并校验请用 `/prd-publish`。
