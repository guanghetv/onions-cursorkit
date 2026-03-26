## ADDED Requirements

### Requirement: /cr 命令支持传入 GitLab MR 链接

aicr-local 的 `/cr` 命令 SHALL 支持可选参数：当用户输入 `/cr <GitLab MR 链接>` 时，进入 MR 模式（`input_mode=mr`）；无参数时保持暂存区模式（`input_mode=staged`），行为不变。

#### Scenario: 无参数触发暂存区模式
- **WHEN** 用户输入 `/cr`（无参数）
- **THEN** 系统从 `git diff --cached` 获取变更，`input_mode=staged`，行为与现有流程完全一致

#### Scenario: 传入 MR 链接触发 MR 模式
- **WHEN** 用户输入 `/cr https://gitlab.yc345.tv/backend/foo/-/merge_requests/123`
- **THEN** 系统解析链接，进入 MR 模式（`input_mode=mr`），获取该 MR 的 diff 进行审查

#### Scenario: 传入非法链接
- **WHEN** 用户输入 `/cr https://example.com/not-a-mr`
- **THEN** 系统提示"无法识别的 MR 链接格式，请提供 GitLab MR 链接（如 https://gitlab.example.com/group/repo/-/merge_requests/123）"

---

### Requirement: 解析 GitLab MR 链接

系统 SHALL 从 GitLab MR 链接中解析出 `host`、`project_path`（group/repo）、`merge_request_iid`。仅支持 GitLab MR 格式。

#### Scenario: 标准 GitLab MR 链接
- **WHEN** 链接为 `https://gitlab.yc345.tv/backend/foo/-/merge_requests/456`
- **THEN** 解析出 host=`gitlab.yc345.tv`、project_path=`backend/foo`、iid=`456`

#### Scenario: 多级 group 的 GitLab MR 链接
- **WHEN** 链接为 `https://gitlab.com/org/sub-group/repo/-/merge_requests/789`
- **THEN** 解析出 host=`gitlab.com`、project_path=`org/sub-group/repo`、iid=`789`

---

### Requirement: 通过本地 Git 获取 MR diff

系统 SHALL 通过本地 Git 命令获取 MR 的 diff，产出 `diffs_text` 和 `file_paths`。需先获取 source_branch 和 target_branch（优先 GitLab API，回退为让用户提供）。Token 检测 SHALL 使用 `test -n` 而非 `echo`，避免 Token 明文泄露。`git fetch` SHALL 同时拉取 source_branch 和 target_branch。

#### Scenario: 通过 GitLab API 获取分支名并取 diff
- **WHEN** 环境中有 `GITLAB_TOKEN` 或 `GITLAB_PRIVATE_TOKEN`（通过 `test -n` 检测）
- **THEN** 系统调用 `GET /api/v4/projects/:id/merge_requests/:iid` 获取 `source_branch` 和 `target_branch`，然后执行 `git fetch origin <source_branch> <target_branch>` 和 `git diff origin/<target>...origin/<source>` 获取 diff

#### Scenario: 无 API Token 时回退
- **WHEN** GitLab API 调用失败（无 Token 或网络不可达）
- **THEN** 系统提示用户提供 source_branch 和 target_branch 名称，用户提供后继续执行获取 diff 步骤

---

### Requirement: 权限不足时给出明确错误提示

当 `git fetch` 因权限不足失败时，系统 SHALL 输出明确的错误提示并终止审查，不得静默失败。

#### Scenario: fetch 失败
- **WHEN** `git fetch origin <source_branch>` 返回非零 exit code
- **THEN** 系统输出 `🔴 无法获取 MR 源分支 <source_branch>，请检查 git 凭证或仓库访问权限` 并终止审查

---

### Requirement: 工作区与 MR 仓库不一致时警告但不阻断

当工作区的 `git remote get-url origin` 与 MR 链接中的仓库不匹配时，系统 SHALL 输出警告提示但继续执行 diff 获取与审查。

#### Scenario: 仓库不匹配
- **WHEN** 当前工作区 remote origin 为 `git@gitlab.yc345.tv:backend/bar.git`，MR 链接指向 `backend/foo`
- **THEN** 系统输出 `⚠️ 当前工作区（backend/bar）与 MR 所属仓库（backend/foo）不一致，影响范围分析可能不准确。若后续 fetch 失败，请在 MR 所在仓库目录中重新执行` 并继续审查

#### Scenario: 仓库匹配
- **WHEN** 当前工作区 remote origin 与 MR 链接的仓库一致
- **THEN** 系统不输出警告，正常执行

---

### Requirement: MR 模式下 Spec 来源限制

当 `input_mode=mr` 时，Spec 查找逻辑 SHALL 与暂存区模式不同：不在工作区搜索 `openspec/specs/`、不查 `git log`。

#### Scenario: diff 中包含 spec 文件
- **WHEN** MR 的 diff 中包含 `openspec/specs/` 路径下的文件变更
- **THEN** 系统使用 `git show origin/<source_branch>:<spec_path>` 获取完整 spec 文件内容作为 `spec_content`（不从 diff hunks 提取，diff 只含变更片段）

#### Scenario: 用户 @ 了 spec
- **WHEN** 用户在对话中通过 @ 引用了 spec 文档
- **THEN** 系统使用用户 @ 的文档内容作为 `spec_content`

#### Scenario: 无 spec
- **WHEN** diff 中无 spec 文件且用户未 @
- **THEN** 系统不注入 spec_content，跳过业务需求审查维度

---

### Requirement: MR 模式下项目规则与影响范围注明

当 `input_mode=mr` 时，系统 SHALL 根据 `on_source_branch` 标志决定影响范围分析结论的注明方式。

#### Scenario: 在源分支上且无本地变更
- **WHEN** 审查在 MR 模式下执行且 `on_source_branch = true`
- **THEN** 影响范围分析结论可靠，无需额外注明

#### Scenario: 不在源分支上或有本地变更
- **WHEN** 审查在 MR 模式下执行且 `on_source_branch = false`
- **THEN** 报告末尾注明"以上影响范围分析基于当前工作区，当前分支可能非 MR 源分支，结论仅供参考"

---

### Requirement: 源分支检测（`on_source_branch`）

MR 模式获取 diff 后，系统 SHALL 检测当前是否在 MR 源分支且无本地变更，设置 `on_source_branch` 标志，用于决定报告中文件位置的点击跳转行为和影响范围注明。

#### Scenario: 在源分支上且无本地变更
- **WHEN** `git branch --show-current` == source_branch 且 `git status --porcelain` 输出为空
- **THEN** 设置 `on_source_branch = true`，报告中文件位置（`相对路径:行号`）可直接点击跳转到对应行

#### Scenario: 不在源分支上
- **WHEN** `git branch --show-current` != source_branch
- **THEN** 设置 `on_source_branch = false`，报告中仍使用 `相对路径:行号` 格式，但在报告末尾追加提示："💡 当前工作区非 MR 源分支，文件位置行号对应 MR 源分支，点击跳转可能不准确。可切换到源分支（git checkout <source_branch>）后重新审查以获得准确跳转。"

#### Scenario: 在源分支上但有本地变更
- **WHEN** `git branch --show-current` == source_branch 但 `git status --porcelain` 输出非空
- **THEN** 设置 `on_source_branch = false`（本地变更可能导致行号偏移），行为同"不在源分支上"
