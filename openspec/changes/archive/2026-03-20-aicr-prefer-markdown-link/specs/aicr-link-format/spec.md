## ADDED Requirements

### Requirement: Markdown 链接为首选文件位置格式

审查报告中的文件位置 SHALL 优先使用 Markdown 链接格式 `[相对路径:行号](相对路径#L行号)`，纯文本格式 `相对路径:行号` 作为备选。

#### Scenario: SKILL.md 格式优先级调整
- **WHEN** 用户阅读 SKILL.md 中"文件位置格式（可点击）"部分
- **THEN** Markdown 链接格式 MUST 排在首位作为"推荐格式"，纯文本格式降级为"简写备选"

#### Scenario: SKILL.md 输出示例更新
- **WHEN** 用户阅读 SKILL.md 中"输出示例"部分
- **THEN** 主示例 MUST 使用 Markdown 链接格式，纯文本格式改为备选示例

#### Scenario: prompt_template.yml 示例同步
- **WHEN** prompt_template.yml 中的 system_prompt 输出格式说明和示例
- **THEN** 默认示例 MUST 使用 Markdown 链接格式 `[path:line](path#Lline)`，输出规则中的每条格式说明 MUST 以 Markdown 链接为主

#### Scenario: monorepo 兼容性说明
- **WHEN** 用户阅读文件位置格式部分
- **THEN** MUST 包含纯文本格式在 monorepo 中可能无法点击的说明
