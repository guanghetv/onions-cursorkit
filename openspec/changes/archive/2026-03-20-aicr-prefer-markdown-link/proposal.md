## Why

当前 `aicr-local` 技能的审查报告中，文件位置的**推荐格式**是纯文本格式（`src/utils/helper.ts:42`），Markdown 链接只作为备选。但在 monorepo 项目中（如 `apps/web/src/...`、`packages/shared/src/...`），纯文本格式在 Cursor 中无法正确解析为可点击链接，因为 IDE 无法确定路径相对于哪个子项目根目录。Markdown 链接格式（`[path:line](path#Lline)`）在所有项目结构中都能可靠工作，应作为首选推荐格式。

## What Changes

- 将 `SKILL.md` 中"文件位置格式（可点击）"部分的格式优先级调整：**Markdown 链接升级为首选推荐格式**，纯文本格式降级为简写备选
- 将 `SKILL.md` 中"输出示例"部分的主示例改为 Markdown 链接格式，纯文本格式改为备选示例
- 将 `assets/prompt_template.yml` 中的示例和指令同步更新，使用 Markdown 链接作为默认输出格式
- 补充说明纯文本格式在 monorepo 中可能失效的原因，帮助用户理解格式选择

## Capabilities

### New Capabilities

（无新增能力）

### Modified Capabilities

（无需修改 openspec/specs 中的现有能力，此变更仅涉及技能文档和模板的内部格式调整）

## Impact

- **文件变更**：
  - `.cursor/skills/aicr-local/SKILL.md` — "文件位置格式（可点击）"节 + "输出示例"节
  - `.cursor/skills/aicr-local/assets/prompt_template.yml` — system_prompt 中的输出格式说明和示例
- **行为变化**：审查报告的默认文件位置格式从纯文本 `path:line` 变为 Markdown 链接 `[path:line](path#Lline)`
- **兼容性**：Markdown 链接在非 Cursor 环境（如终端、纯文本查看器）中仍可读，显示为 `[path:line](path#Lline)` 文本，不影响可用性
- **无破坏性变更**：不涉及审查逻辑、规范文档、提示词结构或流程步骤的改动
