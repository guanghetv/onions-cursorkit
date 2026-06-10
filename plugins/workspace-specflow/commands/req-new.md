---
name: req-new
description: 初始化新需求目录：输入需求想法或飞书需求链接，创建 prd.md、metadata.yaml、prototypes/、test/ 等标准结构，并默认引导先执行 /pm-proto。
---

# /req-new

初始化一个新的需求目录。可直接输入需求想法，或贴上飞书需求文档链接（`lark-cli` 优先，`feishu-mcp` 兜底）提取标题和概要，创建标准目录结构（prd.md + metadata.yaml + prototypes/ + test/）。默认下一步执行 `/pm-proto`，再执行 `/pm-spec`。
