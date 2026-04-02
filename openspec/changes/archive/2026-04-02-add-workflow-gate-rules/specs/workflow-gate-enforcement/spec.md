# workflow-gate-enforcement

在 fe-specflow 和 be-specflow 插件的 `rules/dev-workflow.mdc` 顶部追加文件写入级门禁，利用 Cursor Rules 的 glob 触发机制在 Agent 即将违规时拦截。

## ADDED Requirements

### Requirement: OpenSpec 写入门禁

当 Agent 要创建或修改 `openspec/changes/` 下任何文件时，`dev-workflow.mdc` 被 glob 触发注入。门禁指令 SHALL 位于 Rule 文件的**最顶部**（description 和 globs 元数据之后、现有正文之前），确保 Agent 优先读取。Agent MUST 在写入前确认三项前置条件均满足，否则 MUST NOT 执行写入。

#### Scenario: brainstorming 未完成时阻止 OpenSpec 写入

- **WHEN** Agent 要创建或修改 `openspec/changes/**` 下的文件
- **AND** 本对话中未正式 Read 并遵循 `superpowers:brainstorming` 技能流程
- **THEN** Agent 停止写入操作
- **AND** 输出提示：需先完成 brainstorming 流程

#### Scenario: 灰区讨论未完成时阻止 OpenSpec 写入

- **WHEN** Agent 要创建或修改 `openspec/changes/**` 下的文件
- **AND** 灰区讨论既未完成也未声明跳过（含跳过条件说明）
- **THEN** Agent 停止写入操作
- **AND** 输出提示：需先完成灰区讨论或声明跳过理由

#### Scenario: 用户未放行时阻止 OpenSpec 写入

- **WHEN** Agent 要创建或修改 `openspec/changes/**` 下的文件
- **AND** 用户未用自然语言表示同意进入落盘阶段
- **THEN** Agent 停止写入操作
- **AND** 输出提示：需先获得用户明确放行

#### Scenario: 所有前置条件满足时允许 OpenSpec 写入

- **WHEN** Agent 要创建或修改 `openspec/changes/**` 下的文件
- **AND** brainstorming 已正式完成
- **AND** 灰区讨论已完成或已声明跳过
- **AND** 用户已明确放行
- **THEN** Agent 正常执行写入操作

### Requirement: 业务代码写入门禁

当 Agent 要修改业务代码文件时（前端：`.vue/.ts/.tsx/.jsx/.js/.css/.scss/.less`；后端：`.go/.proto`），`dev-workflow.mdc` 被同一 glob 触发注入。Agent MUST 在修改前确认 OpenSpec 制品已就绪，否则 MUST NOT 执行修改。

#### Scenario: tasks.md 不存在时阻止业务代码修改

- **WHEN** Agent 要修改业务代码文件
- **AND** 当前变更目录下不存在 `tasks.md`
- **THEN** Agent 停止修改操作
- **AND** 输出提示：需先完成 OpenSpec 制品（proposal → specs → tasks）

#### Scenario: tasks.md 未经用户确认时阻止业务代码修改

- **WHEN** Agent 要修改业务代码文件
- **AND** `tasks.md` 存在但用户尚未在对话中确认
- **THEN** Agent 停止修改操作
- **AND** 输出提示：需先展示 tasks 并获得用户确认

#### Scenario: 未遵循 TDD 时阻止业务实现代码修改

- **WHEN** Agent 要修改业务实现代码（非测试文件）
- **AND** 对应 task 的测试代码尚未先于实现代码写入
- **THEN** Agent 停止修改操作
- **AND** 输出提示：需先编写测试代码（TDD 红灯阶段）

#### Scenario: 所有前置条件满足时允许业务代码修改

- **WHEN** Agent 要修改业务代码文件
- **AND** `tasks.md` 存在且已获用户确认
- **AND** 当前 task 的测试已先于实现写入（或该 task 为纯配置/无需测试）
- **THEN** Agent 正常执行修改操作

### Requirement: 门禁指令位置与格式

门禁指令 SHALL 在 Rule 文件中位于 YAML 元数据（`---` 块）之后、现有正文之前，以确保 LLM 优先注意。门禁指令 MUST NOT 删除或修改现有 Rule 的任何内容。

#### Scenario: 门禁指令不影响现有 Rule 内容

- **WHEN** 门禁指令被追加到 `dev-workflow.mdc`
- **THEN** 现有的流程阶段、状态推断、关键约束等内容保持不变
- **AND** 门禁指令位于 YAML 元数据之后的第一个 section

### Requirement: 前后端门禁内容适配

fe-specflow 和 be-specflow 的门禁逻辑相同，但文件类型描述 SHALL 按各自技术栈适配。

#### Scenario: 前端门禁引用前端文件类型

- **WHEN** 门禁指令写入 `plugins/fe-specflow/rules/dev-workflow.mdc`
- **THEN** 业务代码门禁中的文件类型描述为前端相关（`.vue/.ts/.tsx/.jsx/.js/.css/.scss/.less`）
- **AND** 灰区讨论引用"前端灰区"

#### Scenario: 后端门禁引用后端文件类型

- **WHEN** 门禁指令写入 `plugins/be-specflow/rules/dev-workflow.mdc`
- **THEN** 业务代码门禁中的文件类型描述为后端相关（`.go/.proto`）
- **AND** 灰区讨论引用"后端灰区"
