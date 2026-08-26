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

## [0.2.1] - 2026-08-26

### Added

- 手动 Tier 2+/3 开新任务前扫描遗留变更：有 Trellis 则 OpenSpec 与 task 成对归档；未装 Trellis 时仍确认归档上一轮 OpenSpec。拒绝或失败不阻塞。mini、light 与 `/onsf-auto` 不触发。
- `onion_state.py` 写状态前会清理 `.onion-sdd/` 下已有的 Git 跟踪记录，仅移除 index 并保留本地文件；Git 失败只警告。

### Removed

- 移除 Onion SDD 对 Trellis CLI 与项目模板版本的检查、升级询问和执行建议；版本维护不再属于 Onion SDD 使用流程。使用者无需关心 Trellis 项目版本。

## [0.2.0] - 2026-08-12

### Changed

- 迭代发版：`feat/0.2.0版本迭代` 合入发布线；插件版本 `0.1.5` → `0.2.0`。
- 能力主体仍为 check 阶段四步复合审查（AICR 前移、`trellis-check` / `/cr` 职责切分、条件化提交复审），详见 `[0.1.5]`。

## [0.1.5] - 2026-07-27

### Changed

- AICR 从提交门禁**前移到 check 阶段**：`rules/onion-sdd.mdc` 的「提交前审查」重写为「代码审查」，定义 check 四步复合阶段——`trellis-check`（含其修复）→ 暂存本次 change 改动 → `/cr` 审查暂存区 → 修复、回跑受影响门禁、重新暂存、复审。由 Agent 自动串联，用户无需输入命令。
- 顺序不可调换并写明理由：`trellis-check` 会修改代码，先暂存会导致审查对象与最终产物脱节。
- 定义 check 第 4 步的**通过判据**：CR 报告中属于本次 change 的 🔴 清零即通过；🟠 由 Agent 逐条判断，修或不修都需在 check 输出中说明理由，不作为循环条件。
- 授权边界放宽**仅限暂存**：check 阶段允许自动 `git add`（限本次 change 范围，禁止 `git add -A`）与 `/cr`；仍禁止自动 `git commit`、push、创建 PR/MR。暂存只增不减，禁止 `git reset` 或任何移除用户已暂存内容的动作；归属存疑的文件需用户确认；CR 审到本次 change 之外内容的问题只列出并标注归属，不计入 check 的通过判据。`/onsf-finish` 归档时的 `git add openspec/changes/` 属 scoped chore，不受该纪律约束。
- 提交门禁改为**条件化复审**：暂存区自 CR 通过后未变化则直接 commit，有任何变化（含新增暂存文件）或无法判定则重新 `/cr`。判定由 Agent 依据会话上下文完成，不引入指纹机制，不修改 `onion_state.py`。
- 职责切分更新：`trellis-check` 负责 lint / typecheck / 测试 / `.trellis/spec/` 对齐 / spec 回写；`/cr` 负责团队前后端规范、安全风险、影响范围与 `openspec/specs/` 业务需求对齐。切分为弱约束，结论重叠时合并去重。
- `full-change` / `auto-flow` / `onsf-continue` 口径对齐：`/onsf-auto` 下暂存与 `/cr` 可自动执行，commit 仍在高风险清单内停止；`auto-flow` 的 `diff-review`（工作区、范围与产物核对）与 check 阶段 CR（暂存区、团队规范与安全）职责区分已写明。
- `README.md`、`USAGE.md`、`docs/feishu-wiki-onion-sdd-usage.md`：扩展能力表、分工表与收尾流程图同步为新顺序。

### Notes

- 未改造 `aicr-local`：审查基线仍是暂存区（其既有 `staged` 模式），`/cr` 原样调用，`plugins/common/**` 零改动，`fe-specflow` / `be-specflow` 不受影响。
- 降级路径不变且不阻塞 check：`/cr` 不可用时按 `aicr-local` 的 `SKILL.md` 审查暂存区；未安装时 Agent 自审暂存区并注明团队规范维度未覆盖。

## [0.1.4] - 2026-07-24

### Changed

- `commands/onsf-finish.md` Branch B（绑定 Trellis task）从「建议跑 `/trellis:finish-work`」改为**自动归档 Trellis task + journal**：归档前新增工作区干净检查（脏则 bail），`openspec archive` 后自动提交 scoped chore（openspec 归档移动），再委托 `trellis-finish-work` skill 执行 `task.py archive` + `add_session.py`。单命令收尾，用户无需再跑 `/trellis:finish-work`。
- 收尾流程顺序调整：代码 commit（Phase 3.4）**前置于** `/onsf-finish`；`/onsf-finish` 末尾工作区干净，可一并归档两边。
- 「不自动提交 git commit」约束放宽为：仅自动提交 openspec 归档移动这一项 scoped chore（纯文件移动，非代码，不走 AICR）；代码 commit 仍前置；不自动 push/PR。
- `USAGE.md`、`docs/feishu-wiki-onion-sdd-usage.md` 流程图与链路同步为新顺序。

### Added

- `commands/onsf-finish.md`：归档前工作区干净检查（过滤 `.trellis/workspace/`、`.trellis/tasks/`），脏则 bail 不归档。

### Notes

- `/trellis:finish-work` 保留供纯 Trellis 任务（无 OpenSpec change）使用；onion-sdd bound change 不再需要它。
- `finish_check.py` 的 stale-task WARN（0.1.3）保留为兜底，防纯 Trellis 任务漏归档与历史遗留 task 被发现。

## [0.1.3] - 2026-07-24

### Added

- `commands/onsf-finish.md`：Branch B（change 绑定 Trellis task）新增「Trellis 收尾待办」必选输出——OpenSpec 归档成功后必须输出一行点名 bound task 与 `/trellis:finish-work`，未输出不得宣称完成；仍不自动调用 `/trellis:finish-work`（保留其提交门禁）。
- `scripts/finish_check.py`：归档预检新增非致命 WARN——扫描 `in_progress` Trellis task，若其 bound OpenSpec change 已归档/缺失则提示执行 `/trellis:finish-work` 清理。只读 `.trellis/tasks/**` 与 `openspec/changes/**`，不改 `.trellis/scripts/**`；WARN 不改变 exit code。

## [0.1.2] - 2026-07-24

### Added

- `scripts/onion_state.py`：未显式传 `--repo-root` 且未设 `ONION_SDD_ROOT` 时，从 cwd 向上查找最近的含 `.trellis/` 的目录作为 repo-root，找不到回退 cwd。修复 pnpm monorepo 子包 cwd 看不到外层 `.trellis/` 导致状态/产物落错位置的回归。优先级不变：显式 `--repo-root` > `ONION_SDD_ROOT` > 自动解析。
- `scripts/finish_check.py`：归档预检新增非致命 WARN——扫描 change 在 `docs/**` 下新建/修改且文件名含 convention/guideline/standard/规范/约定 的文件，提示应迁入 `.trellis/spec/<package>/<layer>/`（Phase 3.3 spec update）。WARN 不改变 exit code，不阻塞归档。
- `skills/openspec-change/SKILL.md`：新增「规范/约定的归属」小节——`tasks.md` 只装产品/验收交付物；编码约定/规范属 Phase 3.3 spec 积累，落 `.trellis/spec/`，禁止进 `tasks.md` 与 `docs/`。

### Changed

- `rules/onion-sdd.mdc`：运行态段补充 repo-root 自动解析说明，建议手动调用优先让脚本自动解析，避免硬编码 `--repo-root .`。

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
