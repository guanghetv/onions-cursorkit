# Onion SDD AICR 提交门禁设计

## 职责边界

质量流程分为三个互补阶段：

1. `trellis-check`：实现后的工程质量检查，执行 lint、typecheck、测试，并对照任务、Spec 和跨层约定。
2. `verify-change`：依据 OpenSpec、QA 与接口契约进行验证和 E2E 验收。
3. `aicr-local`：用户授权提交后，审查已暂存的最终提交 diff。

`aicr-local` 仅替代提交边界的人工 diff 自审，不替代前两个阶段。`/onsf-auto` 的 `diff-review` 保持为范围、产物和验证证据自检，不进入 Git 暂存区。

## 提交流程

```text
实现与验证完成
  → 用户明确授权提交
  → 暂存本次待提交文件
  → aicr-local /cr（不可用时 Agent 审查暂存区）
  → 修复问题并重新暂存、复审
  → git commit
```

若首次审查后暂存区内容未变化，不重复执行 AICR。审查结论必须以当前暂存区为基线，不能用工作区未暂存 diff 替代。

## 变更边界

- 更新 Onion SDD 规则、Tier 2+ 完整流程和自动流程的职责说明。
- 更新 README、USAGE 与飞书同步使用文档中的提交步骤。
- 不改变 `aicr-local`、Trellis 或归档脚本；不新增运行时配置和 Hook。

## 兼容与降级

- 优先使用 `/cr`；slash command 不可用时读取并遵循 `aicr-local` 的 `SKILL.md`。
- 未安装 `aicr-local` 时，Agent 按同样的暂存区基线完成自审。
- 用户未授权提交时，不执行暂存、AICR 或 commit。
