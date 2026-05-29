# aicr-precommit-reminder

## 概述

本规格定义 `aicr-local` 在「提交前门禁 + MR 可观测统计」场景下的能力。目标是在不牺牲应急灵活性的前提下，默认阻断漏检提交，审查有问题时不可提交，并在 MR 维度提供 L1 弱一致的 `/cr` 覆盖率数据。

## ADDED Requirements

### Requirement: 提供一次性安装入口

系统 SHALL 提供显式安装入口（命令或 skill），用于将 pre-commit 提醒链路安装到目标仓库。

#### Scenario: 人工执行 setup

- **WHEN** 仓库管理员或开发者执行安装入口（如 `/cr-setup`）
- **THEN** 系统安装 pre-commit hook、事件记录脚本、`validate-cr-gate.mjs`，同步 `cr-before-commit.mdc` 到 `.cursor/rules/`
- **AND** 系统 SHALL **不**安装或覆盖团队版 `/commit` Command

#### Scenario: 安装后自检

- **WHEN** 安装完成
- **THEN** 文档或 skill 提供 smoke test 步骤（`event-log --self-check`、`validate-cr-gate --self-check`、无 cr 时 pre-commit 阻断）
- **NOTE** 安装脚本可提示自检命令；自动化 smoke test 为可选增强

### Requirement: 提交前默认阻断（可显式跳过）

系统 SHALL 在 `git commit` 阶段通过 `validate-cr-gate.mjs` 检查有效 `/cr` 证据；证据缺失或无效时 SHALL 阻断提交（`AICR_ENFORCEMENT_MODE=hard`）。系统 SHALL 支持显式跳过并记录审计事件。

有效 `/cr` 证据 SHALL 同时满足：

- 同 `repo`、`branch`、`author` 下存在 `cr_completed`；
- 该 `cr_completed` 的 timestamp **晚于** 最近一次 `commit_attempted` / `commit_blocked_without_cr` / `commit_bypassed_cr`（**per-commit**，非固定时间窗）；
- `cr_completed.status` === `"pass"`；
- `cr_completed.files` 与当前 `git diff --cached --name-only` 一致；
- `cr_completed.diff_fingerprint` 与当前暂存区文件列表 fingerprint 一致。

#### Scenario: 存在有效 `/cr` 证据且审查通过

- **WHEN** hook 检测到满足上述条件的 `cr_completed`
- **THEN** 写 `commit_attempted(status=allowed)`，commit 正常继续

#### Scenario: 不存在有效 `/cr` 证据（默认阻断）

- **WHEN** hook 未检测到有效 `cr_completed`
- **THEN** 输出「请先执行 `/cr`」类提示，写 `commit_blocked_without_cr`，阻断提交（非零退出码）

#### Scenario: 审查有问题（非 pass）

- **WHEN** 最近一次 `cr_completed.status` 为 `fail` 或缺失 `status=pass`
- **THEN** hook 阻断提交，提示须修复后重新 `/cr`
- **AND** Agent SHALL NOT 未经用户明确要求修改业务代码以通过审查

#### Scenario: 显式跳过阻断

- **WHEN** 未检测到有效 `cr_completed`，且设置 `AICR_BYPASS_CR=1`
- **THEN** 允许提交继续，写 `commit_bypassed_cr`（可选 `bypass_reason`）

#### Scenario: 软提醒模式

- **WHEN** `AICR_ENFORCEMENT_MODE=soft` 且无有效 cr
- **THEN** 写 `commit_without_cr`，不阻断提交

#### Scenario: hook 脚本异常

- **WHEN** 提醒链路出现脚本异常或日志写入失败
- **THEN** 系统 SHOULD 记录 `telemetry_error` 并允许提交继续（避免阻塞开发）
- **NOTE** 当前实现未落地；列为待实现需求

### Requirement: 事件采集与字段标准化

系统 SHALL 以 append-only NDJSON 保存事件，默认路径 `.git/aicr/events.ndjson`（`AICR_EVENT_LOG` 可覆盖）。

事件类型 SHALL 至少包含：`cr_invoked`、`cr_completed`、`cr_failed`、`commit_cr_linked`（待实现）、`commit_attempted`、`commit_blocked_without_cr`、`commit_bypassed_cr`、`commit_without_cr`、`commit_pushed`（可选）、`telemetry_error`（可选）。

`repo` 字段当前实现为仓库根目录 **basename**（已知同名目录可能串扰，L1 可接受）。

#### Scenario: `/cr` 审查通过

- **WHEN** `/cr` 结论为「无明显问题」
- **THEN** 写 `cr_completed`，包含 `repo`、`branch`、`author`、`timestamp`、`status=pass`、`files`、`diff_fingerprint`
- **AND** 此时 **不得** 包含 `commit_sha`（commit 尚未发生）

#### Scenario: `/cr` 审查有问题

