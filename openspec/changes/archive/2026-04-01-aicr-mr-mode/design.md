## Context

aicr-local 流程为步骤 1–10：步骤 1 按输入获取 diff（暂存区或 MR）→ 步骤 2–10 判断类型、加载规范、Spec、规则、上下文、模板、审查输出。MR 模式在步骤 1、4–7、9–10 与暂存区有差异；`SKILL.md` 为单一事实来源（当前约 500+ 行，含 MR 专章）。

## Goals / Non-Goals

**Goals:**

- `/cr` 无参数：行为不变（`git diff --cached`）。
- `/cr <GitLab MR 链接>`：MR 模式，复用步骤 2–3、8 及共用审查逻辑。
- 仅支持 GitLab MR URL；`git fetch` 失败时明确报错并终止。
- 工作区 remote 与 MR 仓库不一致时 **终止**，避免误审。
- 用 **`branch_state`**（`source` | `target` | `other`）区分上下文可信度与工具使用范围。

**Non-Goals:**

- 不支持 GitHub PR、不支持 fork MR 的完整自动化（源分支不在 `origin` 等场景未单独建模）。
- 不强制依赖 GitLab MCP；MCP 仅为获取 MR 元数据的**备选**（多数人无 MCP，优先 Token）。

## Decisions

### 1. 步骤 1 统一产出 `diffs_text`、`file_paths`、`input_mode`

在步骤 1 内分「无 MR 链接」与「有 GitLab MR 链接」两支，后续步骤 2–10 以 `input_mode` 与 MR 专有变量（如 `branch_state`）为条件。

### 2. MR 链接仅 GitLab 标准格式

`https://<host>/<group>/<repo>/-/merge_requests/<iid>`（含多级 group）；`project_path` 用于 API 路径需将 `/` 编码为 `%2F`。

### 3. 分支名：API → MCP → 手动

- 优先：`GITLAB_TOKEN` / `GITLAB_PRIVATE_TOKEN` + `curl` 调 `GET .../merge_requests/:iid`。
- 备选：GitLab MCP（若启用）拉取同套字段。
- 再退：用户输入 `source_branch`、`target_branch`；无 title/description 时不注入 MR 信息块。

Token 存在性检测使用 `test -n "${GITLAB_TOKEN:-$GITLAB_PRIVATE_TOKEN}"`，禁止用 `echo` 打印 Token。

### 4. 仓库匹配：不一致则终止

比对 MR 的 `project_path` 与 `git remote get-url origin` 解析结果；不一致则输出固定文案并 **终止审查**（与「警告后继续」的旧草案不同）。

### 5. diff 命令

`git fetch origin <source_branch> <target_branch>`，然后 `git diff origin/<target_branch>...origin/<source_branch>`；`file_paths` 用 `git diff --name-only` 同源。

### 6. `branch_state` 三态（取代二元 `on_source_branch`）

在取得分支名后：若 `current_branch == source_branch` 且 `git status --porcelain` 为空 → `source`；若 `current_branch == target_branch` 且工作区干净 → `target`；否则 → `other`。

- **`source`**：工作区即 MR 侧新代码，可 Read / Grep / SemanticSearch / ReadLints 等全量能力。
- **`target`**：工作区为合入前基线，适合影响分析；新代码可用 `git show origin/<source_branch>:<path>` 补充；ReadLints 不适用工作区为新代码。
- **`other`**：仅基于 diff 文本；**不使用** Grep / SemanticSearch / Read / ReadLints（避免误导）。

### 7. 大变更量阈值

超过 20 个文件或 diff 超过 2000 行：`source` 全量审查并提示；`target` / `other` 优先业务文件并提示可切到源分支全量审。

### 8. 提交历史

`git log --oneline origin/<target_branch>..origin/<source_branch>` → `commits_text`，注入步骤 9。

### 9. MR 非 `opened` 状态

从 API（或 MCP）得到 `state` 非 `opened` 时，提示并 **等待用户确认** 是否继续。

### 10. Spec（MR）

不遍历工作区 `openspec/specs/`、不用 `git log` 找 spec；仅 diff 中出现 `openspec/specs/` 时用 `git show` 取全文，或用户 @。

### 11. 步骤 9 与模板

MR 专属：`mr_title`、`mr_description`、`commits_text`（与 `prompt_template.yml` 中 `{% if mr_title %}` 等一致）。

### 12. 四维度审查

基础规范、业务需求、影响范围、安全风险；影响范围在 MR 且 `branch_state=other` 时不在此节单独用 Grep（见步骤 7）。

## Risks / Trade-offs

- **无 Token 且 MCP 不可用**：需用户手动分支名；体验下降但可接受。
- **`target` 与 `source` 行号**：报告在非 `source` 时末尾提示行号对应 MR 源分支、点击可能不准。
- **SKILL 篇幅**：MR 完整流程较长；以表格与分点压缩重复。
