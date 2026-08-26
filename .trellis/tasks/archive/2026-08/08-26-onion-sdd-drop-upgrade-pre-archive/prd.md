# 优化 onion-sdd：去掉 Trellis 升级推荐并在开任务前确认归档

## Goal

手动走 onion-sdd 时，使用者无需关心或维护 Trellis 项目版本，避免多人维护版本产生冲突；未安装只引导本地安装与 `trellis init`，并幂等写入当前平台 gitignore。新任务开始前确认归档上一轮变更：Trellis task 与对应 OpenSpec 成对归档；未装 Trellis 时仍归档上一轮 OpenSpec。`.onion-sdd/` 必须是纯本地状态。

## Background

- Trellis CLI / 模板版本由专门同学维护，onion-sdd 不应引导 `trellis upgrade` 或 `trellis update`。
- 「未安装 → 询问安装并 init + gitignore」保留；`.gitignore` 已有等价条目则跳过。
- Trellis task 与 OpenSpec change 是同一变更的两面，归档必须同步；仅有 OpenSpec 的仓库也要在开新任务前处理上一轮 spec。

## Requirements

- R1: 删除「已安装则检测更新并推荐 `trellis upgrade` / `trellis update`」的流程与全部用户可见文档。
- R2: 保留「Trellis 未安装 → 询问是否本地安装并 `trellis init` → 为本次 init 的平台追加整目录 gitignore（已有则跳过）」。
- R3: 手动入口、进入需求接入之前扫描遗留变更并请用户确认。有 Trellis 时 OpenSpec 与 task 成对归档；无 Trellis 时只归档上一轮 OpenSpec。拒绝或失败不阻塞新任务。
- R4: `/onsf-auto` 不触发安装询问，不升级，不扫描、不自动归档遗留任务。
- R5: `USAGE.md`、`README.md`、飞书 wiki、`DESIGN-SUPPLEMENT.md`、`CHANGELOG.md`、`onsf-auto.md` 与 skill 行为一致。
- R6: 不修改 Trellis 源码、`.trellis/scripts/**`、`.trellis/.runtime/**`。
- R7: onion-sdd 运行态写入前幂等确保仓库根 `.gitignore` 包含 `.onion-sdd/`；若 `.onion-sdd/` 下有已跟踪文件，清除 Git 跟踪记录但保留本地文件。

## Decisions

1. **成对归档**：归档 Trellis 必须同时归档对应 OpenSpec（目录仍在时先 `finish_check` + `openspec archive`）。OpenSpec 预检失败则整项跳过，避免只收 task。用户明确要求拆开时除外。
2. **无 Trellis**：安装询问被拒绝或失败后，仍扫上一轮 OpenSpec（优先 `current.json.active_change_id`；idle 再列出未归档 `openspec/changes/`），确认后只归档 spec。
3. **新开 `/onsf-plan`**：`current.json` 的上一轮 `active_change_id` 算遗留，不算「继续」。排除仅适用于本轮明确 continue 的同一 change。
4. **触发**：手动 `full-change` 入口；mini / light / `/onsf-auto` 不扫。
5. **gitignore / `.onion-sdd/`**：与既有约定相同。

## Out of scope

- Trellis 版本由专人维护的流程本身。
- 改 `finish_check.py` 的 hard/soft 门禁。
- 为遗留扫描新增 Python helper。

## Acceptance Criteria

- [ ] AC1: 当前流程不再询问或执行 `trellis upgrade` / `trellis update`。
- [ ] AC2: 未安装路径仍询问安装 + `trellis init`；gitignore 按平台整目录追加，已有条目不重复。
- [ ] AC3: Trellis 可用时，确认后先归档 bound OpenSpec 再归档 Trellis；二者保持同步。
- [ ] AC4: Trellis 不可用时，开新任务前仍列出上一轮未归档 OpenSpec 并经确认后归档。
- [ ] AC5: `/onsf-auto` 不询问安装、不升级、不归档遗留变更。
- [ ] AC6: 实现不修改 `.trellis/scripts/**`。
- [ ] AC7: `.onion-sdd/` 未被忽略时幂等追加；已跟踪时只清 index、保留本地文件。
