# Tasks: add-workflow-gate-rules

> **执行约束**
> - 每个 task 遵循 TDD: 写测试 → 验证失败 → 最小实现 → 验证通过
> - 完成有意义的 task 后 commit（**须用户确认**）

## 1. 前端插件门禁

- [x] 1.1 在 `plugins/fe-specflow/rules/dev-workflow.mdc` 顶部追加门禁指令（文件: `plugins/fe-specflow/rules/dev-workflow.mdc`）
      测试要点: 门禁指令位于 YAML 元数据之后、现有正文之前；现有内容未被修改；包含 OpenSpec 写入门禁和业务代码写入门禁两条规则；文件类型引用前端栈（`.vue/.ts/.tsx/.jsx/.js/.css/.scss/.less`）

## 2. 后端插件门禁

- [x] 2.1 在 `plugins/be-specflow/rules/dev-workflow.mdc` 顶部追加门禁指令（文件: `plugins/be-specflow/rules/dev-workflow.mdc`）
      测试要点: 门禁指令位于 YAML 元数据之后、现有正文之前；现有内容未被修改；包含 OpenSpec 写入门禁和业务代码写入门禁两条规则；文件类型引用后端栈（`.go/.proto`）

## 3. 验证

- [x] 3.1 对比验证两个 Rule 文件的门禁逻辑一致性和技术栈差异适配
      测试要点: 两份门禁的核心拦截逻辑相同；文件类型描述分别对应前端/后端；灰区讨论引用分别为"前端灰区"/"后端灰区"；现有 Rule 正文内容未被意外修改
