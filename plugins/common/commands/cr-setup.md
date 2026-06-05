---
name: /cr-setup
id: cr-setup
category: Code Review
description: 安装 /cr 提交前提醒与事件上报链路（默认阻断，可显式跳过）
---

# 安装 /cr 提醒链路 (/cr-setup)

调用 `cr-precommit-setup` 技能，在目标仓库一次性安装：

- pre-commit 默认阻断（可显式跳过）
- post-commit 绑定 `commit_cr_linked` + pre-push 上传 events
- `/cr` 事件日志记录
- 上报至 AI-CodeReview 服务（`/review/aicr/events`）
- pre-commit 校验 `cr_completed` 与暂存区 fingerprint 一致

> **不提供** `/commit` 命令。覆盖率聚合与 MR 发布由 AI-CodeReview 服务统一处理。

## 使用方式

```text
/cr-setup
```

推荐落地命令（仓库级一次性）：

```bash
bash "plugins/common/assets/cr-precommit/install.sh" .
```

默认即 bundled 模式（薄入口 + `vendor/aicr-runtime`），若需显式指定：

```bash
INSTALL_MODE=bundled bash "plugins/common/assets/cr-precommit/install.sh" .
```

平台批量改造（试点/扩面）：

```bash
MODE=dry-run bash "plugins/common/assets/cr-precommit/batch-rollout.sh" --repos-file /tmp/repos.txt
MODE=apply   bash "plugins/common/assets/cr-precommit/batch-rollout.sh" --repos-file /tmp/repos.txt
```

回滚：

```bash
bash "plugins/common/assets/cr-precommit/rollback-bundled-runtime.sh" /path/to/repo
```

仅预览（不落盘）：

```bash
DRY_RUN=true bash "plugins/common/assets/cr-precommit/install.sh" .
```

## 说明

- 该命令用于**安装与自检**，不是每次提交都要手动运行。
- 开发日常仍然手动运行 `/cr`；`git commit` 时由 hook 自动校验并按策略放行/阻断。
- 安装后通过 `git config core.hooksPath .githooks` 统一启用仓库内 hook。
- `cr-before-commit.mdc` 由 common 插件统一下发管理，不再复制到业务仓。
- 默认策略为阻断；如需跳过可在单次提交前设置 `AICR_BYPASS_CR=1`（可选 `AICR_BYPASS_REASON`）。
