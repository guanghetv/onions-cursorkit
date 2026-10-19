---
name: prd-publish
description: 发布需求基线。用户说「同步到飞书」或「推到飞书」时也走这里。先预检，再增量写入，再 /prd-check。没有 critical 后写快照、版本表和 revision_id。warn 可以发布。
---

# /prd-publish

把当前需求发布成基线。用户说「同步到飞书」就是本命令，不是只推正文。不使用 `--stage v5|v9`。

详见技能 `prd-publish`。
