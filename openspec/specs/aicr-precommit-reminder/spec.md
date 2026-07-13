## Purpose

定义 AICR 提交前门禁与提醒链路：薄入口 + `vendor/aicr-runtime`、平台批量改造、本地硬门禁、pre-push 事件上报，以及 MR 覆盖率由 `AI-CodeReview` 服务主导。`/cr` 本地审查与 hook 安装解耦；`cr-before-commit.mdc` 由 common 插件下发、不复制进业务仓。

实现资产：`plugins/common/assets/cr-precommit/`、`/cr-setup`、`cr-precommit-setup`、`aicr-local` 步骤 11。

## Requirements

### Requirement: 平台批量改造应作为默认接入路径

系统 SHALL 提供平台级批量改造能力，用于将目标仓库从旧接入方式迁移到新接入方式，避免开发者逐仓手工初始化。

批量入口为 `batch-rollout.sh --repos-file <path>`；SHALL 支持 `MODE=dry-run|apply`。SHALL NOT 要求实现按 GitLab `group` 自动枚举仓库（仓库清单由调用方预先准备）。

#### Scenario: dry-run 预检

- **WHEN** 平台以 `dry-run` 模式执行批量改造
- **THEN** 输出每个仓库的预期改动与状态（`PREVIEW`/`UPDATED`/`UNCHANGED`/`FAILED`）
- **AND** 不实际写入仓库文件

#### Scenario: apply 生效

- **WHEN** 平台以 `apply` 模式执行
- **THEN** 系统写入薄入口和最小运行时文件集
- **AND** 输出批量执行报告，包含失败仓库和失败原因

#### Scenario: 重复执行幂等

- **WHEN** 目标仓库已是目标结构且运行时文件完整
- **THEN** 再次执行批量改造 SHALL 输出 `UNCHANGED`
- **AND** 不重复改写文件

### Requirement: 仓库应采用薄入口 + repo-bundled runtime

系统 SHALL 使用仓库内薄入口脚本调用本地 runtime；runtime SHALL 固化在 `vendor/aicr-runtime/`（复制或 subtree 均可，默认 install 为复制）。

#### Scenario: 入口执行本地 runtime

- **WHEN** 开发者执行 `git commit`
- **THEN** `.githooks/pre-commit` 仅调用仓库内 runtime
- **AND** 不在 commit 路径发起远程脚本下载

#### Scenario: runtime 结构完整性校验

- **WHEN** 仓库执行初始化或升级后
- **THEN** runtime 必需脚本与 `.githooks` 入口 SHALL 完整可用
- **AND** 缺失关键文件时应提示修复
- **AND** 升级时 SHALL 移除已废弃的旧 runtime 文件（含但不限于 `repo-context.mjs`、`resolve-runtime-dir.sh`、`aggregate-mr.mjs`、`gitlab-auth.mjs`、`diff-fingerprint.mjs`、`hook-post-commit.sh`、`hook-pre-push.sh`）

runtime 包含：`hook-pre-commit.sh`、`aicr-utils.mjs`、`validate-cr-gate.mjs`、`event-log.mjs`、`link-cr-commit.mjs`、`upload-events-ci.mjs`。

薄入口包含：`.githooks/pre-commit`、`.githooks/post-commit`、`.githooks/pre-push`。

### Requirement: 本地门禁语义保持不变

系统 SHALL 保持已有门禁语义：`status=pass` + files/fingerprint 一致 + per-commit 校验，默认阻断并支持显式 bypass。

`diff_fingerprint` SHALL 基于暂存区 diff 内容（`git diff --cached` 对 `files` 列表）计算 SHA-256，而非仅对文件路径列表 hash；同文件不同内容须产生不同 fingerprint。

#### Scenario: 有效证据放行

- **WHEN** 存在有效 `cr_completed(status=pass)` 且与暂存区一致
- **THEN** 允许提交，并记录 `commit_attempted(status=allowed)`

#### Scenario: 证据缺失阻断

- **WHEN** 不存在有效 `/cr` 证据且未设置 bypass
- **THEN** 阻断提交并记录 `commit_blocked_without_cr`

#### Scenario: 显式 bypass

- **WHEN** 设置 `AICR_BYPASS_CR=1`
- **THEN** 允许提交并记录 `commit_bypassed_cr`

#### Scenario: 暂存区内容变更须重新 /cr

- **WHEN** 暂存区文件路径未变但 diff 内容已变更
- **THEN** `diff_fingerprint` 与最近一次 `cr_completed` 不一致
- **AND** pre-commit 阻断并提示重新执行 `/cr`

#### Scenario: validator 异常放行

- **WHEN** `validate-cr-gate.mjs` 不可用或崩溃（退出码 ≥ 2）
- **THEN** 记录 `telemetry_error` 与 `commit_attempted(status=telemetry_fallback)`
- **AND** 放行本次提交

### Requirement: post-commit 按 commit 关联审查证据

系统 SHALL 在 post-commit 为每个新 `commit_sha` 写入 `commit_cr_linked`，幂等键为 `commit_sha`；不得因相同 `diff_fingerprint` 已关联过而跳过新 commit。

#### Scenario: 新 commit 写入 commit_cr_linked

