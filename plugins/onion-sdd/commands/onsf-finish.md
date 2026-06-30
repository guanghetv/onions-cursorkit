---
name: onsf-finish
description: 检查 Onion SDD 变更的验证证据、任务状态与归档条件。
---

# /onsf-finish

用于收束当前 Onion SDD 变更。它不替用户执行归档或提交，而是检查产物是否足够、验证是否可信、是否可以提示用户进入下一步。

## 执行顺序

1. 定位当前 `openspec/changes/<change-id>/`。
2. 读取 `proposal.md`、`tasks.md`、`specs/**/spec.md`、验证记录和 `e2e-report.md`。
3. 对 Tier 0+/1，检查 mini/light change 的目标、任务和定向验证是否闭合。
4. 对 Tier 2+，读取 `skills/verify-change/SKILL.md` 的验收口径，检查 `e2e-report.md` 或等价验收证据。
5. 检查是否存在"带债项"：`proposal.md` 中 `## 带债项` 章节，逐条判断是否可接受。
6. 输出是否可归档、仍需补哪些验证、是否存在已知风险、债项数。

## 完成标准

- 变更目标清晰，相关任务已完成或明确标注不做。
- 验证命令与结果可追溯。
- Tier 2+ 默认需要 `e2e-report.md`；若使用等价验收证据，必须在最终输出中说明来源、覆盖范围和用户确认。
- 若存在 `e2e-report.md`，以其中 `## 验收结论` 为准。
- 如需归档，只提示用户在终端执行 `openspec archive <change-id>`。

## Trellis 收尾分工

`/onsf-finish` 只判断 Onion/OpenSpec 变更是否满足归档条件，不替代 Trellis 任务收尾。

当当前 change 绑定 Trellis task 时，输出中同时给出两段建议：

1. OpenSpec：若验收通过，只提示用户执行 `openspec archive <change-id>`，不自动执行。
2. Trellis：若代码提交完成且工作区干净，提示继续执行 `/trellis:finish-work`，由 Trellis 负责 task archive 和 workspace journal。

边界：

- 不把 OpenSpec 正文复制到 Trellis journal；journal 只写摘要、验证结果和下一步。
- 若 Trellis 不可用，仍可完成 `/onsf-finish` 判断，并提示用户手动记录任务收尾。
- 若 OpenSpec 未通过验收，不提示 `/trellis:finish-work`，先补验证或修复问题。

## 带债归档规则

可接受债项：
- `tasks.md` 中已明确标注不做，且 `proposal.md` 的不做范围有说明。
- Tier 0+/1 的部分验证缺口，且已在验证结果中标注。
- 已知兼容性问题，且有 follow-up issue 或明确后续处理项。

不可接受债项：
- Tier 2+ 跳过 E2E 或等价验收门禁。
- 接口契约、权限、安全、支付、资金相关风险未验证。
- 升级红线未处理却仍尝试归档。

带债时必须在 `proposal.md` 增加 `## 带债项`，并在输出中写明债项数量与 follow-up 位置。

## 约束

- 不自动执行 `openspec archive`。
- 不自动提交 git commit。
- journal 只表示本次变更或会话摘要，不表示 Trellis 运行态。
