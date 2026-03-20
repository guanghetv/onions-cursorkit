## Why

当前 aicr-local 仅支持从 Git 暂存区获取变更进行审查（开发自己的代码 Review）。团队还有另一种场景：对他人或自己已提交的 GitLab MR 进行 Review。这两者是**同一审查能力的两种输入形式**——暂存区是"开发自审"，MR 链接是"MR Review"。需要在 aicr-local 技能中扩展支持 `/cr <MR链接>` 作为第二种输入形式，复用现有审查流程。

## What Changes

- 在 aicr-local 技能中新增 **MR 模式**：支持 `/cr <MR链接>` 触发，与现有暂存区模式共用步骤 2–10，仅在步骤 1（获取变更）和步骤 4–7（Spec / 规则 / 影响范围）有分叉。
- 步骤 1 统一产出 `diffs_text`、`file_paths`、`input_mode`（`staged` | `mr`），MR 模式通过本地 Git（`git fetch` + `git diff`）获取 diff，无需 MCP 或浏览器 OAuth。
- 仅支持 **GitLab MR** 链接（如 `https://gitlab.yc345.tv/group/repo/-/merge_requests/123`），不考虑 GitHub PR。
- MR 模式下 Spec 来源改为"仅 diff 内的 spec 文件或用户 @"，不在工作区自动搜索（因当前分支可能不是 MR 分支）。
- MR 模式下项目规则与影响范围分析注明"可能非 MR 分支，仅供参考"。
- 若因权限不足（如无 fetch 权限）导致无法获取 diff，需输出明确的错误提示（如"无法 fetch 源分支，请检查 git 凭证或仓库权限"），**不静默失败**。
- 若当前工作区项目与 MR 链接所属仓库不一致，需输出**警告提示**（如"当前工作区非 MR 所属仓库，影响范围分析可能不准确。若后续 fetch 失败，请在 MR 所在仓库目录中重新执行"），但**不阻断** diff 获取与审查流程。
- Token 检测使用 `test -n` 而非 `echo`，避免 Token 明文泄露到终端输出。
- `git fetch` 需同时拉取 source_branch 和 target_branch，确保 diff 基准点是最新的。
- MR 模式下 Spec 提取使用 `git show origin/<source_branch>:<spec_path>` 获取完整文件内容，而非从 diff hunks 中拼凑。
- 新增 **源分支检测**（`on_source_branch`）：获取 diff 后检测当前是否在 MR 源分支且无本地变更。若是，报告中的文件位置可直接点击跳转；否则在报告末尾提示行号对应 MR 源分支。

## Capabilities

### New Capabilities

- `aicr-mr-mode`: 在 aicr-local 中支持通过 GitLab MR 链接触发代码审查（解析链接、获取 diff、MR 模式下的 Spec/规则/影响范围差异处理、权限与仓库不匹配的提示机制）。
- `aicr-on-source-branch`: MR 模式下自动检测当前是否在 MR 源分支且无本地变更，若是则报告文件位置可点击跳转到正确行号，否则在末尾提示用户。

### Modified Capabilities

（无现有 openspec spec 需修改）

## Impact

- **`.cursor/skills/aicr-local/SKILL.md`**：frontmatter、何时使用、前置条件、步骤 1（重写，含源分支检测）、步骤 4–7（增加 MR 短条）、报告格式（MR 模式文件位置行为）、使用步骤、常见问题、版本历史。
- **无新增技能**：不创建 aicr-mr 技能，MR 模式完全内置于 aicr-local。
- **无代码变更**：本变更仅涉及 skill 文档（SKILL.md），不涉及脚本或应用代码。
- **无 breaking change**：现有 `/cr`（暂存区模式）行为完全不变。