- **WHEN** commit 成功且本轮 `commit_attempted(status=allowed)`
- **AND** 存在属于本轮提交周期的 `cr_completed(status=pass)`（时间戳在上一轮提交尝试之后、本轮 `commit_attempted` 之前或同时）
- **AND** 该 `commit_sha` 尚未关联
- **THEN** 写入 `commit_cr_linked`（含 `commit_sha`、`diff_fingerprint`、`status=pass`）

#### Scenario: 非门禁放行 commit 不关联

- **WHEN** 本轮 `commit_attempted` 为 `bypassed`、`soft_warn`、`telemetry_fallback` 等非 `allowed` 状态
- **THEN** 不写入 `commit_cr_linked`

#### Scenario: 同文件多次提交各自关联

- **WHEN** 连续多次 commit 修改同一文件且每次均完成 `/cr` 并通过门禁
- **THEN** 每次 commit 均产生独立的 `commit_cr_linked`
- **AND** MR 覆盖率统计可将各 commit 计入分子

#### Scenario: 同 commit 幂等

- **WHEN** post-commit 对同一 `commit_sha` 重复执行
- **THEN** 不重复写入 `commit_cr_linked`

### Requirement: 业务仓 SHALL 通过 pre-push 上报 events

系统 SHALL 在 `git push` 时将本地 `events.ndjson` 全量上报至 `AI-CodeReview` ingest 接口；上报失败不得阻断 push。

#### Scenario: push 触发上报

- **WHEN** 开发者执行 `git push` 且 `.git/aicr/events.ndjson` 非空
- **THEN** `upload-events-ci.mjs` POST 至 `AICR_INGEST_URL`（含 `project_id` 或 `project_path`、`repo`、`branch`、`author`、`events[]`）
- **AND** 成功时输出 `UPLOAD_OK`

#### Scenario: 上报失败保留快照

- **WHEN** ingest 请求失败或网络不可用
- **THEN** 写入 `.git/aicr/ci-export/*.ndjson` 本地快照
- **AND** push 仍成功完成（薄入口不因 uploader 失败而阻断）

### Requirement: 覆盖率统计应由 AI-CodeReview 服务主导

系统 SHALL 将 MR 覆盖率聚合与 GitLab 发布职责收敛到 `AI-CodeReview` 服务，业务仓 CI 不再承担主计算链路。

#### Scenario: 服务端聚合覆盖率

- **WHEN** `AI-CodeReview` 收到 MR 上下文与事件数据
- **THEN** 返回覆盖率报告（`total_commits`、`covered_commits`、`coverage_rate`、`missing_commits`、`updated_at`）

#### Scenario: 服务端发布 MR 结果

- **WHEN** 覆盖率报告可用
- **THEN** 由服务端发布到 GitLab MR（comment 或 description）
- **AND** 发布失败不应影响本地提交门禁

### Requirement: 安装脚本应支持幂等与 Git 还原

系统 SHALL 通过 `install.sh` 提供幂等安装与 Git 还原能力，确保可控接入。

`install.sh` SHALL 写入薄 hook 与 `vendor/aicr-runtime/`，设置 `core.hooksPath=.githooks`；SHALL NOT 复制 `cr-before-commit.mdc` 到业务仓；SHALL NOT 自动执行 runtime `--self-check`（自检由验收文档手动触发）。

#### Scenario: 首次安装

- **WHEN** 仓库执行 `install.sh` 或批量改造 apply
- **THEN** 写入薄 hook 与 `vendor/aicr-runtime/`（不写入 `.aicr-migration-backup/` 本地备份）
- **AND** 不复制 `cr-before-commit.mdc`
- **AND** 不在安装脚本内强制跑 `--self-check`

#### Scenario: 批次还原

- **WHEN** 批量改造出现系统性问题
- **THEN** 平台通过 Git（`git restore --source=<git_ref> -- .githooks vendor/aicr-runtime`）还原 `.githooks` 与 `vendor/aicr-runtime`
- **AND** 回滚结果可经 Git 历史审计

### Requirement: /cr 本地审查不依赖 hook 安装

系统 SHALL 保证 `aicr-local` 的 `/cr` 在未执行 `cr-precommit-setup` / 未安装业务仓 hook 时仍可完成本地审查。

#### Scenario: 未集成 hook 仍可 /cr

- **WHEN** 业务仓不存在 `vendor/aicr-runtime/event-log.mjs` 且未配置 `core.hooksPath=.githooks`
- **THEN** 用户仍可通过 `git add` + `/cr` 完成暂存区审查并输出报告
- **AND** 步骤 11 因缺少 `event-log.mjs` 而跳过事件写入，且不视为审查失败

#### Scenario: 已集成 hook 时写事件

- **WHEN** 业务仓已安装 `vendor/aicr-runtime/event-log.mjs` 且审查结论为 `✅ 无明显问题`
- **THEN** `/cr` 步骤 11 写入 `cr_completed(status=pass)` 供 pre-commit 校验

### Requirement: Agent 提交前规则由插件下发

系统 SHALL 通过 common 插件下发 `cr-before-commit.mdc`（约束 Agent 协助提交前完整执行 `/cr`），SHALL NOT 由安装脚本将其复制进业务仓库。

#### Scenario: 安装不落盘规则文件

- **WHEN** 对业务仓执行 `install.sh`
- **THEN** 业务仓不新增 `cr-before-commit.mdc`（或等价路径下的同名规则文件）
- **AND** 规则仍由已安装的 common 插件对 Agent 生效
