---
name: pm-spec
description: 多轮编写并更新本地 prd.md。先提示原型和飞书差异。写完后二次确认并引导 /prd-publish。不在本命令自动预检、校验或推飞书。
---

# /pm-spec

编写或更新本地 `prd.md`。每一轮先按三端协议提示原型、飞书文档和 `prd.md` 的差异，用户确认前不写另外两端。

写正文前先调用 CodeWiki `search_wiki`。默认不跑 `/prd-risk`、不跑 `/prd-check`、不 push。工作区改完 `prd.md` 后停住，二次确认并引导 `/prd-publish`。同一句话里说发布也不立刻进入发布。本地已经写完后，用户再说「同步到飞书」才改走 `/prd-publish`。

不在本命令里把 `prd.status` 设为 `confirmed`。

详见技能 `pm-spec`。
