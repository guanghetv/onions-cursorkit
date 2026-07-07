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
9. 判断 Trellis 可用性与当前 change 是否绑定 Trellis task，按分支 A/B/C 执行对应的 Trellis 收尾动作（见下方"Trellis 收尾分工"）。

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

`/onsf-finish` 只负责 OpenSpec 归档，不替代 Trellis 任务收尾。OpenSpec 归档成功（正常通过或带债归档均算成功）后，按以下分支处理 Trellis 相关动作：

### 判断依据

- **Trellis 是否可用**：`.trellis/scripts/add_session.py` 文件存在即视为可用；不要求 `.trellis/.developer` 已初始化——脚本内部的 `ensure_developer` 会自动完成初始化。
- **当前 change 是否绑定 Trellis task**：看 `.onion-sdd/current.json` 的 `trellis_task` 或 Trellis active task 的 `task.json.meta.onion.change_id` 是否指向当前 change。

### 分支 A：Trellis 不可用

保持现状：只更新 `.onion-sdd/current.json`，不提及 Trellis，不调用任何 Trellis 脚本或技能。

### 分支 B：Trellis 可用，且当前 change 绑定 Trellis task

保持现状，输出中给出两段建议：

1. OpenSpec：已自动归档完成；若失败，已在输出中说明原因。
2. Trellis：若代码提交完成且工作区干净，提示继续执行 `/trellis:finish-work`，由 Trellis 负责 task archive 和 workspace journal。

不在 `/onsf-finish` 内直接调用 `add_session.py`，也不额外加载 `trellis-update-spec`——绑定 task 时，整体会话已经在遵循 Trellis workflow.md 的 Phase 3.3（`trellis-implement -> trellis-check -> trellis-update-spec -> commit`），重复记录会导致 journal/spec 判断被记两次。

### 分支 C（新增）：Trellis 可用，且当前 change 未绑定 Trellis task

`/onsf-finish` 自身直接执行以下两个动作。两者都不涉及 Trellis task 的创建/启动/归档，不需要额外用户确认（沿用 OpenSpec 归档门禁本身作为确认点）：

1. **记录 journal**：调用 `.trellis/scripts/add_session.py`。
   - `--title`：优先取 `proposal.md` 的一级标题（去掉 `# ` 前缀）；取不到则用 change-id。
   - `--summary`：用 1-2 句话总结这次变更做了什么，可参考 `tasks.md` 完成情况或 `proposal.md` 的目标段落改写；**不得整段复制** `proposal.md`/`specs/**` 正文。
   - `--commit`：先跑 `git status --porcelain`；工作区干净则用 `git log -1 --format=%h` 取最近一次 commit hash 传入 `--commit`；不干净则不传该参数（脚本默认值 `-`，对应"(No commits - planning session)"语义）。
   - 不传 `--branch`、`--package`：由脚本按自身默认逻辑处理（git 自动探测分支；单仓库项目忽略 package）。
   - 使用脚本默认的 `auto_commit=True`，允许其对 `.trellis/workspace/**` 等安全路径做一次范围受限的 auto-commit。

2. **spec 积累判断**：加载 `trellis-update-spec` 技能（`.claude/skills/trellis-update-spec/SKILL.md`），对本次变更做一次"是否需要沉淀经验"的判断。
   - 判断素材来自当前 change 的 `proposal.md`、`tasks.md`、实现过程中的 diff/决策，不需要额外用户访谈。
   - 结论只有两种，且必须显式输出：
     - **无需更新**：一次性的实现细节，没有可复用的模式/约定/坑；输出中如实写"已判断，无需更新"。
     - **需要更新**：按该 skill 的模板（Design Decision / Convention / Pattern / Forbidden Pattern / Common Mistake / Gotcha）写入 `.trellis/spec/<package>/<layer>/` 对应文件，必要时同步该 layer 的 `index.md`。
   - 边界：只写"这次学到的可复用经验"，不写"这次变更做了什么"（那是 journal 的职责）；不把 OpenSpec `proposal.md`/`specs/**` 正文整段搬进 `.trellis/spec/`。

分支 C 完成后，输出中新增两行说明，例如：

```text
- Trellis journal: 已通过 add_session.py 记录本次变更（未绑定 Trellis task）
- Trellis spec 积累: 已判断，无需更新 / 已写入 .trellis/spec/<path>
```

### 三个分支共同的边界

- 不把 OpenSpec 正文复制到 Trellis journal 或 `.trellis/spec/`；journal 只写摘要、验证结果和下一步。
- 若 OpenSpec 未通过验收，不执行自动归档，三个分支的 Trellis 动作也都不执行。
- 分支 C 的记 journal、spec 积累判断都不是 task 创建/启动/归档操作，不受"需要创建/启动/归档 Trellis task"这类停止条件约束。

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
