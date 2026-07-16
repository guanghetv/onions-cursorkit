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
