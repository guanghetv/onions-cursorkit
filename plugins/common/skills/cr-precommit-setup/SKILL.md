---
name: cr-precommit-setup
description: 在业务仓库安装 /cr 提交前默认阻断与事件上报链路。用于一次性接入 pre-commit 门禁链路，后续由 hook 自动执行并上报 AI-CodeReview。
---

# CR Precommit Setup

用于在目标业务仓库一次性安装 `/cr` 提交前提醒与事件上报链路。该能力默认是**硬门禁**：缺少有效 `/cr` 记录会阻断 commit，但支持显式跳过。

## 何时使用

- 团队希望开发提交前有 `/cr` 遗漏提醒
- 希望将 `/cr` 事件统一上报至 AI-CodeReview
- 需要先小范围灰度，再逐步推广

## 安装步骤

### 1) 一键安装（推荐）

在目标仓库执行安装脚本（仓库级一次性操作）：

```bash
bash "plugins/common/assets/cr-precommit/install.sh" /path/to/target-repo
```

脚本会自动完成：

- 安装 thin hooks + `vendor/aicr-runtime`（见下方清单）
- `cr-before-commit.mdc` 由 common 插件统一下发（不再复制到业务仓）
- 写入 `.githooks/{pre-commit,post-commit,pre-push}` 启动器
- 执行 `git config core.hooksPath .githooks`
- 上报地址通过 `AICR_INGEST_URL` 配置
- **不**生成本地 `.aicr-migration-backup/`（回滚见下方）

预览模式：

```bash
DRY_RUN=true bash "plugins/common/assets/cr-precommit/install.sh" /path/to/target-repo
```

### 2) runtime 文件清单

`vendor/aicr-runtime/`：

| 文件 | 职责 |
|------|------|
| `hook-pre-commit.sh` | pre-commit 门禁编排 |
| `aicr-utils.mjs` | git 上下文 + `diff_fingerprint` |
| `validate-cr-gate.mjs` | 校验 `cr_completed` 与暂存区 |
| `event-log.mjs` | 写 NDJSON 事件 |
| `link-cr-commit.mjs` | post-commit 写 `commit_cr_linked` |
| `upload-events-ci.mjs` | pre-push 上报 events |

另由 install 生成 `.githooks/{pre-commit,post-commit,pre-push}` 薄入口（指向上述 runtime）。

升级时会自动删除已废弃的旧 runtime 文件（如 `repo-context.mjs`、`resolve-runtime-dir.sh`）。

### 3) 本地链路自检

runtime 位于 `vendor/aicr-runtime/`。

```bash
AICR_DIR="vendor/aicr-runtime"

node "$AICR_DIR/event-log.mjs" --self-check
node "$AICR_DIR/validate-cr-gate.mjs" --self-check
node "$AICR_DIR/link-cr-commit.mjs" --self-check
bash ".githooks/pre-commit"
```

预期：

- `event-log` 输出 `SELF_CHECK_OK`
- `validate-cr-gate` 输出 `SELF_CHECK_OK`
- hook 在无 `/cr` 证据时阻断提交（退出码非 0）
- hook 在 cr 与暂存区 fingerprint 不一致时阻断提交

### 4) `/cr` 后复测

先执行一次 `/cr`（或写入 `cr_completed` 测试事件），再执行 hook。

预期：

- 本次提交通过（每次 commit 前都需有新的 `/cr` 记录）
- 提交恢复通过

### 5) 事件上报链路自检

```bash
node "$AICR_DIR/upload-events-ci.mjs" --self-check
```

预期：

- 输出 `SELF_CHECK_OK`

## 平台批量改造

多仓扩面时使用 `batch-rollout.sh`（插件侧脚本，不进业务仓）：

```bash
# repos.txt：每行一个仓库绝对路径
MODE=dry-run REPORT_FILE=/tmp/aicr-rollout-preview.csv \
  bash "plugins/common/assets/cr-precommit/batch-rollout.sh" --repos-file /tmp/repos.txt

MODE=apply REPORT_FILE=/tmp/aicr-rollout-apply.csv \
  bash "plugins/common/assets/cr-precommit/batch-rollout.sh" --repos-file /tmp/repos.txt
```

可选环境变量：`LOG_DIR`、`REPORT_FILE`。

输出 CSV 列：`repo,status,reason,log_file`；`status` 为 `PREVIEW` / `UPDATED` / `UNCHANGED` / `FAILED`。

## 升级与还原

升级 runtime 后，开发者须对当前暂存区**重新执行 `/cr`**（`diff_fingerprint` 已改为基于 `git diff --cached` 内容 hash）。

若需还原 hook 与 runtime，用 Git：

```bash
git -C /path/to/target-repo restore --source=HEAD~1 -- .githooks vendor/aicr-runtime
```

## 默认策略

- **事件日志**：`AICR_EVENT_LOG`，默认 `.git/aicr/events.ndjson`
- **门禁级别**：`AICR_ENFORCEMENT_MODE=hard`（默认阻断）
- **显式跳过**：`AICR_BYPASS_CR=1`（原因可选：`AICR_BYPASS_REASON`）

## 排障入口

常见问题请参考：

- `plugins/common/skills/aicr-local/references/troubleshooting.md`
