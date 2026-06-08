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

推荐落地命令（仓库级一次性，薄入口 + `vendor/aicr-runtime`）：

```bash
bash "plugins/common/assets/cr-precommit/install.sh" .
```

安装后业务仓写入 `vendor/aicr-runtime/` 与 `.githooks/` 薄入口。升级时会自动清理已废弃的旧 runtime 文件。

平台批量改造（试点/扩面）：

```bash
MODE=dry-run REPORT_FILE=/tmp/aicr-rollout-preview.csv \
  bash "plugins/common/assets/cr-precommit/batch-rollout.sh" --repos-file /tmp/repos.txt
MODE=apply REPORT_FILE=/tmp/aicr-rollout-apply.csv \
  bash "plugins/common/assets/cr-precommit/batch-rollout.sh" --repos-file /tmp/repos.txt
```

升级 runtime 后须对当前暂存区**重新执行 `/cr`**（`diff_fingerprint` 算法变更）。

还原安装（经 Git）：

```bash
git -C /path/to/repo restore --source=HEAD~1 -- .githooks vendor/aicr-runtime
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
