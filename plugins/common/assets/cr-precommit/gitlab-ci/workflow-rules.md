# GitLab CI 根配置要求（workflow + stages）

AICR MR 覆盖率 job 要跑起来，根配置至少满足两点：

1. **`workflow: rules`** 放行 `merge_request_event`（否则 pipeline 不创建）
2. **`stages:`** 包含 job 所用 stage（AICR 默认 `.post`；未声明会导致 CI lint 失败或 job 被跳过）

> 仅 job 级 `rules:` **不够**；仅 `include` job 文件 **不够**。

---

## 一、Workflow 审计

### Agent 必做

1. Read 根 `.gitlab-ci.yml`（及 include 链里定义 `workflow:` 的文件）
2. 是否存在 `workflow:`？
3. 是否至少一条 rule 放行 `CI_PIPELINE_SOURCE == "merge_request_event"`？
4. 缺失 → 《接入建议》中**单独列出 workflow 补丁**

### 补丁示例（追加，勿删业务 rules）

```yaml
workflow:
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
    # …保留原有 rules…
```

### 无 CI 时禁止

禁止只建 `.gitlab/ci/aicr-mr-coverage.yml` + `include` 而不写 `workflow:`。

---

## 二、Stages 审计

### Agent 必做

1. Read 根 `.gitlab-ci.yml`（及定义 `stages:` 的 include）
2. AICR job 使用 **`stage: .post`**（见 `aicr-mr-coverage.job.yml`）
3. 若文件**显式**定义了 `stages:` 列表 → 检查是否含 **`.post`**
4. 若无 `.post` → 《接入建议》中**追加** `.post` 到 `stages`（保留原有 stage 顺序，`.post` 放末尾）
5. 若**完全没有** `stages:` 段 → 新建/补丁时**必须写入** `stages:`（见下方最小示例）

### 常见现象

| 现象 | 原因 |
|------|------|
| CI Lint: stage `.post` does not exist | 显式 `stages:` 未包含 `.post` |
| Pipeline 创建但 job 被 skip | workflow 或 job rules 问题 |
| 新建根 CI 无法跑 | 缺少 `workflow:` 或 `stages:` |

### 补丁示例 A — 已有 stages，缺 `.post`

```yaml
stages:
  - build
  - test
  - deploy
  - .post   # ← 追加
```

### 补丁示例 B — 尚无 stages（与 workflow 一并写入）

```yaml
stages:
  - .post
```

### 补丁示例 C — 仅 AICR 试点（最小）

```yaml
workflow:
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
    - if: $CI_COMMIT_BRANCH && $CI_OPEN_MERGE_REQUESTS
      when: never
    - if: $CI_COMMIT_BRANCH

stages:
  - .post

include:
  - local: .gitlab/ci/aicr-mr-coverage.yml
```

（完整版见 `starter.gitlab-ci.yml`）

---

## 三、场景速查

| 场景 | workflow | stages |
|------|----------|--------|
| 无 `.gitlab-ci.yml` | 用 starter（必含） | 用 starter（必含 `.post`） |
| 有 CI，无 MR workflow | 追加 MR rule | 检查/追加 `.post` |
| workflow 在 remote include | 协调模板维护者 | 检查 remote 或根 `stages` |
| 改 job 为 `stage: report` | — | 须在 `stages` 中加 `report` 而非 `.post` |

---

## 四、验收

- [ ] MR **Pipelines** 页签出现 pipeline（source = merge request）
- [ ] CI Lint 通过（无 unknown stage）
- [ ] Job 列表含 `aicr-mr-coverage`（stage 为 `.post` 或你声明的 stage）
