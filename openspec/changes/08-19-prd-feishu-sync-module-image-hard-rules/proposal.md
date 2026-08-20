# 08-19-prd-feishu-sync-module-image-hard-rules

## 背景

- 用 Cursor 工作区同步飞书 PRD 时，MODULE「图示」列若使用 `docs +media-insert --selection-with-ellipsis`，图片会落到**顶层祖先块外**（上传成功 ≠ 位置正确）。
- 正确做法是对单元格内块做 `block_replace`，写入 `<img path="@./..."/>`（或 token 回填同一单元格）。
- 现有 `prd-feishu-sync` skill「图片」章节为软规程，未禁止单元格内 `media-insert`，也无写后位置自检。

## 变更

- 将「图片」升级为硬规则：决策树（表格/callout 内禁止 `media-insert`；正文独立配图可用）。
- 明确图示列写法：`path="@./..."`、2127 fallback、禁止降级到表格外插入。
- 写后自检新增第 7 条：格内 `<img>` 数量达标，同名图不得残留表格外。
- 对齐前置说明、读写步骤与 `push` 流程中的互指，避免 Agent 仍按旧习惯调用 `media-insert`。

## 影响范围

- 文件/模块: `plugins/workspace-specflow/skills/prd-feishu-sync/SKILL.md`
- 用户影响: 执行 `/prd-feishu-sync` 时，MODULE 图示写入路径与成功判定更严；错误位置会判同步失败

## 不做范围

- 不改 `lark-cli` / 运行时脚本
- 不改 `chapter-map.md`、其它 workspace-specflow skill
- 不做真实飞书端到端自动化（本次以 skill 规程与静态对照验证）

## 验证

- diff 对照参考 patch：`prd-feishu-sync-图片规则.patch` 的决策树 / 禁止项 / 自检第 7 条均已落地
- 静态检查：`SKILL.md` 中「图示」相关条文含「禁止 `media-insert`」与 `block_replace` + `path="@./`
- 前置第 3 条、读写步骤第 2 条、`push` MODULE 步骤与「图片硬规则」互指一致
