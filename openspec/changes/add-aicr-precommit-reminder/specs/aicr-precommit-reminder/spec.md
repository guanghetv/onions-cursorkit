# aicr-precommit-reminder

## 概述

本规格定义 AICR 提交前门禁升级后的目标形态：以平台批量改造为主路径，采用仓库固化 runtime 的薄入口模式，保持本地门禁稳定；MR 覆盖率统计与发布由 `AI-CodeReview` 服务承接。

## ADDED Requirements

### Requirement: 平台批量改造应作为默认接入路径

系统 SHALL 提供平台级批量改造能力，用于将目标仓库从旧接入方式迁移到新接入方式，避免开发者逐仓手工初始化。

#### Scenario: dry-run 预检

- **WHEN** 平台以 `dry-run` 模式执行批量改造
- **THEN** 输出每个仓库的预期改动、风险点和状态（`PREVIEW`/`UPDATED`/`UNCHANGED`/`FAILED`）
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
- **THEN** `upload-events-ci.mjs` POST 至 `AICR_INGEST_URL`（含 `project_id` 或 `project_path`、`branch`、`author`、`events[]`）
- **AND** 成功时输出 `UPLOAD_OK`

#### Scenario: 上报失败保留快照

- **WHEN** ingest 请求失败或网络不可用
- **THEN** 写入 `.git/aicr/ci-export/*.ndjson` 本地快照
- **AND** push 仍成功完成

### Requirement: 覆盖率统计应由 AI-CodeReview 服务主导

系统 SHALL 将 MR 覆盖率聚合与 GitLab 发布职责收敛到 `AI-CodeReview` 服务，业务仓 CI 不再承担主计算链路。

#### Scenario: 服务端聚合覆盖率

- **WHEN** `AI-CodeReview` 收到 MR 上下文与事件数据
- **THEN** 返回覆盖率报告（`total_commits`、`covered_commits`、`coverage_rate`、`missing_commits`、`updated_at`）

#### Scenario: 服务端发布 MR 结果

- **WHEN** 覆盖率报告可用
- **THEN** 由服务端发布到 GitLab MR（comment 或 description）
- **AND** 发布失败不应影响本地提交门禁

### Requirement: 迁移脚本应支持一次切换与回滚

本次升级允许不兼容旧结构；系统 SHALL 提供迁移与回滚机制，确保可控切换。

#### Scenario: 旧结构迁移

- **WHEN** 仓库存在旧结构（如 `.githooks/aicr/*`）
- **THEN** 迁移脚本备份旧内容并切换到新结构
- **AND** 切换后执行自检

#### Scenario: 批次回滚

- **WHEN** 批量改造出现系统性问题
- **THEN** 平台可按批次回滚到改造前状态
- **AND** 回滚结果可审计
