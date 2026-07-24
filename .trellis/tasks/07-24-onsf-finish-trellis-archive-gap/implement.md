# Implement Plan

## 交付物 A: Branch B 提醒强化

- [ ] 1.1 `commands/onsf-finish.md` Branch B 段：补「输出必选项」规则——OpenSpec 归档成功后必须输出 `Trellis 收尾待办` 行，点名 task 与 `/trellis:finish-work`；未输出不得宣称完成；带债归档同样适用。
  - 验证：`rg -n "Trellis 收尾待办|/trellis:finish-work" plugins/onion-sdd/commands/onsf-finish.md`。

## 交付物 B: stale-task 诊断

- [ ] 2.1 `scripts/finish_check.py`：新增 `check_stale_trellis_tasks(repo_root) -> List[str]`（扫 `.trellis/tasks/*/task.json` 的 `in_progress` + `meta.onion.change_id`，bound change 已归档/缺失则 WARN）。
  - 验证：读现有结构；`python3 -c "import sys; sys.path.insert(0,'plugins/onion-sdd/scripts'); from finish_check import check_stale_trellis_tasks; from pathlib import Path; print(check_stale_trellis_tasks(Path('.')))"` 在 cursorkit 不报（当前 change 未归档）。
- [ ] 2.2 `run_check` 末尾接入：`stale_warns = check_stale_trellis_tasks(repo_root); if stale_warns: notes.extend(stale_warns)`。
  - 验证：`rg -n "check_stale_trellis_tasks" plugins/onion-sdd/scripts/finish_check.py`。
- [ ] 2.3 正例：造一个假仓库——`.trellis/tasks/07-01-foo/task.json`（status=in_progress, meta.onion.change_id=foo）+ `openspec/changes/archive/2026-07-01-foo/`（已归档），跑 `finish_check.py --repo-root <fake> --change-id <other> --tier 1`，确认 stale WARN 出现且 exit code 不变。
  - 验证：输出含 `Trellis task ... 仍为 in_progress` WARN。
- [ ] 2.4 反例：把 bound change 改为活跃（`openspec/changes/foo/` 存在），确认无 stale WARN。
- [ ] 2.5 无 Trellis 反例：`.trellis/` 缺失时不报、不崩。

## 发版 0.1.3

- [ ] 3.1 `CHANGELOG.md`：`[Unreleased]` 下新增 `[0.1.3] - <date>`，Added 记 A/B。
- [ ] 3.2 `.cursor-plugin/plugin.json`：version `0.1.2` → `0.1.3`。
  - 验证：`python3 -m json.tool plugins/onion-sdd/.cursor-plugin/plugin.json` 且 version=0.1.3。

## 整体回归

- [ ] 4.1 `python3 plugins/onion-sdd/scripts/finish_check.py --help` 正常。
- [ ] 4.2 `python3 -m json.tool plugins/onion-sdd/.cursor-plugin/plugin.json` 通过。
- [ ] 4.3 `rg -n "check_stale_trellis_tasks|Trellis 收尾待办|/trellis:finish-work" plugins/onion-sdd` 抽查接线。
- [ ] 4.4 ReadLints 检查 finish_check.py 无新增 lint 错误。

## 提交规划（Phase 3.4，待实现后）

按 Conventional Commits + 简体中文拆：
- `feat(onion-sdd): onsf-finish Branch B 强化 Trellis 收尾待办提醒`
- `feat(onion-sdd): finish_check 新增 stale Trellis task 诊断 WARN`
- `chore(onion-sdd): 发版 0.1.3`

## 回滚点

- A 出问题：删 `onsf-finish.md` Branch B 段新增的「输出必选项」规则即可恢复。
- B 出问题：移除 `check_stale_trellis_tasks` 调用即恢复；函数保留不影响。
