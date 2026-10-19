# 实现计划

变更正文在 `openspec/changes/workspace-specflow-prd-flow-upgrade/`。按 `tasks.md` 的 1 到 6 节实现，不要把 OpenSpec 正文复制到这里。

## 顺序

1. 基线与稿次（`prd-baseline`）
2. 三端对齐（`three-way-sync`）
3. 写作规范落地到模板和 `/qa-spec`（`writing-and-qa`）
4. 产品变更技能（`prd-change-notify`）
5. 原型去占位（`proto-core`）
6. 核对已写入的 `rules/agent-hard-rules.mdc`（`agent-hard-rules`）

## 验证

- 按每个任务的验证点走读对应技能。
- 不推送远端，不执行 Multica 同步。

## 回滚

- 回退本变更的技能与规则文件。
- 已发布到飞书的需求正文不回滚。
- `6702435` 的写作规范提交单独保留。
