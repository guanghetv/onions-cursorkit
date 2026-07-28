---
name: req-new
description: 初始化新需求目录（中文目录名 + 英文 id slug）：飞书七章 prd 骨架、metadata、snapshots/、prototypes/、test/；目录创建后必须 /prd-feishu-sync create。
---

# /req-new

初始化需求目录。支持飞书链接或一句话需求（`lark-cli` 优先）。

- **目录名**：清洗后中文（重名 `-2` / `-MMDD`）
- **metadata.id**：英文关键词 slug，创建后不变
- **prd.md**：飞书七章骨架

**硬门禁（目录创建成功后必须执行）**：

1. 执行 `/prd-feishu-sync create`（XML 骨架 + 绑定写回 `metadata.feishu.*`）
2. create 失败 → **明确报错**，不得假装已绑定；提示修好环境后重跑 create
3. 用户已有飞书文档要接管 → 引导 `rebind`（须确认），禁止静默覆盖

完整规程见技能 `req-new` / `prd-feishu-sync`。

默认下一步：`/pm-proto`（可选）→ `/pm-spec-5` → 交互评审 → `/pm-spec`（9稿）。
