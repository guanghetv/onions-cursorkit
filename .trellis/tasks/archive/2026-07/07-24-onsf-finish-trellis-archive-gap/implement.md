# Implement Plan

> 0.1.3 已交付 A（提醒）+ B（诊断）。0.1.4 返工：A 从「提醒跑 /trellis:finish-work」改为「/onsf-finish 自动归档 Trellis task + journal」，B 保留为兜底。

## 交付物 A: Branch B 自动归档 Trellis task（0.1.4 返工）

- [x] 1.1 `commands/onsf-finish.md`：顶部说明新流程（commit 前置 → 单命令归档两边）；执行顺序加步骤 8 工作区干净检查、步骤 9 openspec archive + 自动 scoped commit、步骤 11 委托 trellis-finish-work。
- [x] 1.2 Branch B 段重写为「自动归档 Trellis task」：委托 `trellis-finish-work` skill 执行 `task.py archive` + `add_session.py`；不再要求用户手动跑 `/trellis:finish-work`。
- [x] 1.3 约束段放宽「不自动提交」为「仅自动提交 openspec 归档移动 scoped chore」；保留「不 push/PR」。
- [x] 1.4 `USAGE.md`、`docs/feishu-wiki-onion-sdd-usage.md` 流程图与链路同步为新顺序。
  - 验证：`rg -n "0\.1\.4|自动归档 Trellis|工作区干净检查|委托 .trellis-finish-work" plugins/onion-sdd`。
  - 补改（两份文档各 4 处旧流程残留）：§4 纪律段「不会自动 git commit」→ 改为「不自动提交代码 commit；仅自动提交 openspec 归档移动 scoped chore」；§6.6「再执行 /trellis:finish-work」→ 改为「/onsf-finish 一并自动归档 task + journal，无需再跑 /trellis:finish-work」；§8.1 journal 行 Trellis 列 → 改为「/onsf-finish 委托 trellis-finish-work skill 写入」；§8.5 命令对照「归档 Trellis task」行 Onion 列由「—」→ 改为「/onsf-finish（绑定 task 时自动委托）」。

## 交付物 B: stale-task 诊断（0.1.3 已交付，保留为兜底）

- [x] 2.1 `scripts/finish_check.py`：`check_stale_trellis_tasks(repo_root)` 已实现并接入 `run_check`。
- [x] 2.2 正/反/无 Trellis 三例已验证，exit code 不变。
  - 验证：`rg -n "check_stale_trellis_tasks" plugins/onion-sdd/scripts/finish_check.py`。

## 发版 0.1.4

- [x] 3.1 `CHANGELOG.md`：`[Unreleased]` 下新增 `[0.1.4] - 2026-07-24`，Changed/Added/Notes 记返工。
- [x] 3.2 `.cursor-plugin/plugin.json`：version `0.1.3` → `0.1.4`。
  - 验证：`python3 -m json.tool plugins/onion-sdd/.cursor-plugin/plugin.json` 且 version=0.1.4。

## 整体回归

- [x] 4.1 `python3 -m json.tool plugins/onion-sdd/.cursor-plugin/plugin.json` 通过。
- [x] 4.2 `rg -n "0\.1\.4|自动归档 Trellis|工作区干净检查|委托 .trellis-finish-work" plugins/onion-sdd` 抽查接线。

## 提交规划（Phase 3.4）

按 Conventional Commits + 简体中文拆：
- `feat(onion-sdd): onsf-finish Branch B 自动归档 Trellis task 与 journal`
- `docs(onion-sdd): USAGE 与飞书 wiki 同步 0.1.4 收尾流程顺序`
- `chore(onion-sdd): 发版 0.1.4`

## 回滚点

- A 出问题：把 Branch B 段换回「只 OpenSpec 归档 + 建议跑 /trellis:finish-work」即恢复 0.1.3 行为。
- B 出问题：移除 `check_stale_trellis_tasks` 调用即恢复；函数保留不影响。
