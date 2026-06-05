## Why

`aicr-local` 已经具备提交前审查能力，但在规模化落地时仍有两类痛点：

1. 业务仓接入成本高：需要逐仓执行 `/cr-setup` 并拷贝整包脚本；
2. MR 覆盖率链路耦合：统计与评论发布过度依赖业务仓 CI，维护成本高。

本次升级目标是：在保持本地门禁稳定性的前提下，采用平台批量改造降低接入成本，并将 MR 覆盖率统计收敛到 `AI-CodeReview` 服务。

## What Changes

### 1) 接入模式升级：C 主、B 兜底

- 主路径采用 **平台批量改造（C）**：
  - 按仓库清单批量下发 AICR 薄入口与运行时；
  - 支持 dry-run、幂等、失败重试、批次回滚；
  - 降低对开发者手动逐仓操作的依赖。
- 兜底路径保留 **仓库最小改动（B）**，用于平台未覆盖仓库。

### 2) 运行时形态调整：repo-bundled runtime

- 采用 `vendor/aicr-runtime/` 将运行时固化到业务仓（默认复制，亦可 subtree）；
- pre-commit 只调用本地 runtime；
- commit 路径禁止在线拉取脚本。

### 3) MR 覆盖率职责收敛

- 业务仓职责：本地门禁 + 事件生产 + **pre-push 上报 events**；
- `AI-CodeReview` 职责：覆盖率聚合 + MR 描述/评论发布；
- 覆盖率链路异常不影响本地提交门禁。

## API 契约（脚本/服务）

### 平台批量改造脚本

- 输入参数：
  - `repos`（仓库列表）或 `group`
  - `mode`（`dry-run` | `apply`）
- 输出结果：
  - `PREVIEW | UPDATED | UNCHANGED | FAILED`
  - `reason`（失败原因）
  - `log_file`（单仓日志路径）

### 业务仓 events 上报（pre-push）

- 触发：`git push` 时 `upload-events-ci.mjs`
- 目标：`POST ${AICR_INGEST_URL}`（默认 `https://aicrfe.yc345.tv/review/aicr/events`）
- 请求体：`project_id`、`project_path`、`repo`、`branch`、`author`、`events[]`
- 失败：保留 `.git/aicr/ci-export/*.ndjson` 快照，**不阻断 push**

### AI-CodeReview 覆盖率服务

- 输入：
  - MR 元信息（project/mr_iid/commit 列表）
  - 事件数据（`cr_completed`、`commit_cr_linked` 等）
- 输出：
  - 覆盖率报告（`total_commits`、`covered_commits`、`coverage_rate`、`missing_commits`、`updated_at`）
  - GitLab 发布结果（comment 或 description）

## Capabilities

### New Capabilities

- `aicr-batch-rollout`：平台批量改造与治理能力。
- `aicr-repo-bundled-runtime`：基于 `vendor/aicr-runtime` 的运行时固化能力。
- `aicr-mr-coverage-service-mode`：AI-CodeReview 服务主导的 MR 覆盖率模式。

### Modified Capabilities

- `aicr-setup-installation`：从“逐仓整包安装”升级为“批量主路径 + 最小兜底”。
- `aicr-mr-coverage-aggregation`：从“业务仓 CI 主链路”升级为“服务端主链路 + pre-push 上报”。

## Decisions

1. 接入策略采用 **C 主、B 兜底**：平台批量改造优先。
2. 运行时采用 **repo-bundled runtime**（`vendor/aicr-runtime/`），随仓库统一管理。
3. pre-commit 必须纯本地执行，禁止在线拉取脚本。
4. `core.hooksPath=.githooks` 保持不变，入口脚本仅负责本地 runtime 跳转。
5. 初始化质量以平台批量脚本与仓内 runtime 结构完整性校验为准。
6. 批量改造脚本必须满足幂等、失败可重试、批次可回滚（`rollback-bundled-runtime.sh`）。
7. 本次允许不兼容旧结构（`.githooks/aicr/*`），通过迁移脚本一次切换。
8. MR 覆盖率聚合与发布由 `AI-CodeReview` 服务承接，业务仓 GitLab CI 不再是主计算链路。
9. 覆盖率链路故障不得影响本地门禁（门禁优先级最高）。
10. 已移除业务仓 GitLab CI MR 覆盖率 job、`aggregate-mr.mjs`、`gitlab-auth.mjs` 等遗留资产。

## Impact

- **业务仓库**：接入文件最小化，逐仓手工初始化成本下降。
- **平台工程**：新增批量改造、结构巡检、失败重试与回滚能力。
- **服务端**：`AI-CodeReview` 承担覆盖率聚合和 MR 发布逻辑。
- **开发体验**：提交链路更稳定（本地执行），网络不再成为 commit 阶段依赖。

## References

- 当前变更目录：`openspec/changes/add-aicr-precommit-reminder/`
- 现有脚本资产：`plugins/common/assets/cr-precommit/`
- 现有安装入口：`plugins/common/commands/cr-setup.md`
- 目标服务仓：`/Users/lige/Onion/AI-CodeReview/`

## 前端实现决策（灰区）

本需求为工程接入与服务编排，不涉及前端 UI 状态、交互与样式灰区，跳过该节。
