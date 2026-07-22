# 接入 Onion SDD AICR 提交门禁

## 目标

在 Onion SDD 的所有 Tier 提交边界接入团队 `aicr-local`，使已暂存的提交 diff 经过统一代码审查，同时不削弱 `trellis-check`、验证或验收门禁。

## 需求

- 用户明确要求提交后，先暂存待提交文件，再优先调用 `/cr` 或按 `aicr-local` Skill 审查暂存区。
- 无法使用 `aicr-local` 时，降级为 Agent 对暂存区 diff 自审，不阻塞用户已授权的提交。
- `trellis-check` 继续负责 lint、typecheck、测试、任务/Spec 对齐与跨层检查；`aicr-local` 不替代这些检查。
- `/onsf-auto` 的 `diff-review` 继续检查范围、产物和验证证据，但不得自动暂存或调用 `/cr`。
- 同一暂存 diff 经 AICR 审查后，只有修改并重新暂存时才需要复审。
- 规则、技能和面向用户的文档使用一致的提交前审查口径。

## 不做范围

- 不修改 `aicr-local` Skill、Trellis 源码或 `.trellis/scripts/**`。
- 不让 Onion SDD 自动执行 `git add`、`/cr`、`git commit`、push 或 PR/MR。
- 不用 AICR 替代 `verify-change`、E2E 或 OpenSpec 归档门禁。

## 验收标准

- [x] `plugins/onion-sdd/rules/onion-sdd.mdc` 定义用户授权后的暂存、AICR、修复复审和提交顺序。
- [x] `full-change` 明确 `trellis-check` 与提交前 AICR 的职责边界。
- [x] `auto-flow` 明确 `diff-review` 不会自动触发 AICR，并在准备提交时提示提交门禁。
- [x] README、USAGE 和飞书同步文档采用同一 AICR 提交路径。
- [x] 覆盖有 `aicr-local` 与无 `aicr-local` 的降级路径，且不保留相互冲突的提交前审查说明。
