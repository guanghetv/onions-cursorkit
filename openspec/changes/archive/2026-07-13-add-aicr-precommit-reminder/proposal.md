## Why

`aicr-local` 已经具备提交前审查能力，但在规模化落地时仍有两类痛点：

1. 业务仓接入成本高：需要逐仓执行 `/cr-setup` 并拷贝整包脚本；
2. MR 覆盖率链路耦合：统计与评论发布过度依赖业务仓 CI，维护成本高。

本次升级目标是：在保持本地门禁稳定性的前提下，采用平台批量改造降低接入成本，并将 MR 覆盖率统计收敛到 `AI-CodeReview` 服务。

## What Changes

### 1) 接入模式升级：C 主、B 兜底

- 主路径采用 **平台批量改造（C）**：
  - 按仓库清单（`--repos-file`）批量下发 AICR 薄入口与运行时；
  - 支持 dry-run、幂等、失败报告（可人工重跑）、Git 回滚；
  - 降低对开发者手动逐仓操作的依赖。
- 兜底路径保留 **仓库最小改动（B）**（单仓 `install.sh` / `/cr-setup`），用于平台未覆盖仓库。

### 2) 运行时形态调整：repo-bundled runtime

- 采用 `vendor/aicr-runtime/` 将运行时固化到业务仓（默认复制，亦可 subtree）；
- pre-commit 只调用本地 runtime；
- commit 路径禁止在线拉取脚本。

### 3) MR 覆盖率职责收敛

- 业务仓职责：本地门禁 + 事件生产 + **pre-push 上报 events**；
- `AI-CodeReview` 职责：覆盖率聚合 + MR 描述/评论发布；
- 覆盖率链路异常不影响本地提交门禁。

### 4) `/cr` 与 hook 解耦（保持不变）

- `/cr`（`aicr-local`）本地审查 **不依赖** 业务仓是否执行 `cr-precommit-setup`；
- 未安装 hook / `vendor/aicr-runtime` 时，审查步骤 1–10 正常可用；步骤 11 写事件静默跳过；
- hook 仅提供提交硬门禁、事件落盘与上报能力。

### 5) Agent 规则不下沉业务仓

- `cr-before-commit.mdc` 由 common 插件统一下发（`alwaysApply`），**不**随 `install.sh` 复制到业务仓。

## API 契约（脚本/服务）

### 平台批量改造脚本

- 入口：`batch-rollout.sh --repos-file <path>`
- 环境变量：
  - `MODE`（`dry-run` | `apply`，默认 `dry-run`）
  - `REPORT_FILE`（可选 CSV）
  - `LOG_DIR`（可选）
- 输出结果（每仓一行）：
  - `PREVIEW | UPDATED | UNCHANGED | FAILED`
  - `reason`（失败原因）
  - `log_file`（单仓日志路径）
- **不支持**按 GitLab `group` 自动枚举仓库；须事先准备 repos 清单文件。

### 业务仓 events 上报（pre-push）

- 触发：`git push` 时 `upload-events-ci.mjs`
- 目标：`POST ${AICR_INGEST_URL}`（默认 `https://aicrfe.yc345.tv/review/aicr/events`）
- 请求体：`project_id`、`project_path`、`repo`、`branch`、`author`、`events[]`
- 失败：保留 `.git/aicr/ci-export/*.ndjson` 快照；pre-push 薄入口 **不阻断 push**（uploader 失败仍 `exit 0`）

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

1. 接入策略采用 **C 主、B 兜底**：平台批量改造优先；单仓 `install.sh` 兜底。
2. 运行时采用 **repo-bundled runtime**（`vendor/aicr-runtime/`），随仓库统一管理。
3. pre-commit 必须纯本地执行，禁止在线拉取脚本。
4. `core.hooksPath=.githooks` 保持不变，入口脚本仅负责本地 runtime 跳转。
5. 初始化质量以平台批量脚本与仓内 runtime 结构完整性校验为准；`install.sh` **不**自动跑 `--self-check`，自检由文档/验收步骤手动执行。
6. 批量改造脚本必须满足幂等、失败可报告与人工重跑；还原经 Git（`git restore`），不生成本地 `.aicr-migration-backup/`。
7. 仅支持 bundled 安装（薄 hook + `vendor/aicr-runtime/`），不提供 legacy 安装模式。
8. MR 覆盖率聚合与发布由 `AI-CodeReview` 服务承接，业务仓 GitLab CI 不再是主计算链路。
9. 覆盖率链路故障不得影响本地门禁（门禁优先级最高）。
10. 已移除业务仓 GitLab CI MR 覆盖率 job、`aggregate-mr.mjs`、`gitlab-auth.mjs` 等遗留资产。
11. `/cr` 本地审查与 hook 安装解耦；未集成 hook 不影响 `/cr` 使用。
12. `cr-before-commit.mdc` 仅随 common 插件下发，不写入业务仓。

## Impact

- **业务仓库**：接入文件最小化（`.githooks` + `vendor/aicr-runtime`），逐仓手工初始化成本下降。
- **平台工程**：新增批量改造、结构巡检、失败报告与 Git 回滚能力。
- **服务端**：`AI-CodeReview` 承担覆盖率聚合和 MR 发布逻辑。
- **开发体验**：未装 hook 的仓库仍可 `/cr`；装 hook 后提交链路有硬门禁，网络不再成为 commit 阶段依赖。

## Out of Scope / Follow-ups

本 change 归档时以下项仍为后续工作（不阻塞本仓 cursorkit 交付归档）：

- 飞书通知（辅）接口接入
- 试点仓 batch rollout 与 GitLab MR 覆盖率端到端可见性验证后再扩面

## References

- 当前变更目录：`openspec/changes/add-aicr-precommit-reminder/`
- 现有脚本资产：`plugins/common/assets/cr-precommit/`
- 现有安装入口：`plugins/common/commands/cr-setup.md`
- 目标服务仓：`AI-CodeReview`（覆盖率聚合与 MR 发布）

## 前端实现决策（灰区）

本需求为工程接入与服务编排，不涉及前端 UI 状态、交互与样式灰区，跳过该节。
