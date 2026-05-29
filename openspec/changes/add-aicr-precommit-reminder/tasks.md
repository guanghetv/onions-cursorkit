## 1. OpenSpec 与能力定义

- [x] 1.1 新建 change 目录 `openspec/changes/add-aicr-precommit-reminder/`
- [x] 1.2 编写 `proposal.md`：明确「人 + 自动」调用链路与默认阻断策略
- [x] 1.3 编写 `specs/aicr-precommit-reminder/spec.md`：补充需求与场景
- [x] 1.4 写入 `.openspec.yaml` 并标注创建日期
- [x] 1.6 写入 Agent 引导式 CI 接入设计（权限边界选项 2，2026-05-29）

## 2. 本地门禁能力（实现层）

- [x] 2.1 新增 pre-commit 提醒脚本模板（默认 hard 阻断）
- [x] 2.2 新增事件记录脚本（`cr_completed`、`cr_failed`、`commit_attempted`、`commit_blocked_without_cr`、`commit_bypassed_cr` 等）
- [x] 2.3 实现 **per-commit** 匹配（`lastCr > lastAttempt`，同 repo/branch/author）
- [x] 2.4 增加显式跳过参数（`AICR_BYPASS_CR=1`，原因可选）
- [x] 2.5 新增 `validate-cr-gate.mjs`（files + fingerprint + **status=pass**）
- [x] 2.6 同步 `cr-before-commit.mdc`；**不**安装 common `/commit`（避免覆盖团队版）
- [x] 2.7 更新 `aicr-local`：有问题禁止写 pass、禁止 Agent 擅自改代码
- [x] 2.8 hook 异常时写 `telemetry_error` 并放行（validator 不可用/崩溃）
- [x] 2.9 bypass_reason JSON 转义（`log-hook-event.mjs`）

## 3. MR 聚合能力（实现层）

- [x] 3.1 新增 MR 聚合脚本骨架 `aggregate-mr.mjs`
- [x] 3.2 输出覆盖率、缺失 commit 列表、更新时间
- [x] 3.3 新增 GitLab comment 脚本 `publish-gitlab-note.mjs`
- [x] 3.4 新增 **post-commit hook** + `commit_cr_linked`（`link-cr-commit.mjs`）
- [x] 3.5 改 `aggregate-mr.mjs`：认 `commit_cr_linked.commit_sha`，仅计 pass
- [x] 3.6 实现 events 上传 CI 机制（pre-push + Generic Package + `fetch-events-ci.mjs`）
- [x] 3.7 GitLab CI 与 Agent 引导接入
  - [x] 3.7.1 新增 `gitlab-ci/aicr-mr-coverage.job.yml` 模板
  - [x] 3.7.2 新增 `aicr-gitlab-ci-setup` skill（扫描、决策树、权限边界选项 2）
  - [x] 3.7.3 新增 `/cr-setup-ci` command
  - [x] 3.7.4 `install.sh` 安装完成后 offer CI 接入（`AICR_SKIP_CI_PROMPT` 可跳过）
  - [x] 3.7.5 `integration-checklist.md` 与 troubleshooting CI 章节
- [x] 3.8 本地 smoke 脚本：`smoke-mr-coverage.sh`（`RUN_SMOKE=true install`）
- [ ] 3.9 飞书通知（辅）接口接入（后续）

## 4. 安装入口与文档（实现层）

- [x] 4.1 新增 setup skill（`cr-precommit-setup`）
- [x] 4.2 新增命令入口 `/cr-setup`
- [x] 4.3 新增一键安装脚本 `install.sh` 并接入 `.githooks` 模式（含 post-commit / pre-push）
- [x] 4.4 更新 `aicr-local/SKILL.md` 与 `references/troubleshooting.md`
- [x] 4.5 install.sh 可选自动 smoke test（`RUN_SMOKE=true`）
- [x] 4.6 troubleshooting 增加 MR 覆盖率端到端调试章节

## 5. 验收与灰度

- [x] 5.1 验证「已执行 `/cr`（pass）后提交」路径
- [x] 5.2 验证「未执行 `/cr` 直接提交」触发阻断；显式跳过可继续
- [x] 5.3 验证 MR 覆盖率聚合逻辑（smoke 脚本 100%）；**GitLab 端到端待试点**
- [ ] 5.4 先在 1-2 个试点仓库灰度，确认 MR comment 覆盖率可见后再扩面
