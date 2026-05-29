---
name: /cr-setup
id: cr-setup
category: Code Review
description: 安装 /cr 提交前提醒与 MR 覆盖率统计模板（默认阻断，可显式跳过）
---

# 安装 /cr 提醒链路 (/cr-setup)

调用 `cr-precommit-setup` 技能，在目标仓库一次性安装：

- pre-commit 默认阻断（可显式跳过）
- post-commit 绑定 `commit_cr_linked` + pre-push 上传 events
- `/cr` 事件日志记录
- MR 覆盖率聚合脚本 + GitLab CI 模板（`.gitlab/ci/`）
- `cr-before-commit` 规则同步到目标仓库 `.cursor/rules/`
- pre-commit 校验 `cr_completed` 与暂存区 fingerprint 一致

> **不提供** `/commit` 命令。MR CI 接入：安装完成后可执行 **`/cr-setup-ci`**（Agent 改 CI 但不 commit）。

## 使用方式

```text
/cr-setup
```

推荐落地命令（仓库级一次性）：

```bash
bash "plugins/common/assets/cr-precommit/install.sh" .
```

仅预览（不落盘）：

```bash
DRY_RUN=true bash "plugins/common/assets/cr-precommit/install.sh" .
```

## 说明

- 该命令用于**安装与自检**，不是每次提交都要手动运行。
- 开发日常仍然手动运行 `/cr`；`git commit` 时由 hook 自动校验并按策略放行/阻断。
- 安装后通过 `git config core.hooksPath .githooks` 统一启用仓库内 hook。
- 默认策略为阻断；如需跳过可在单次提交前设置 `AICR_BYPASS_CR=1`（可选 `AICR_BYPASS_REASON`）。
