# Onion SDD 手动入口与本地运行态

规范手动 Tier 2+/3 开新任务时的 Trellis 边界，以及 `.onion-sdd/` 本地状态治理。

## MODIFIED Requirements

### Requirement: 手动入口不维护 Trellis 版本

系统 MUST 仅在手动 Tier 2+/3 入口检测 Trellis 是否可用；已可用时不得检查、询问或执行 Trellis 版本升级。

#### Scenario: Trellis 已可用

- **WHEN** 手动 Tier 2+/3 入口检测到 `.trellis/scripts/add_session.py`
- **THEN** 跳过安装流程
- **AND** 不读取版本用于升级判断，不推荐 `trellis upgrade` 或 `trellis update`
- **AND** 进入遗留变更扫描

#### Scenario: Trellis 未安装

- **WHEN** 手动 Tier 2+/3 入口未检测到 Trellis
- **THEN** 询问用户是否本地安装并执行 `trellis init`
- **AND** 仅为本次实际初始化的平台幂等追加 `.cursor/`、`.claude/` 或 `.codex/`
- **AND** 拒绝或失败不阻塞 Onion SDD
- **AND** 仍进入遗留变更扫描（仅 OpenSpec）

### Requirement: 开新任务前确认归档遗留变更

系统 MUST 在进入需求接入前扫描上一轮遗留变更，并仅在用户确认后归档。Trellis 与 OpenSpec 必须成对处理；无 Trellis 时只归档上一轮 OpenSpec。

#### Scenario: Trellis 可用且存在成对遗留

- **WHEN** 存在遗留 Trellis task 或其 bound OpenSpec 目录仍在
- **THEN** 列出 change_id 与 task
- **AND** 用户确认后先 `finish_check` 与 `openspec archive`，再 `task.py archive`
- **AND** OpenSpec 预检失败则整项跳过，不得只归档 Trellis（除非用户明确拆开）

#### Scenario: Trellis 不可用仅有 OpenSpec

- **WHEN** Trellis 未安装或用户拒绝安装
- **AND** 存在上一轮未归档 OpenSpec（优先 `current.json.active_change_id`；idle 则列出 `openspec/changes/` 未归档目录）
- **THEN** 列出候选并在确认后只归档 OpenSpec

#### Scenario: 新开 plan 与继续

- **WHEN** 入口为新的 `/onsf-plan`
- **THEN** 将 `current.json` 的上一轮 `active_change_id` 视为遗留
- **WHEN** 用户本轮明确 continue 同一 change
- **THEN** 不将该 change 列为遗留

#### Scenario: 用户拒绝或归档失败

- **WHEN** 用户未确认任何候选，或归档失败
- **THEN** 报告结果并继续新任务，不阻塞

#### Scenario: 非手动完整流程

- **WHEN** 入口为 mini、light 或 `/onsf-auto`
- **THEN** 不扫描也不归档遗留 Trellis 或 OpenSpec
- **AND** `/onsf-auto` 不触发 Trellis 安装询问

## ADDED Requirements

### Requirement: `.onion-sdd/` 始终保持本地状态

系统 MUST 在每次运行态写入前确保仓库根忽略 `.onion-sdd/`，并尽力清除该目录下已有的 Git 跟踪记录而不删除本地文件。

#### Scenario: 忽略规则不存在

- **WHEN** helper 即将写入状态
- **THEN** 在仓库根 `.gitignore` 幂等追加 `.onion-sdd/`
- **AND** 已有 `.onion-sdd` 或 `.onion-sdd/` 时不重复追加

#### Scenario: 状态文件已被 Git 跟踪

- **WHEN** `git ls-files -- .onion-sdd` 返回文件
- **THEN** 执行 `git rm -r --cached --ignore-unmatch -- .onion-sdd`
- **AND** 本地 `.onion-sdd/` 文件继续存在
- **AND** stderr 明确提示 index 已清理

#### Scenario: Git 不可用、非仓库根或命令失败

- **WHEN** 仓库不是 Git 仓库、`git rev-parse --show-toplevel` 不等于 `--repo-root`、Git 不可用或检测/清理命令失败
- **THEN** stderr 输出警告并跳过 index 清理
- **AND** 状态写入继续完成
