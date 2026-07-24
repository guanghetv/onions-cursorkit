# onsf-finish Trellis 归档衔接补强

## Goal

补上 `/onsf-finish` 只归档 OpenSpec、不归档 Trellis task 留下的缺口，防止「OpenSpec 已归档但 Trellis task 长期 `in_progress`」的累积。两个交付物：

- **A**：强化 Branch B 提醒——bound 任务时 `/onsf-finish` 必须给出不可忽略的「Trellis 收尾待办」，指向 `/trellis:finish-work`，未提示不得宣称完成。
- **B**：stale-task 诊断——在 `/onsf-finish` 预检时扫描 `in_progress` Trellis task，标记其 bound OpenSpec change 已归档/缺失的「遗留任务」，输出 WARN。

## Background

`/onsf-finish` 只做 OpenSpec 归档 + `onion_state set --idle`；Branch B（Trellis 可用且 change 绑定 Trellis task）仅**建议**跑 `/trellis:finish-work`，不代劳。`/trellis:finish-work` 自带提交 sanity 门禁（工作区有本任务未提交代码则 bail），不宜被 `/onsf-finish` 绕过，故设计上分离。但只跑 `/onsf-finish` 就停的用户会留下 `in_progress` Trellis task；`/trellis:finish-work` Step 1 虽能 survey 并清理历史遗留任务，前提是用户终究跑一次。从不跑者持续累积。

## Requirements

### R1: 强化 Branch B 提醒（A，纯 command 输出）
- `commands/onsf-finish.md` Branch B 段：OpenSpec 归档成功后，输出必须含一条醒目的「Trellis 收尾待办」，点名当前绑定的 task 与建议命令 `/trellis:finish-work`。
- 该待办为收尾结论的必选项：未输出不得在结论里宣称「全部完成/已归档」；带债归档场景同样适用。
- 不在 `/onsf-finish` 内自动调用 `/trellis:finish-work`（保留其提交门禁边界）。

### R2: stale-task 诊断（B，onion-sdd 内实现）
- 在 `scripts/finish_check.py` 新增非致命 WARN：扫描 `repo_root/.trellis/tasks/*/task.json` 中 `status=in_progress` 的任务，读取 `meta.onion.change_id`，若其 bound OpenSpec change 已归档（位于 `openspec/changes/archive/`）或目录缺失，则视为 stale，输出 WARN 点名 task 与建议命令 `/trellis:finish-work`。
- 仅读 `.trellis/tasks/**/task.json` 与 `openspec/changes/**` 数据，**不修改** `.trellis/scripts/**` 或 Trellis 源码。
- WARN 不改变 exit code，不阻塞归档；与现有 hard/soft/convention-WARN 正交。

### R3: 发版 0.1.3
- CHANGELOG 新增 `[0.1.3]` 小节；plugin.json version 0.1.2 → 0.1.3。

## Acceptance Criteria

- [ ] `commands/onsf-finish.md` Branch B 含「Trellis 收尾待办」必选输出规则，点名 task 与 `/trellis:finish-work`。
- [ ] `finish_check.py` 对「1 个 in_progress task 且其 bound change 已归档」的仓库输出 stale WARN，exit code 不变。
- [ ] `finish_check.py` 对「in_progress task 的 bound change 仍存在（未归档）」的仓库不产生 stale WARN。
- [ ] `finish_check.py` 对无 Trellis（`.trellis/` 缺失）的仓库不产生 stale WARN，行为不变。
- [ ] 不修改 `.trellis/scripts/**` 或 Trellis 源码。
- [ ] CHANGELOG 与 plugin.json 版本一致为 0.1.3。

## Out of Scope

- 不让 `/onsf-finish` 自动调用 `/trellis:finish-work`（避免绕过其提交 sanity 门禁与 journal 记录）。
- 不修改 `.trellis/scripts/**`（如 `task.py list --stale`），诊断只在 onion-sdd 侧读数据。
- 不把 stale WARN 升级为 HARD FAIL。
- 不改 onion-sdd 之外插件。
