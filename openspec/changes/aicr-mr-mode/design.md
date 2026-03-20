## Context

aicr-local 当前流程为 10 步：步骤 1 从暂存区取 diff → 步骤 2–10 判断类型、加载规范、查 Spec、加载规则、收集上下文、构建提示词、执行审查。整个 SKILL.md 约 327 行。

本次扩展需要在不破坏现有暂存区流程的前提下，新增 MR 链接作为第二种输入形式，且保持 SKILL 文档简洁——不翻倍、不重复流程。

**当前状态**：
- 步骤 1 硬编码为 `git diff --cached`。
- 步骤 4–5 的 Spec 查找逻辑依赖工作区 `openspec/specs/` 搜索和 `git log`。
- 步骤 6–7 的规则/影响范围分析默认工作区 = 被审分支。

## Goals / Non-Goals

**Goals:**
- `/cr` 无参数时行为不变（暂存区模式）。
- `/cr <GitLab MR 链接>` 触发 MR 模式，复用步骤 2–10。
- MR 模式仅支持 GitLab MR 链接。
- 权限不足时给出明确错误提示，不静默失败。
- 工作区与 MR 仓库不一致时给出警告，但不阻断审查。
- SKILL 文档增量控制在 40–60 行以内。

**Non-Goals:**
- 不支持 GitHub PR。
- 不创建独立的 aicr-mr 技能。
- 不引入 MCP 或 OAuth 依赖。
- 不改变现有审查报告格式或审查维度。

## Decisions

### 1. 步骤 1 改为「获取变更」，内部按有无 MR 链接分两支

**选择**：在步骤 1 内分支，统一产出 `diffs_text`、`file_paths`、`input_mode`。

**替代方案**：将 MR 逻辑拆成独立步骤（如步骤 0）。

**理由**：步骤 1 的职责就是「获取变更」，无论来源是暂存区还是 MR，产出相同。保持后续步骤 2–10 不感知来源，最小化改动面。分支逻辑只需在步骤 1 内写两段（暂存区 / MR），无需新增步骤。

### 2. MR 链接解析仅支持 GitLab 一种格式

**选择**：仅解析 `https://<host>/<group>/<repo>/-/merge_requests/<iid>` 格式。

**理由**：团队只用 GitLab，不需要额外的 GitHub/Bitbucket 解析逻辑。单一格式降低复杂度，SKILL 中只需一行正则说明。

### 3. MR diff 获取使用本地 Git

**选择**：`git fetch origin <source_branch>` + `git diff origin/<target>...origin/<source>`。

**替代方案**：GitLab API（需 Token）、GitLab MCP（需 OAuth）。

**理由**：本地 Git 使用现有 SSH/credential，无额外配置，无浏览器弹窗。source/target 分支名需要获取——优先通过 GitLab REST API（`GET /api/v4/projects/:id/merge_requests/:iid`，需 `GITLAB_TOKEN` 环境变量或 `.netrc`）；若无 Token 可回退让用户提供分支名。

### 4. 仓库匹配检查：警告但不阻断

**选择**：比对 MR 链接中的 `<group>/<repo>` 与当前工作区的 `git remote get-url origin`，不匹配时输出 `⚠️` 警告，继续执行。

**替代方案**：阻断审查、要求用户切换目录。

**理由**：用户可能在另一个目录 clone 了该仓库但 Cursor 打开的是别的仓库；也可能是同一仓库的 fork。阻断会降低体验。警告后继续，让用户自行判断结果的可靠性。diff 获取本身不依赖工作区内容（用 `git fetch` + 远程 ref 对比），即使仓库不匹配也能拿到 diff（前提是 remote 可达）。

### 5. 步骤 4–7 的 MR 差异：用一张表 + 短条收口

**选择**：在步骤 4–5 和步骤 6–7 末尾各加「当 input_mode=mr 时」短条（1–2 句），加一张对比表。

**替代方案**：为 MR 重写完整的步骤 4–7。

**理由**：差异只有 3 点（Spec 来源、规则注明、影响范围注明），无需重写整段。短条 + 表格既精确又控制篇幅。

### 6. 权限失败处理

**选择**：`git fetch` 失败时（exit code ≠ 0），输出 `🔴 无法获取 MR 源分支，请检查 git 凭证或仓库访问权限` 并终止审查。

**替代方案**：重试或回退到其他获取方式。

**理由**：权限问题需要用户介入（配置 SSH key / Token），Agent 无法自动修复。明确报错比静默失败更好。

### 7. Token 检测使用 `test -n` 而非 `echo`

**选择**：用 `test -n "${GITLAB_TOKEN:-$GITLAB_PRIVATE_TOKEN}"` 检测 Token 是否存在。

**替代方案**：使用 `echo` 输出 Token 值来判断是否为空。

**理由**：`echo` 会将 Token 明文打印到终端输出，存在安全泄露风险。`test -n` 仅返回 exit code，不暴露 Token 内容。

### 8. `git fetch` 同时拉取 source 和 target 分支

**选择**：`git fetch origin <source_branch> <target_branch>` 一次拉取两个分支。

**替代方案**：只 fetch source_branch，假设 target_branch 本地已有最新。

**理由**：`git diff origin/<target>...origin/<source>` 依赖两个远程引用都是最新的。若 target_branch（如 `main`）的本地追踪引用过旧，diff 结果会不准确。同时 fetch 保证基准正确。

### 9. MR Spec 提取使用 `git show` 获取完整文件

**选择**：当 diff 中包含 `openspec/specs/` 文件时，用 `git show origin/<source_branch>:<spec_path>` 获取完整 spec 内容。

**替代方案**：从 diff hunks 中提取 spec 内容。

**理由**：diff 只包含变更片段（hunks + 有限上下文行），不是完整文档。作为审查参考的 spec 需要完整内容才能有效验证业务需求覆盖度。

### 10. 源分支检测（`on_source_branch`）决定报告文件位置行为

**选择**：在步骤 1 获取 diff 后，检测 `git branch --show-current` == source_branch 且 `git status --porcelain` 为空，设置 `on_source_branch` 标志。

**替代方案**：始终提示行号可能不准确，不做检测。

**理由**：当用户恰好在 MR 源分支且无本地变更时，报告中的文件位置行号与本地文件完全一致，可直接点击跳转——这提供了与暂存区模式一致的体验。检测成本极低（两个 git 命令），收益明确。不在源分支时仍输出 `相对路径:行号` 格式，但在报告末尾追加提示。

## Risks / Trade-offs

- **[分支名获取依赖 GitLab API 或用户提供]** → 若无 `GITLAB_TOKEN` 且用户不提供分支名，无法自动获取 source/target。缓解：步骤 1 中先尝试 API，失败后提示用户提供分支名，形成两层 fallback。
- **[工作区非 MR 分支时影响范围不准]** → 步骤 7 的 Grep/SemanticSearch 基于当前工作区文件，可能与 MR 源分支代码不一致。缓解：报告中注明"影响范围分析基于当前工作区，仅供参考"。
- **[SKILL 篇幅增长]** → 新增约 40–60 行（含 on_source_branch 后约 90 行）。缓解：MR 解析细节不展开写，仅写要点（链接格式、git 命令）。
- **[on_source_branch 检测不覆盖 rebase 场景]** → 若用户在源分支上但做了 rebase 未推送，本地文件行号可能与远程 diff 不一致。缓解：同时检查 `git status --porcelain` 为空，要求无本地变更。
