---
name: req-new
description: 初始化新需求目录（中文目录名 + 英文 id slug）：飞书七章 prd 骨架、metadata、snapshots/、prototypes/、test/。默认引导 /pm-proto → /pm-spec-5。
---

# /req-new

初始化需求目录。支持飞书链接或一句话需求（`lark-cli` 优先）。

- **目录名**：清洗后中文（重名 `-2` / `-MMDD`）
- **metadata.id**：英文关键词 slug，创建后不变
- **prd.md**：飞书七章骨架

默认下一步：`/pm-proto`（可选）→ `/pm-spec-5` → 交互评审 → `/pm-spec`（9稿）。
