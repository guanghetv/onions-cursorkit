# AICR GitLab CI 接入 — Agent 扫描清单

## 1. 前置

- [ ] 已执行 `/cr-setup`（存在 `.githooks/aicr/aggregate-mr.mjs`）
- [ ] post-commit / pre-push 已安装
- [ ] 本机 pre-push 需 `GITLAB_TOKEN`；CI 默认 `CI_JOB_TOKEN`

## 2. 扫描文件

- [ ] `.gitlab-ci.yml`（**`workflow:` + `stages:`** — 见第 2.1、2.2 节）
- [ ] `.gitlab/ci/**/*.yml`
- [ ] 远程 `include:`（是否定义 workflow / stages）

### 2.1 Workflow 审计（必做）

- [ ] 是否放行 `CI_PIPELINE_SOURCE == "merge_request_event"`？
- [ ] 新建 CI 时是否写入 `workflow:`？

### 2.2 Stages 审计（必做）

- [ ] 是否存在 `stages:` 段？定义在哪个文件？
- [ ] AICR job 使用 `stage: .post` → **`stages` 是否包含 `.post`**？
- [ ] 若无 `stages:` 段 → 新建/补丁时**必须写入**（至少 `- .post`）
- [ ] 若改 job 为其他 stage → 须在 `stages` 中声明同名 stage

> 缺 workflow → pipeline 不创建；缺 stages / 未声明 `.post` → CI lint 失败或 job 异常。

## 3. 决策

| 条件 | 建议 |
|------|------|
| 无 `.gitlab-ci.yml` | `starter.gitlab-ci.yml`（**workflow + stages + include**） |
| 有 workflow 但无 MR | 追加 MR workflow rule |
| 有 stages 但无 `.post` | 在 `stages` 末尾追加 `.post` |
| 有团队 remote include | 确认 remote 的 workflow/stages，协调补丁 |

## 4. Agent 权限（选项 2）

- 用户确认前：**不得**改 CI
- 用户确认后：可 Write；**不得** commit / push
- **禁止**只 include job 而不处理 workflow / stages

## 5. 验收

- [ ] MR Pipelines 出现 merge request pipeline
- [ ] CI Lint 无 stage 错误
- [ ] Job `aicr-mr-coverage` 存在且 MR comment 有覆盖率块

## 参考

- `workflow-rules.md` — workflow + stages 场景与补丁
- `starter.gitlab-ci.yml` — 无 CI 时的最小根文件