- **WHEN** `/cr` 报告含 🔴 或 🟠
- **THEN** **不得** 写 `status=pass` 的 `cr_completed`
- **AND** 可选写 `cr_failed`（`status=fail`）

#### Scenario: commit 成功后绑定 SHA（待实现）

- **WHEN** pre-commit 放行且 commit 成功完成
- **THEN** post-commit hook 写 `commit_cr_linked`，包含 `commit_sha`（HEAD）、`diff_fingerprint`、与对应 `cr_completed` 一致的 `repo/branch/author`

#### Scenario: 提交动作发生

- **WHEN** 开发执行 `git commit` 且 pre-commit 运行
- **THEN** 写 `commit_attempted`；若阻断则写 `commit_blocked_without_cr`；若 bypass 则写 `commit_bypassed_cr`

### Requirement: MR 覆盖率聚合（L1）

系统 SHALL 提供 MR 级别覆盖率聚合：输入 MR commit SHA 列表 + events，输出覆盖统计。

#### Scenario: 聚合 MR 覆盖率

- **WHEN** CI 或 MR bot 提供 MR commit 列表及可读的 events 数据
- **THEN** 系统返回 JSON：`total_commits`、`covered_commits`、`coverage_rate`、`missing_commits`、`updated_at`
- **AND** 「已覆盖」定义为：commit SHA 存在于 `commit_cr_linked`（且关联 CR 为 pass）；兼容期可含带 `commit_sha` 的 `cr_completed`

#### Scenario: MR 无 commit

- **WHEN** MR commit 列表为空
- **THEN** 返回 `coverage_rate = 1`，`missing_commits = []`

#### Scenario: events 不可达

- **WHEN** CI 无法获取开发者本机 events
- **THEN** 覆盖率 SHALL 为 0 或标记为「无数据」；系统 SHOULD 通过 push 上传/API 提供 events（待实现）

### Requirement: events 进入 CI（待实现）

系统 SHALL 提供将本地 events 片段传输至 MR CI 的机制，以便远程 pipeline 执行聚合。

#### Scenario: push 时上传 events

- **WHEN** 开发者 push 到远程分支
- **THEN** 系统将自上次 push 以来新增的 events 行上传至约定存储（Job Artifact、内部 API 等）
- **AND** MR pipeline 可读取该存储并与 MR commit 列表聚合

### Requirement: 统计结果输出通道

系统 SHALL 支持将 MR 覆盖率结果输出到 GitLab（主通道），并可选输出到飞书（辅通道）。

#### Scenario: GitLab 输出

- **WHEN** 聚合结果生成
- **THEN** 通过 `publish-gitlab-note.mjs` 在 MR comment 发布覆盖率摘要与缺失 commit 列表（marker 幂等更新）

#### Scenario: 飞书输出

- **WHEN** 团队启用飞书通知
- **THEN** 输出简化统计摘要（覆盖率、缺失数量、MR 链接）
- **NOTE** 待实现

### Requirement: Agent 引导式 GitLab CI 接入

系统 SHALL 提供 Agent 可执行的 CI 接入流程，用于在**已有 GitLab CI** 的业务仓库中最小增量接入 MR 覆盖率 job。系统 SHALL **不**在安装 hook 时自动修改 `.gitlab-ci.yml`。

#### Scenario: `/cr-setup` 完成后 offer CI 接入

- **WHEN** 用户完成 `/cr-setup` 且未设置 `AICR_SKIP_CI_PROMPT=1`
- **THEN** Agent 询问是否分析本仓库 CI 并给出接入建议
- **AND** 用户拒绝则不修改任何 CI 文件

#### Scenario: 用户触发 `/cr-setup-ci`

- **WHEN** 用户执行 `/cr-setup-ci`
- **THEN** Agent Read `aicr-gitlab-ci-setup` 技能，扫描 `.gitlab-ci.yml` 及 include 链，输出《AICR CI 接入建议》
- **AND** 用户确认方案后，Agent 可写入/修改 CI 文件

#### Scenario: Agent 权限边界（选项 2）

- **WHEN** Agent 执行 CI 接入
- **THEN** Agent MAY 修改业务仓库内 CI 配置文件
- **AND** Agent SHALL NOT `git commit` 或 push；由用户 review 后自行提交
- **AND** 用户未确认方案前 Agent SHALL NOT 修改 CI 文件

#### Scenario: 与现有 pipeline 共存

- **WHEN** Agent 生成 MR 覆盖率 job
- **THEN** job 名 SHALL 为 `aicr-mr-coverage`（或带前缀），`rules` 限制 `merge_request_event`
- **AND** 试点期 SHALL 设置 `allow_failure: true`，且 SHALL NOT 破坏现有 build/test/deploy 的 `needs` 链

#### Scenario: 前置能力未就绪时的提示

- **WHEN** post-commit 或 events 上传尚未实现
- **THEN** Agent SHALL 在接入建议中明确警告：CI job 可安装但覆盖率可能为 0，直至 tasks 3.4–3.6 完成
