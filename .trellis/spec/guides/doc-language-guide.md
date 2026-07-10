# 文档语言规范

> **目的**：统一 `.trellis/spec/`、插件文档、OpenSpec 产物与任务产物的语言口径，避免「半中半英」或整篇英文说明。

---

## 强制约定

| 项 | 要求 |
|----|------|
| **正文** | 使用**简体中文**表达（标题、段落、列表、表格说明、检查清单） |
| **专有名词 / 代码** | 保留英文原文：命令、路径、标识符、API、配置键、URL、包名 |
| **代码块** | 代码与 shell 命令保持原样；注释可用中文 |
| **模板章节名** | 若沿用英文模板标题（如 `Scope / Trigger`），应改为中文等价标题，或「中文标题（English）」；**禁止**整节说明仍用英文 |

本约定与仓库 Cursor 规则「文档正文使用中文」一致，并**明确覆盖** `.trellis/spec/guides/**`（不得因上游 Trellis 模板是英文而继续用英文写新内容）。

## 适用范围

- `.trellis/spec/**`（含 `guides/`、`backend/`、`frontend/`）
- `plugins/**` 下的 `README.md`、`USAGE.md`、`SKILL.md`、命令文档
- `openspec/changes/**` 的 `proposal.md` / `tasks.md` / `specs/**/spec.md`
- `.trellis/tasks/**` 的 `prd.md` / `design.md` / `implement.md`

## 正确 / 错误示例

```markdown
<!-- ✅ 正确：正文中文，标识符英文 -->
阶段切换必须调用 `onion_state.py`；有绑定 Trellis task 时主写 `meta.onion`。

<!-- ❌ 错误：正文整句英文 -->
Stage transitions must call `onion_state.py`.

<!-- ❌ 错误：翻译专有名词 -->
请运行 `npm run build`，并附上吉特哈布仓库链接。
```

## 维护纪律

- **新增** spec / guide / OpenSpec 产物：默认中文正文。
- **修改**既有英文 guide：顺手改为中文，或至少把本次触及的章节改成中文，不要再追加英文段落。
- **`trellis update` 可能覆盖**部分模板文件：若上游重新写入英文，以本规范为准在本仓库改回中文，并避免在英文段落上继续叠英文。

## 与 Thinking Guides 的关系

`guides/` 是「写代码前要想什么」的检查清单，面向本仓库中文协作；**不是**保留上游英文原文的镜像。索引与各 guide 正文均应中文。
