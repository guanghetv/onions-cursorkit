---
name: cr-precommit-setup
description: 在业务仓库安装 /cr 提交前默认阻断与 MR 覆盖率统计模板。用于一次性接入 pre-commit 门禁链路，后续由 hook 与 CI 自动执行。
---

# CR Precommit Setup

用于在目标业务仓库一次性安装 `/cr` 提交前提醒与统计链路。该能力默认是**硬门禁**：缺少有效 `/cr` 记录会阻断 commit，但支持显式跳过。

## 何时使用

- 团队希望开发提交前有 `/cr` 遗漏提醒
- 希望在 MR 维度统计 `/cr` 覆盖率
- 需要先小范围灰度，再逐步推广

## 安装步骤

### 1) 一键安装（推荐）

在目标仓库执行安装脚本（仓库级一次性操作）：

```bash
bash "plugins/common/assets/cr-precommit/install.sh" /path/to/target-repo
```

脚本会自动完成：

- 复制 hook 脚本（pre-commit / **post-commit** / **pre-push**）与 Node 工具链
- 同步规则 `cr-before-commit.mdc` 到目标仓库 `.cursor/rules/`（/cr 门禁；**不**安装 `/commit`）
- 复制 GitLab CI 模板到 `.gitlab/ci/aicr-mr-coverage.yml`
- 写入 `.githooks/{pre-commit,post-commit,pre-push}` 启动器
- 执行 `git config core.hooksPath .githooks`
- 可选：`RUN_SMOKE=true` 运行 `smoke-mr-coverage.sh`
- 安装完成提示执行 **`/cr-setup-ci`**（可用 `AICR_SKIP_CI_PROMPT=1` 跳过）

预览模式：

```bash
DRY_RUN=true bash "plugins/common/assets/cr-precommit/install.sh" /path/to/target-repo
```

### 2) 本地链路自检

```bash
node ".githooks/aicr/event-log.mjs" --self-check
node ".githooks/aicr/validate-cr-gate.mjs" --self-check
bash ".githooks/pre-commit"
```

预期：

- `event-log` 输出 `SELF_CHECK_OK`
- `validate-cr-gate` 输出 `SELF_CHECK_OK`
- hook 在无 `/cr` 证据时阻断提交（退出码非 0）
- hook 在 cr 与暂存区 fingerprint 不一致时阻断提交

### 3) `/cr` 后复测

先执行一次 `/cr`（或写入 `cr_completed` 测试事件），再执行 hook。

预期：

- 本次提交通过（每次 commit 前都需有新的 `/cr` 记录）
- 提交恢复通过

### 4) MR 聚合链路自检

```bash
node ".githooks/aicr/aggregate-mr.mjs" --events ".git/aicr/events.ndjson" --commits '[]'
```

预期：

- 输出包含 `coverage_rate`、`missing_commits` 的 JSON

## 默认策略

- **事件日志**：`AICR_EVENT_LOG`，默认 `.git/aicr/events.ndjson`
- **门禁级别**：`AICR_ENFORCEMENT_MODE=hard`（默认阻断）
- **显式跳过**：`AICR_BYPASS_CR=1`（原因可选：`AICR_BYPASS_REASON`）

## 排障入口

常见问题请参考：

- `plugins/common/skills/aicr-local/references/troubleshooting.md`
