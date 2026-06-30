# 插件文档组件规范

## 当前事实

本仓库没有 React/Vue 组件源码。这里的“组件”指 Cursor 插件中的文档型组成部分：commands、rules、skills、README、模板文件。

## Command 文档

commands 是用户显式触发的入口。应包含：

- YAML frontmatter：`name`、`description`。
- 命令适用场景。
- 执行顺序。
- 约束和不做范围。

参考：
- `plugins/onion-sdd/commands/onion-plan.md`
- `plugins/workspace-specflow/commands/dev-start.md`

不要在 command 里塞完整实现细节；复杂流程应拆到 `skills/<name>/SKILL.md`。

## Skill 文档

skills 是可复用流程能力。应包含：

- YAML frontmatter：`name`、`description`。
- 输入与前置条件。
- 操作流程。
- 输出格式或模板。
- 失败/升级/停止条件。

参考：
- `plugins/onion-sdd/skills/tier-triage/SKILL.md`
- `plugins/workspace-specflow/skills/pm-spec/SKILL.md`

## Rule 文档

rules 是常驻或按 glob 加载的行为约束。应包含：

- YAML frontmatter：至少 `description`。
- 合理的 `globs` 或 `alwaysApply`。
- 明确的 MUST / SHOULD / MUST NOT 或等价中文约束。

参考：
- `plugins/common/rules/doc-writing-zh.mdc`
- `plugins/frontend/rules/commit-rule.mdc`
- `plugins/onion-sdd/rules/onion-sdd.mdc`

## README

README 面向插件使用者，优先说明：

- 插件定位。
- 命令入口。
- 安装/试用方式。
- 与其他机制的边界。
- 本期不做范围。

README 不应记录开发过程中的内部参考来源，避免让用户误解成运行时依赖。

## 常见错误

- command/skill/rule 缺 frontmatter。
- README 写成研发记录，而不是使用说明。
- 试点插件文档引用旧流程，导致独立性不清。
- 技能文档只有原则，没有可执行步骤或输出格式。
