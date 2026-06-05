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

- 复制 hook 脚本（pre-commit / **post-commit** / **pre-push**）与 Node 工具链
- 默认 bundled 模式：安装 thin hooks + `vendor/aicr-runtime`
- `cr-before-commit.mdc` 由 common 插件统一下发（不再复制到业务仓）
- 写入 `.githooks/{pre-commit,post-commit,pre-push}` 启动器
- 执行 `git config core.hooksPath .githooks`
- 上报地址通过 `AICR_INGEST_URL` 配置

预览模式：

```bash
DRY_RUN=true bash "plugins/common/assets/cr-precommit/install.sh" /path/to/target-repo
```

### 2) 本地链路自检

bundled 模式（默认）runtime 在 `vendor/aicr-runtime/`；legacy 模式在 `.githooks/aicr/`。

```bash
# 自动探测 runtime 目录（bundled 优先）
AICR_DIR=""
for resolver in vendor/aicr-runtime/resolve-runtime-dir.sh .githooks/aicr/resolve-runtime-dir.sh; do
  if [ -x "$resolver" ]; then
    AICR_DIR="$(bash "$resolver" 2>/dev/null || true)"
    if [ -n "$AICR_DIR" ] && [ -f "$AICR_DIR/event-log.mjs" ]; then
      break
    fi
    AICR_DIR=""
  fi
done

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

### 3) `/cr` 后复测

先执行一次 `/cr`（或写入 `cr_completed` 测试事件），再执行 hook。

预期：

- 本次提交通过（每次 commit 前都需有新的 `/cr` 记录）
- 提交恢复通过

### 4) 事件上报链路自检

```bash
node "$AICR_DIR/upload-events-ci.mjs" --self-check
```

预期：

- 输出 `SELF_CHECK_OK`

## 默认策略

- **事件日志**：`AICR_EVENT_LOG`，默认 `.git/aicr/events.ndjson`
- **门禁级别**：`AICR_ENFORCEMENT_MODE=hard`（默认阻断）
- **显式跳过**：`AICR_BYPASS_CR=1`（原因可选：`AICR_BYPASS_REASON`）

## 排障入口

常见问题请参考：

- `plugins/common/skills/aicr-local/references/troubleshooting.md`
