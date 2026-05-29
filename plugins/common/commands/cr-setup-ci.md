---
name: /cr-setup-ci
id: cr-setup-ci
category: Code Review
description: Agent 分析业务仓库 GitLab CI 并接入 AICR MR 覆盖率 job（可改 CI 文件，不 commit）
---

# 接入 GitLab CI (/cr-setup-ci)

Read 并遵循 `aicr-gitlab-ci-setup` 技能，在**当前业务仓库**完成 MR 覆盖率 CI 接入。

## 权限边界（选项 2）

- ✅ 扫描 `.gitlab-ci.yml` / include 链，输出《AICR CI 接入建议》
- ✅ 用户确认后，可新增/修改 CI 文件（如 `.gitlab/ci/aicr-mr-coverage.yml`、`.gitlab-ci.yml` include）
- ❌ **不得** `git commit` 或 push；用户 review 后自行提交

## 前置

- 已执行 `/cr-setup`（存在 `.githooks/aicr/`）
- 模板参考：`.gitlab/ci/aicr-mr-coverage.yml`（install 已复制）

## 触发

```text
/cr-setup-ci
```

## 说明

- 不自动替换业务现有 pipeline；增量 job `aicr-mr-coverage`，`allow_failure: true`
- **必须审计 `workflow: rules` 与 `stages:`**：
  - 未放行 `merge_request_event` → 先补丁 workflow 再 include job
  - AICR job 用 `stage: .post` → `stages` 须含 `.post`（见 `.gitlab/ci/aicr-workflow-rules.md`）
- 仓库尚无 CI 时，参考 `.gitlab/ci/aicr-starter.gitlab-ci.yml`
- **CI**：默认 `CI_JOB_TOKEN`；**本机 pre-push**：`GITLAB_TOKEN`
