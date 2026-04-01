## Why

当前 aicr-local 仅支持从 Git 暂存区获取变更进行审查（开发自审）。团队还需要对 GitLab MR 进行 Review。两者是**同一审查能力的两种输入形式**：暂存区是「开发自审」，MR 链接是「MR Review」。已在 aicr-local 中扩展 `/cr <GitLab MR 链接>`，与暂存区模式共用步骤 2–10。

## What Changes

- **MR 模式**：`/cr <GitLab MR 链接>` 触发，`input_mode=mr`；步骤 1 解析链接、匹配仓库、获取分支名与 diff；步骤 4–7 与暂存区有明确分叉。
- **分支元数据获取优先级**：优先环境变量 `GITLAB_TOKEN`（或 `GITLAB_PRIVATE_TOKEN`）+ GitLab REST API；无 Token 或 API 失败时可尝试 **GitLab MCP**（若已配置）；再退为用户手动提供 `source_branch` / `target_branch`。
- **diff**：`git fetch origin <source_branch> <target_branch>` + `git diff origin/<target_branch>...origin/<source_branch>`；仅支持 GitLab MR URL 格式。
- **仓库匹配**：`git remote get-url origin` 与 MR 的 `project_path` 不一致时 **终止审查**（非仅警告）。
- **MR 状态**：API 返回的 `state` 非 `opened` 时提示并等待用户确认是否继续。
- **branch_state 三态**（非二元 `on_source_branch`）：`source`（当前在源分支且无本地变更）、`target`（当前在目标分支且无本地变更）、`other`；决定步骤 7 上下文能力、变更量策略与报告文件位置说明。
- **Spec（MR）**：不搜工作区 `openspec/specs/`、不查 `git log`；仅 diff 内含 `openspec/specs/` 时用 `git show origin/<source_branch>:<path>` 取全文，或用户 @ 引用。
- **提示词**：MR 专属注入 `mr_title`、`mr_description`、`commits_text`（对应 `assets/prompt_template.yml` 条件块）。
- **审查维度**：**四维度**（基础规范、业务需求、影响范围、安全风险）；提示词与 `references/review_guidance.md` 已对齐。
- **权限**：`git fetch` 失败时明确报错并终止，不静默失败。

## Capabilities

### New Capabilities

- `aicr-mr-mode`：GitLab MR 链接触发、分支元数据获取（Token → MCP → 手动）、diff 获取、仓库校验、`branch_state`、大 MR 分级策略、MR 专属提示词字段。
- `aicr-mr-branch-state`：MR 模式下 `source` / `target` / `other` 三态，驱动上下文收集深度与报告行号说明。

### Modified Capabilities

（无其他 openspec delta 需改主 spec；本 change 自洽。）

## Impact

- **`.cursor/skills/aicr-local/`**：`SKILL.md`、`assets/prompt_template.yml`、`references/review_guidance.md`、`references/troubleshooting.md` 等。
- **无新增独立技能**：MR 内置于 aicr-local。
- **无应用代码**：文档与技能资源为主。
- **无 breaking change**：`/cr` 无参数时仍为暂存区模式，行为不变。
