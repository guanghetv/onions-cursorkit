---
name: prd-publish
description: 发布需求基线。本地文档已经写完，用户第二次确认发布，或单独说「同步到飞书」「推到飞书」时走这里。先预检，再增量写入，再 /prd-check。没有 critical 后写快照、版本表和 revision_id。warn 可以发布。
---

# /prd-publish

把当前需求发布成基线。用户说「同步到飞书」就是本命令，不是只推正文。

贴了绑定文档并说更新需求、改范围或这条先不做了，或从飞书拉回：先写入本地 `prd.md` 并停住，按 `three-way-sync.md` 二次确认。第二次明确同意之前，不要进入本命令。不使用 `--stage v5|v9`。

详见技能 `prd-publish`。
