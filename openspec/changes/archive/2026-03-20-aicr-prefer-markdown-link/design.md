## Context

`aicr-local` 技能的审查报告使用纯文本格式 `path:line` 作为首选文件位置格式。在 monorepo 项目中，Cursor 无法通过纯文本路径正确定位文件，导致链接不可点击。Markdown 链接格式 `[path:line](path#Lline)` 在所有项目结构中均可靠工作。

涉及两个文件：`SKILL.md`（技能文档）和 `assets/prompt_template.yml`（提示词模板）。

## Goals / Non-Goals

**Goals:**
- Markdown 链接成为首选推荐格式，纯文本格式降级为备选
- 输出示例以 Markdown 链接为主示例
- prompt_template.yml 的示例与 SKILL.md 保持一致

**Non-Goals:**
- 不修改审查流程、规范文档或审查维度
- 不强制禁用纯文本格式（保留为备选）

## Decisions

1. **Markdown 链接作为首选**：`[src/utils/helper.ts:42](src/utils/helper.ts#L42)` 在所有环境（单项目、monorepo）中可靠跳转，纯文本格式仅在单项目中可靠。
2. **保留纯文本为备选**：部分用户或场景（如终端阅读）可能偏好简洁的纯文本格式，不强制移除。

## Risks / Trade-offs

- [Markdown 链接稍长] → 审查报告行宽略增，但可读性不受影响
- [非 Cursor 环境] → Markdown 链接在纯文本环境显示为原始文本，仍可读，不影响使用
