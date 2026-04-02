# add-workflow-gate-rules

## Why

fe-specflow 和 be-specflow 插件的工作流中，Agent 存在跳步问题：

1. **跳过 brainstorming 直接写 OpenSpec 制品**：用户放行后，Agent 不正式调用 `superpowers:brainstorming` 就直接创建 `proposal.md` / `specs/` / 业务代码
2. **跳过 OpenSpec 直接改代码**：brainstorming 确认后，Agent 跳过 `design-to-opsx` 落盘步骤，直接修改业务代码
3. **tasks.md 不符合 TDD 格式要求**：缺少 TDD 执行约束头部模板、缺少每个 task 的测试要点、缺少测试分层说明

根因：当前所有约束都写在 `dev-workflow/SKILL.md`（400+ 行）中，依赖 Agent 主动记忆并遵守。LLM 对长文本存在"中间遗忘"效应，且"快速完成任务"的本能会覆盖流程纪律。

## What Changes

在两个插件已有的 `rules/dev-workflow.mdc` 文件**顶部**追加硬门禁指令。利用 Cursor Rules 的 glob 触发机制——Agent 触碰匹配文件时 Rule 被**平台自动注入上下文**——在 Agent 即将违规的那一刻拦截它。

**不新增文件**，不修改 Skill 或 Command，仅在现有 Rule 开头追加 5-10 行门禁逻辑。

### 具体变更

- `plugins/fe-specflow/rules/dev-workflow.mdc`：顶部追加前端门禁指令
- `plugins/be-specflow/rules/dev-workflow.mdc`：顶部追加后端门禁指令

### 门禁内容

两条核心拦截规则：

1. **OpenSpec 写入门禁**：写入 `openspec/changes/**` 前，必须确认本对话中已正式 Read 并遵循 `superpowers:brainstorming` 流程、灰区讨论已完成或声明跳过、用户已明确放行。不满足则停止写入
2. **业务代码写入门禁**：修改业务代码（前端 `.vue/.ts/.tsx` 等，后端 `.go/.proto` 等）前，必须确认 `tasks.md` 已存在且用户已确认、当前 task 遵循 TDD。不满足则停止修改

## Capabilities

### Modified Capabilities

- `workflow-gate-enforcement`: 在现有 `dev-workflow.mdc` Rule 中增加文件写入级别的门禁拦截，补充原有的流程意识描述

## Impact

- **前端插件**（fe-specflow）：`rules/dev-workflow.mdc` 顶部追加门禁，glob 不变
- **后端插件**（be-specflow）：`rules/dev-workflow.mdc` 顶部追加门禁，glob 不变
- **用户体验**：无感知变化——Rule 在后台自动触发，不增加用户操作步骤
- **依赖**：无新依赖

## References

- 问题截图：Agent 自认跳步的对话记录
- 现有 Rule：`plugins/fe-specflow/rules/dev-workflow.mdc`、`plugins/be-specflow/rules/dev-workflow.mdc`

## Decisions

- **不拆分 Skill 文件**（方向 A）：改动大、维护成本高，且问题根因不在"文件太长记不住"而在"记住了也跳过"
- **不增加阶段级 Command**（方向 C）：牺牲用户体验
- **不使用 always-applied Rule**（方向 H）：会污染非 specflow 对话
- **选择在现有 Rule 顶部追加**（方向 E 变体）：零新增文件、利用已有 glob、内容前置确保 Agent 注意力
