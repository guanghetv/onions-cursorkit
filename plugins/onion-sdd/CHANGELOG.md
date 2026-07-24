# Changelog

本文件记录 `onion-sdd` 插件的版本变更。格式参考 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)，版本号遵循 [Semantic Versioning](https://semver.org/lang/zh-CN/)。

## 发版约定

每次发布新版本时，请同步完成：

1. 在 `CHANGELOG.md` 顶部 `## [Unreleased]` 下整理本次变更，并新增 `## [x.y.z] - YYYY-MM-DD` 小节。
2. 更新 `.cursor-plugin/plugin.json` 的 `version` 字段（须与 CHANGELOG 最新版本一致）。
3. 若能力摘要有变化，视情况更新 `plugin.json` 的 `description` 或 `.cursor-plugin/marketplace.json` 中对应条目。
4. push 到 onions-plugins 源仓库后，团队成员在 Cursor 插件市场更新即可获取新版本。

> Cursor 插件市场**不会**自动读取本文件展示 release notes；CHANGELOG 供团队查阅，必要时可在飞书 wiki 或 README 引用要点。

## [Unreleased]

## [0.1.1] - 2026-07-24

### Added

- `scripts/onion_state.py`：写入 `current.json` 时自动确保 `.onion-sdd/` 已在根 `.gitignore` 中（幂等；命中 `.onion-sdd/` 或 `.onion-sdd` 则跳过，追加时在 stderr 提示一行）。`.onion-sdd/current.json` 为本地运行态兜底指针，不应同步到仓库。

## [0.1.0] - 2026-07-17

### Added

- 提交前 AICR 门禁：用户明确授权提交后，先暂存目标文件，再优先用 `aicr-local` 的 `/cr` 审查最终暂存 diff；slash command 不可用时按该 Skill 审查；未安装或不可用时降级为 Agent 自审暂存区。
- 规则层明确 `trellis-check`（工程质量）与 `aicr-local`（提交前 diff 审查）的职责边界；同一暂存 diff 未变化时不复审，修复后须重新暂存并复审。

### Changed

- `full-change` / `auto-flow` / `onsf-continue`：提交前审查口径与规则对齐；`/onsf-auto` 的 `diff-review` 仍不自动暂存或调用 `/cr`。
- `README.md`、`USAGE.md`、飞书同步文档：Commit review 步骤统一为「授权 → 暂存 → AICR/降级自审 → commit」。

## [0.0.4] - 2026-07-10

### Added

- Tier 2+/3 进入 `full-change` 时，Trellis 已安装则检测 `Trellis update available`；询问用户后可执行 `trellis upgrade` + `trellis update`（`/onsf-auto` 不触发）。

### Changed

- `USAGE.md`、`README.md`：「自动询问安装」扩展为「自动询问安装与更新」，说明触发时机与边界。

## [0.0.3] - 2026-07-09

### Added

- `scripts/onion_state.py`：运行态 helper（Trellis `meta.onion` 主写 + `current.json` 镜像/兜底）。
- `scripts/finish_check.py`：`/onsf-finish` 归档前置预检（tasks 未完成项、Tier 2+ 验收结论、可选 `openspec validate`）。
- Tier 0++ 超时可见：`tier0pp_deadline` 扫描与逾期硬提示。
- 开发前分支门禁：受保护分支拦截、跨 change 分支复用检测。

### Changed

- `/onsf-finish`：门禁通过后自动归档 OpenSpec change。
- Trellis 缺失时 Tier 2+/3 交互式安装初始化；未绑定 task 时 `/onsf-finish` 自动写 journal 与 spec 积累判断。
- 各 `/onsf-*` 命令与 skills 接线 `onion_state.py` 硬纪律。

## [0.0.1] - 2026-06-25

### Added

- 初始发布：`/onsf-plan`、`/onsf-fix`、`/onsf-tweak`、`/onsf-continue`、`/onsf-finish`、`/onsf-auto`。
- Tier 0–3 分级与 mini/light/full OpenSpec 流程。
- `trellis-adapter`：OpenSpec ↔ Trellis task metadata 同步。
- 注册至 onions-plugins 插件市场。
