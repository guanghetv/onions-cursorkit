---
name: aicr-gitlab-ci-setup
description: Agent 引导业务仓库接入 AICR MR 覆盖率 GitLab CI。扫描 pipeline（含 workflow: rules 与 stages），输出接入建议；用户确认后可改 CI 文件但不 commit。
---

# AICR GitLab CI 接入

在业务仓库将 MR 覆盖率 job 增量接入现有 GitLab CI。**不**替换 build/test/deploy。

## 何时使用

- 已完成 `/cr-setup`
- 需要 MR comment 展示 `/cr` 覆盖率
- 业务仓库已有或尚无 `.gitlab-ci.yml`，需定制接入

## 权限边界（选项 2 — 必须遵守）

1. 用户未确认方案前 → **禁止**修改 CI 文件
2. 用户确认后 → 可 Write `.gitlab-ci.yml`、`.gitlab/ci/**`
3. **禁止** `git commit` / `git push`
4. **禁止**修改现有 job 的 `needs` 链或删除业务 `include`

## 流程

### 1) 前置检查

- 存在 `.githooks/aicr/aggregate-mr.mjs`（否则先 `/cr-setup`）
- 存在 `.gitlab/ci/aicr-mr-coverage.yml`（install 模板；若无则从插件 Read）
- Read `gitlab-ci/workflow-rules.md` 与 `integration-checklist.md`

### 2) 扫描现有 CI

Read + Grep：

- `.gitlab-ci.yml` — **`workflow: rules` + `stages:`（必查）**
- `.gitlab/ci/**/*.yml`
- `include:` 远程/本地引用（remote 是否定义 workflow）
- `stages:`、job 级 MR `rules:`

### 2.1) Workflow 审计（必做）

**问题**：仅 job 有 `rules: merge_request_event` 不够；根 **`workflow: rules` 未放行 MR** 时，流水线根本不会创建。

Agent 必须判断：

| 情况 | 动作 |
|------|------|
| 无 `.gitlab-ci.yml` | 建议用 `starter.gitlab-ci.yml`（含 workflow + include），**勿**只建 job 文件 |
| 有 workflow，无 MR rule | 在《建议》中给出 **workflow 补丁**（追加 MR rule），与 include 一并改 |
| workflow 在 remote include | 说明来源；优先协调模板或根文件补丁，**勿**静默 assume MR 可跑 |
| workflow 已放行 MR | 仅 include job 即可 |

推荐 MR 放行规则（追加到现有 workflow，勿删业务规则）：

```yaml
workflow:
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
    # …保留原有 rules…
```

无 CI 时的推荐根文件见 `gitlab-ci/starter.gitlab-ci.yml`（**含 workflow + stages + include**）。

### 2.2) Stages 审计（必做）

AICR job 默认 **`stage: .post`**。若根配置**显式**定义了 `stages:` 但未含 `.post`，GitLab CI lint 会失败或 job 无法运行。

| 情况 | 动作 |
|------|------|
| 无 `stages:` 段 | 新建/补丁时**必须写入** `stages: [.post]`（或完整列表，`.post` 在末） |
| 有 `stages:`，无 `.post` | 在《建议》中**追加** `- .post`，保留原有 stages |
| 已有 `.post` | 无需改 stages |

```yaml
stages:
  - build
  - test
  - deploy
  - .post   # ← 若 AICR 用 .post，须存在
```

### 3) 输出《AICR CI 接入建议》

必须包含：

- **扫描结果**（**workflow 是否放行 MR**、**stages 是否含 `.post`**、include）
- **推荐方案**（local include vs remote include vs starter 根文件）
- **拟修改文件列表** 与 diff 摘要（**workflow / stages / include 分开列出**）
- **认证**：CI 默认 `CI_JOB_TOKEN`；本机 pre-push 需 `GITLAB_TOKEN`
- **风险**：缺 workflow → 无 pipeline；缺 stages/`.post` → lint 失败或 job 不跑

### 4) 用户确认后写入

**已有 CI — 典型 diff：**

```yaml
workflow:
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
    # 保留原有 workflow rules…

stages:
  - build
  - test
  - deploy
  - .post   # 若尚无 .post，追加

include:
  - local: .gitlab/ci/aicr-mr-coverage.yml
```

若已有 `workflow:` / `stages:` / `include:`，**合并**而非覆盖。

**尚无 CI — 使用 `starter.gitlab-ci.yml` 作为 `.gitlab-ci.yml`。**

### 5) 验收清单（告知用户自行验证）

- MR 页面 **Pipelines** 出现 pipeline（source = merge request）
- Job 列表含 `aicr-mr-coverage`
- MR comment 含 `<!-- aicr-coverage -->`

## 决策树

```
是否存在 .gitlab-ci.yml？
  ├─ 否 → starter.gitlab-ci.yml（workflow + stages + include）
  └─ 是 → workflow 是否放行 MR？
        ├─ 否 → 先补丁 workflow + stages（若缺 .post），再 include job
        └─ 是 → stages 是否含 .post？
              ├─ 否 → 追加 .post 到 stages，再 include job
              └─ 是 → local/remote include aicr-mr-coverage.yml
```

## MUST NOT

- **禁止**只 add job include 而不检查/修复 `workflow: rules` 与 `stages:`（MR 无法触发或 lint 失败）
- **禁止**新建 CI 时省略 `workflow:` 或 `stages:`（见 workflow-rules.md）
- 默认 `allow_failure: false`
- 未经确认改 CI

## 参考资产

- `plugins/common/assets/cr-precommit/gitlab-ci/aicr-mr-coverage.job.yml`
- `plugins/common/assets/cr-precommit/gitlab-ci/starter.gitlab-ci.yml`
- `plugins/common/assets/cr-precommit/gitlab-ci/workflow-rules.md`
- `plugins/common/assets/cr-precommit/gitlab-ci/integration-checklist.md`
