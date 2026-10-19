---
name: prd-publish
description: 发布需求基线。必要时先做风险预检，再增量同步飞书并跑 /prd-check。通过后写入快照、版本表和 revision_id。第一次成功才把 prd.status 设为 confirmed。
---

# /prd-publish

发布当前需求基线。不使用 `--stage v5|v9`。

详见技能 `prd-publish`。
