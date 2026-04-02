## Purpose

定义 **aicr-local** 技能中 `/cr <GitLab MR 链接>`（MR 模式）的行为：与暂存区模式共用审查管线，在获取变更、Spec、上下文与报告说明上按本 spec 约束。实现见 `.cursor/skills/aicr-local/SKILL.md`。

## Requirements

### Requirement: /cr 命令支持传入 GitLab MR 链接

aicr-local 的 `/cr` 命令 SHALL 支持可选参数：当用户输入 `/cr <GitLab MR 链接>` 时，进入 MR 模式（`input_mode=mr`）；无参数时为暂存区模式（`input_mode=staged`），行为不变。

#### Scenario: 无参数触发暂存区模式
- **WHEN** 用户输入 `/cr`（无参数）
- **THEN** 系统从 `git diff --cached` 获取变更，`input_mode=staged`

#### Scenario: 传入 MR 链接触发 MR 模式
- **WHEN** 用户输入 `/cr https://gitlab.yc345.tv/backend/foo/-/merge_requests/123`
- **THEN** 系统解析链接，`input_mode=mr`，获取该 MR 的 diff 并进入后续审查流程

#### Scenario: 传入非法链接
- **WHEN** 用户输入无法解析为 GitLab MR 格式的 URL
- **THEN** 系统提示「无法识别的 MR 链接格式」，并给出标准 GitLab MR URL 示例

---

### Requirement: 解析 GitLab MR 链接

系统 SHALL 从 MR 链接中解析 `host`、`project_path`、`merge_request_iid`（iid）。SHALL 仅支持 GitLab MR URL 格式。

#### Scenario: 标准 MR 链接
- **WHEN** 链接为 `https://gitlab.yc345.tv/backend/foo/-/merge_requests/456`
- **THEN** 解析出 host、project_path=`backend/foo`、iid=`456`

#### Scenario: 多级 group
- **WHEN** 链接包含多级 path（如 `org/sub-group/repo`）
- **THEN** `project_path` 含完整路径；调用 API 时对 `project_path` 中的 `/` 进行 URL 编码（如 `%2F`）

---

### Requirement: 工作区仓库与 MR 仓库一致

系统 SHALL 将当前工作区 `git remote get-url origin` 解析出的 `project_path` 与 MR 链接中的 `project_path` 比对（支持 HTTPS 与 SSH 两种 remote 形式）。

#### Scenario: 不一致时终止
- **WHEN** 两者不一致
- **THEN** 系统输出固定错误提示（标明当前工作区与 MR 所属仓库），并 **终止审查**（不继续 fetch/diff）

#### Scenario: 一致时继续
- **WHEN** 两者一致
- **THEN** 继续获取分支名与 diff

---

### Requirement: MR 分支元数据获取顺序

系统 SHALL 按以下顺序取得 `source_branch`、`target_branch` 及（若可得）`title`、`description`、`state`：

1. 环境变量 `GITLAB_TOKEN` 或 `GITLAB_PRIVATE_TOKEN` 存在时，使用 GitLab REST API `GET /api/v4/projects/:id/merge_requests/:iid`（`test -n` 检测 Token，禁止用 `echo` 输出 Token）。
2. 无 Token 或 API 失败时，若环境提供 **GitLab MCP**，可经 MCP 获取同一套字段。
3. 仍不可得时，提示用户手动提供 `source_branch` 与 `target_branch`；此时无 MR 标题/描述则跳过 MR 信息注入。

#### Scenario: API 成功
- **WHEN** Token 可用且 API 返回 200
- **THEN** 从 JSON 提取分支名与 MR 元数据

#### Scenario: MR 状态非 opened
- **WHEN** `state` 不是 `opened`（如 `merged`、`closed`）
- **THEN** 提示审查可能不准确，并 **等待用户确认** 是否继续；用户拒绝则终止

#### Scenario: 手动分支名
- **WHEN** 用户提供了 source/target 分支名
- **THEN** 继续执行 `git fetch` 与 `git diff` 步骤

