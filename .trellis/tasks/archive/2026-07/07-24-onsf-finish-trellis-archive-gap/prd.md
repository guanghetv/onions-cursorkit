# onsf-finish Trellis 归档衔接补强

## Goal

补上 `/onsf-finish` 只归档 OpenSpec、不归档 Trellis task 留下的缺口，防止「OpenSpec 已归档但 Trellis task 长期 `in_progress`」的累积。两个交付物：

- **A**：强化 Branch B 提醒——bound 任务时 `/onsf-finish` 必须给出不可忽略的「Trellis 收尾待办」，指向 `/trellis:finish-work`，未提示不得宣称完成。
- **B**：stale-task 诊断——在 `/onsf-finish` 预检时扫描 `in_progress` Trellis task，标记其 bound OpenSpec change 已归档/缺失的「遗留任务」，输出 WARN。

## Background

`/onsf-finish` 只做 OpenSpec 归档 + `onion_state set --idle`；Branch B（Trellis 可用且 change 绑定 Trellis task）仅**建议**跑 `/trellis:finish-work`，不代劳。`/trellis:finish-work` 自带提交 sanity 门禁（工作区有本任务未提交代码则 bail），不宜被 `/onsf-finish` 绕过，故设计上分离。但只跑 `/onsf-finish` 就停的用户会留下 `in_progress` Trellis task；`/trellis:finish-work` Step 1 虽能 survey 并清理历史遗留任务，前提是用户终究跑一次。从不跑者持续累积。

## Requirements

### R1: Branch B 自动归档 Trellis task（A，返工 0.1.3 的「仅提醒」）
- 流程顺序改为：**代码 commit（Phase 3.4）→ `/onsf-finish`（单命令归档两边）**。
- `commands/onsf-finish.md` Branch B：finish_check → 工作区干净检查（脏则 bail，不归档）→ `openspec archive` → **自动 commit openspec 归档移动**（scoped chore）→ `onion_state set --idle` → 委托 `trellis-finish-work` skill 归档 bound task + journal。
- 「不自动提交 git commit」放宽为：仅自动提交 openspec 归档移动这一项 scoped chore；代码 commit 仍前置由 Phase 3.4 完成；不自动 push/PR。
- `/trellis:finish-work` 保留供纯 Trellis 任务使用；onion-sdd bound change 不再需要它。

### R2: stale-task 诊断（B，onion-sdd 内实现）
- 在 `scripts/finish_check.py` 新增非致命 WARN：扫描 `repo_root/.trellis/tasks/*/task.json` 中 `status=in_progress` 的任务，读取 `meta.onion.change_id`，若其 bound OpenSpec change 已归档（位于 `openspec/changes/archive/`）或目录缺失，则视为 stale，输出 WARN 点名 task 与建议命令 `/trellis:finish-work`。
- 仅读 `.trellis/tasks/**/task.json` 与 `openspec/changes/**` 数据，**不修改** `.trellis/scripts/**` 或 Trellis 源码。
- WARN 不改变 exit code，不阻塞归档；与现有 hard/soft/convention-WARN 正交。

### R3: 发版 0.1.3
- CHANGELOG 新增 `[0.1.3]` 小节；plugin.json version 0.1.2 → 0.1.3。

## Acceptance Criteria

- [ ] `commands/onsf-finish.md` Branch B 描述新顺序：commit 前置 → 单命令归档 OpenSpec + Trellis task + journal，含工作区干净 bail、openspec 归档移动自动 commit、委托 trellis-finish-work。
- [ ] 「不自动提交」约束放宽说明：仅 openspec 归档移动 scoped chore 自动 commit；代码 commit 仍前置；不 push/PR。
- [ ] `/trellis-finish-work` 仍保留供纯 Trellis 任务使用。
- [ ] `finish_check.py` 对「1 个 in_progress task 且其 bound change 已归档」输出 stale WARN，exit code 不变（B 兜底，保留）。
- [ ] `finish_check.py` 对无 Trellis（`.trellis/` 缺失）的仓库不产生 stale WARN，行为不变。
- [ ] 不修改 `.trellis/scripts/**` 或 Trellis 源码。
- [ ] USAGE.md 与飞书 wiki 同步新流程顺序。
- [ ] CHANGELOG 与 plugin.json 版本一致为 0.1.4。

## Out of Scope

- 不自动 push、创建 PR/MR（代码 commit 仍由 Phase 3.4 前置完成；openspec 归档移动由 `/onsf-finish` 自动 scoped commit）。
- 不修改 `.trellis/scripts/**`（诊断只读数据；归档通过委托 `trellis-finish-work` skill 调用现有脚本，不修改）。
- 不把 stale WARN 升级为 HARD FAIL。
- 不改 onion-sdd 之外插件。
- 不让 `/onsf-finish` 接管纯 Trellis 任务的归档（无 OpenSpec change 的仍走 `/trellis:finish-work`）。
