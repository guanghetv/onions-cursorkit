---
name: onsf-finish
description: 检查 Onion SDD 变更的验证证据、任务状态与归档条件，并在门禁通过后自动归档 OpenSpec change。
---

# /onsf-finish

用于收束当前 Onion SDD 变更。它先检查产物、验证和风险是否满足归档条件，满足后自动执行 OpenSpec 归档并同步本地状态；不替代 Trellis 任务收尾，也不自动提交 git commit。

## 执行顺序

1. 定位当前 `openspec/changes/<change-id>/`。
2. 读取 `proposal.md`、`tasks.md`、`specs/**/spec.md`、验证记录和 `e2e-report.md`。
3. 对 Tier 0+/1，检查 mini/light change 的目标、任务和定向验证是否闭合。
4. 对 Tier 2+，读取 `skills/verify-change/SKILL.md` 的验收口径，检查 `e2e-report.md` 或等价验收证据。
5. 检查是否存在"带债项"：`proposal.md` 中 `## 带债项` 章节，逐条判断是否可接受。
6. 输出检查结论：是否可归档、仍需补哪些验证、是否存在已知风险、债项数。
7. **门禁通过后自动归档**：
   - 调用 `openspec archive <change-id>`。
   - 若 `openspec` CLI 不可用，使用等效手工归档：将 `openspec/changes/<change-id>/` 移动到 `openspec/changes/archive/<YYYY-MM-DD>-<change-id>/`，命名方式与 OpenSpec CLI 归档一致。
   - 归档失败时停止并报告，保留 `.onion-sdd/current.json` 中的 `active_change_id` 便于重试。
8. 归档成功后更新 `.onion-sdd/current.json`：`active_change_id` 置为 `null`，`phase` 置为 `idle`，`last_action` 记录归档时间。
9. 若当前 change 绑定 Trellis task，提示继续执行 `/trellis:finish-work` 完成 task 归档。

## 完成标准

- 变更目标清晰，相关任务已完成或明确标注不做。
- 验证命令与结果可追溯。
- Tier 2+ 默认需要 `e2e-report.md`；若使用等价验收证据，必须在最终输出中说明来源、覆盖范围和用户确认。
- 若存在 `e2e-report.md`，以其中 `## 验收结论` 为准。
- 门禁通过后自动归档 OpenSpec change；CLI 不可用时使用等效手工归档。
- 归档成功后 `.onion-sdd/current.json` 切回 `idle` 状态。
- 归档失败时输出明确错误，不破坏现有产物状态。

## 自动归档流程

### 触发条件

以下两个条件满足其一即可触发自动归档：

1. **正常通过**：所有门禁检查结论为"通过"，无阻塞项，无不可接受债项。
2. **带债归档**：存在可接受债项，且用户在本轮对话中明确同意带债归档；报告中必须已记录同意时间、债项摘要和 follow-up 位置。

### 执行方式

1. 优先调用 `openspec archive <change-id>`。
2. 若 `openspec` CLI 不可用（`which openspec` 失败或命令返回非零），进入降级路径：
   - 确认源目录 `openspec/changes/<change-id>/` 存在。
   - 确认目标目录 `openspec/changes/archive/<YYYY-MM-DD>-<change-id>/` 不存在；若存在，停止并提示用户处理冲突。
   - 使用文件系统移动（或复制后删除）完成等效归档。
3. 归档完成后检查目标目录存在且非空；若检查失败，按归档失败处理。

### 失败处理

- 任何失败都不回写 success 状态，不将 `current.json` 置为 `idle`。
- 保留 `active_change_id` 和 `phase=finish`，用户修复问题后可再次调用 `/onsf-finish` 重试。
- 输出包含：失败原因、当前 change 路径、建议的下一步命令、未损坏的现有产物路径。

## 状态同步

归档成功后，`.onion-sdd/current.json` 更新为：

```json
{
  "version": 1,
  "active_change_id": null,
  "tier": null,
  "phase": "idle",
  "last_action": "OpenSpec change <change-id> 已自动归档",
  "last_action_at": "2026-07-06T14:15:00+08:00",
  "upgrade_risk": false,
  "trellis_task": <保留原引用或 null>,
  "metrics": {
    "finished_at": "2026-07-06T14:15:00+08:00"
  }
}
```

若绑定 Trellis task，`trellis_task` 保留引用以便 `/trellis:finish-work` 继续；`active_change_id` 必须置为 `null`。

## Trellis 收尾分工

`/onsf-finish` 只负责 OpenSpec 归档，不替代 Trellis 任务收尾。

当当前 change 绑定 Trellis task 时，输出中同时给出两段建议：

1. OpenSpec：已自动归档完成；若失败，已在输出中说明原因。
2. Trellis：若代码提交完成且工作区干净，提示继续执行 `/trellis:finish-work`，由 Trellis 负责 task archive 和 workspace journal。

边界：

- 不把 OpenSpec 正文复制到 Trellis journal；journal 只写摘要、验证结果和下一步。
- 若 Trellis 不可用，仍可完成 `/onsf-finish` 自动归档，并提示用户手动记录任务收尾。
- 若 OpenSpec 未通过验收，不执行自动归档，也不提示 `/trellis:finish-work`。

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

- 门禁通过或用户明确同意带债归档时，自动执行 `openspec archive <change-id>`；CLI 不可用时使用等效手工归档；失败时停止并报告。
- 不自动提交 git commit。
- 不自动 push、创建 PR/MR 或归档 Trellis task。
- journal 只表示本次变更或会话摘要，不表示 Trellis 运行态。