---

### Requirement: 通过本地 Git 获取 MR diff

系统 SHALL 使用 `git fetch origin <source_branch> <target_branch>`，然后 `git diff origin/<target_branch>...origin/<source_branch>` 得到 `diffs_text`，并用同源三点范围得到 `file_paths`（如 `--name-only`）。

#### Scenario: fetch 失败
- **WHEN** `git fetch` 退出码非零
- **THEN** 输出明确错误（含无法获取源分支、检查凭证与权限），并 **终止审查**

---

### Requirement: branch_state 三态

系统在取得 MR 分支名并准备审查前，SHALL 根据当前分支与 `git status --porcelain` 设置 `branch_state`：

- **`source`**：`current_branch` 等于 `source_branch` 且工作区无未提交变更（`git status --porcelain` 为空）。
- **`target`**：`current_branch` 等于 `target_branch` 且工作区无未提交变更。
- **`other`**：其余情况。

#### Scenario: 源分支且干净
- **WHEN** 条件满足 `source`
- **THEN** `branch_state=source`，步骤 7 允许全量 Read / Grep / SemanticSearch / ReadLints 等（针对 MR 语义）

#### Scenario: 目标分支且干净
- **WHEN** 条件满足 `target`
- **THEN** `branch_state=target`，步骤 7 以目标分支为影响分析基线，并可用 `git show origin/<source_branch>:<path>` 读新代码

#### Scenario: 其他
- **WHEN** 条件满足 `other`
- **THEN** 步骤 7 **不得**使用 Grep / SemanticSearch / Read / ReadLints 作为 MR 一致性依据；仅基于 diff 文本审查，并在报告中说明

---

### Requirement: 大变更量时的审查策略

当 MR 涉及的文件数超过 20 或 diff 行数超过 2000 时，系统 SHALL 按 `branch_state` 提示并采取策略：`source` 全量审查；`target` 或 `other` 优先业务类文件并提示可切换到 `source_branch` 后重试全量。

---

### Requirement: MR 模式下 Spec 来源限制

当 `input_mode=mr` 时，系统 SHALL NOT 在工作区遍历搜索 `openspec/specs/`，SHALL NOT 使用 `git log` 推断 spec。

#### Scenario: diff 中含 openspec 文件
- **WHEN** diff 中出现 `openspec/specs/` 下路径
- **THEN** 使用 `git show origin/<source_branch>:<spec_path>` 获取完整文件作为 `spec_content`

#### Scenario: 用户 @ spec
- **WHEN** 用户 @ 了 spec 文档
- **THEN** 使用该内容作为 `spec_content`

#### Scenario: 无 spec
- **WHEN** 上述均无
- **THEN** 不注入 `spec_content`，业务需求维度按「无 spec」处理

---

### Requirement: MR 提示词附加字段

MR 模式 SHALL 在构建用户提示时注入（若可得）：`mr_title`、`mr_description`、`commits_text`，并与 `assets/prompt_template.yml` 中条件块一致。

---

### Requirement: 审查维度与影响范围（MR）

系统 SHALL 采用**四维度**审查：基础规范、业务需求、影响范围、安全风险。在「影响范围」策略中，MR 模式 SHALL 遵守步骤 7 中 `branch_state` 对工具使用的限制（`other` 下不使用 Grep / SemanticSearch）。

---

### Requirement: MR 模式报告中的文件位置说明

- **WHEN** `branch_state=source`
- **THEN** 文件位置推荐使用 Markdown 链接格式，行号与本地一致，可点击跳转

- **WHEN** `branch_state` 为 `target` 或 `other`
- **THEN** 仍输出位置信息，但 SHALL 在报告末尾说明行号对应 MR 源分支、点击可能不准确，并建议切换到 `source_branch` 后重审

---

### Requirement: 与暂存区模式隔离

无 MR 链接时，系统 SHALL 仅使用 `git diff --cached`，SHALL NOT 要求 MR 相关环境变量或 `branch_state`。
