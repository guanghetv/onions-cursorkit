# 常见问题 (Troubleshooting)

## 使用问题

### Q: 为什么提示"暂存区为空"？

**原因**：Git暂存区没有待审查的文件。

**解决方案**：
```bash
# 添加单个文件
git add src/components/UserProfile.tsx

# 或添加所有变更
git add .

# 然后执行审查
/cr
```

### Q: 审查结果过于简短，只有几条建议？

**这是正常的**。极简输出是设计理念，只关注核心问题：
- 如果代码质量良好，会输出 "✅ 无明显问题"
- 如果有问题，只会列出需要修复的严重问题和改进建议
- 避免信息过载，让开发者快速定位关键点

### Q: 可以审查未暂存的文件吗？

**不可以**。必须先使用 `git add` 添加到暂存区。

**原因**：
- 明确审查范围，避免误审工作目录中的临时文件
- 与Git工作流保持一致
- 确保审查的是即将提交的代码

### Q: 审查时间过长？

**可能原因**：
1. 暂存区文件过多 → 建议分批审查
2. 工作区上下文过大 → 系统会自动精简，优先保留核心内容
3. Spec文档过长 → 系统会智能摘要

**优化建议**：
- 每次审查控制在10个文件以内
- 将大的变更拆分为多个小的提交

### Q: 为什么每次提交都被阻断并提示先执行 /cr？

**可能原因**：
1. 尚未安装 pre-commit 提醒链路（未执行 `/cr-setup`）
2. 事件日志路径不正确（默认 `.git/aicr/events.ndjson`）
3. 上一次 `/cr` 发生在更早的提交周期（每次 commit 前都需要新的 `/cr` 记录）
4. 当前分支或用户与事件记录不匹配

**排查步骤**：
```bash
# 1) 查看是否存在 cr_completed 事件
rg "cr_completed" ".git/aicr/events.ndjson"

# 2) 检查 pre-commit hook 是否正确指向
ls -l ".git/hooks/pre-commit"

# 3) 检查环境变量（可选）
echo "${AICR_EVENT_LOG:-.git/aicr/events.ndjson}"
echo "${AICR_ENFORCEMENT_MODE:-hard}"
```

临时跳过（单次提交）：
```bash
AICR_BYPASS_CR=1 AICR_BYPASS_REASON="hotfix" git commit -m "..."
```

### Q: `/cr-setup` 和 `/cr` 的关系是什么？

`/cr-setup` 是**一次性安装命令**，用于接入提醒与统计链路；`/cr` 是**日常自检命令**，开发提交前仍需手动执行。

工作模式：
- 人工：开发者执行 `/cr`
- 自动：执行 `git commit` 时 hook 自动校验（默认阻断，可显式跳过）
- 自动：MR 阶段聚合覆盖率并输出统计

### Q: 执行了 `/cr`，为什么仍然提示没有 `cr_completed` 记录？

**可能原因**：
1. 仓库未安装提醒链路（缺少 `.githooks/aicr/event-log.mjs`）
2. `/cr` 的步骤 11 未执行到（被中断或脚本路径不匹配）
3. 当前工作区没有暂存文件，`files` 指纹为空且不满足后续策略

**排查步骤**：
```bash
# 检查 logger 是否存在
ls ".githooks/aicr/event-log.mjs"

# 手动验证写事件
repo="$(basename "$(git rev-parse --show-toplevel)")"
branch="$(git branch --show-current)"
author="$(git config user.email || echo unknown)"
node ".githooks/aicr/event-log.mjs" "{\"event\":\"cr_completed\",\"repo\":\"$repo\",\"branch\":\"$branch\",\"author\":\"$author\"}"

# 检查日志中是否落盘
rg "cr_completed" ".git/aicr/events.ndjson"
```

### Q: `/cr` 报告有问题，为什么 commit 仍被阻断？

**设计如此**：pre-commit 只接受 `cr_completed` 且 `status=pass`。报告含 🔴/🟠 时：

1. **不得**写入 `status=pass` 的 `cr_completed`
2. Agent **不得**擅自改代码后再提交
3. 须由开发者修复 → `git add` → 重新完整 `/cr` → 结论 `✅ 无明显问题` 后再 commit

若 hook 提示「报告存在问题」或「未标记为 pass」，检查最近一条 `cr_completed` 的 `status` 字段。

## MR 覆盖率与 GitLab CI

### Q: MR 覆盖率 comment 恒为 0%？

**排查顺序**：

1. post-commit 是否安装：`ls .githooks/post-commit`，commit 后是否有 `commit_cr_linked`：
   ```bash
   rg "commit_cr_linked" ".git/aicr/events.ndjson"
   ```
2. pre-push 是否上传 events（**本机**需 `GITLAB_TOKEN`，PAT 等；`CI_JOB_TOKEN` 仅在 Runner 内可用）：
   ```bash
   git push  # 观察 UPLOAD_OK 或 SKIP_UPLOAD_NO_TOKEN
   ```
3. CI 是否 include `.gitlab/ci/aicr-mr-coverage.yml`（或 `/cr-setup-ci` 接入）
4. CI **默认用 `CI_JOB_TOKEN`**，一般无需项目 Variables；若 job 报 403，再配 `GITLAB_TOKEN` fallback

**本地 smoke**：

```bash
RUN_SMOKE=true bash .githooks/aicr/smoke-mr-coverage.sh .
```

### Q: 业务仓库已有 GitLab CI，如何接入？

1. 确保已 `/cr-setup`
2. 在 Cursor 执行 **`/cr-setup-ci`** — Agent 扫描现有 pipeline（**含 `workflow: rules` 与 `stages:`**）并给出方案
3. Agent **可改 CI 文件但不 commit**；你 review 后自行提交
4. 参考：`.gitlab/ci/aicr-integration-checklist.md`、`workflow-rules.md`

### Q: 已 include AICR job，但 MR 没有 pipeline？

**常见原因**：根 `.gitlab-ci.yml` 的 **`workflow: rules` 未放行 `merge_request_event`**。Job 级 `rules` 无法单独创建 pipeline。

**处理**：

1. 打开 `.gitlab-ci.yml`，检查 `workflow:` 段（可能在 remote include 里）
2. 追加：`- if: $CI_PIPELINE_SOURCE == "merge_request_event"`
3. 若仓库尚无 CI，使用 install 复制的 `starter.gitlab-ci.yml` 作根配置
4. 重新开 MR 或 push，确认 Pipelines 页签出现 merge request pipeline

### Q: CI Lint 报 stage `.post` does not exist？

**常见原因**：根 `.gitlab-ci.yml` **显式定义了 `stages:`**，但未包含 AICR job 使用的 **`.post`**。

**处理**：

1. 在 `stages:` 列表**末尾**追加 `- .post`（保留原有 build/test/deploy 等）
2. 若仓库尚无 CI，使用 install 复制的 `starter.gitlab-ci.yml`（已含 `stages: [.post]`）
3. 运行 CI Lint 或重新 push，确认 job `aicr-mr-coverage` 出现在 pipeline 中

### Q: 点击文件位置链接无法跳转？

**可能原因**：
- Cursor版本过旧，不支持文件链接格式
- 文件路径不正确（使用相对路径）
- MR 模式下当前不在源分支，行号与本地文件不一致

**解决方案**：
- 更新到最新版本的Cursor
- 手动复制路径和行号打开文件
- MR 模式下切换到源分支：`git checkout <source_branch>`

## MR 模式问题

### Q: 提示"无法识别的 MR 链接格式"？

**原因**：MR 链接格式不符合 GitLab 标准。

**支持格式**：`https://<host>/<group>/<repo>/-/merge_requests/<iid>`（含多级 group）。

**常见错误**：
- 缺少 `/-/` 分隔符
- 使用了 GitHub PR 链接格式
- URL 被截断

### Q: 提示"无法获取 MR 源分支"（git fetch 失败）？

**排查步骤**：
1. 检查 git 凭证：`git remote get-url origin`，确认有该仓库的读权限
2. 检查分支名是否正确：分支可能已被删除
3. 检查网络连接：确认可以访问 GitLab 服务器
4. 仓库不匹配：当前工作区可能不是 MR 所在仓库，在正确的仓库目录中重新执行

### Q: 提示"该 MR 状态为 merged/closed"？

**说明**：MR 已合并或已关闭，审查结果可能不准确（diff 可能与预期不同）。

**建议**：
- 对于已合并的 MR，可直接在目标分支上查看最终代码
- 对于已关闭的 MR，确认是否还需要审查

### Q: MR 模式没有 Token，提示手动输入分支名？

**原因**：未配置 `GITLAB_TOKEN` 或 `GITLAB_PRIVATE_TOKEN`，且无法通过 GitLab MCP 获取 MR 信息（多数人未配置 MCP，属常见情况）。

**解决方案**（推荐顺序）：
1. **优先**：设置环境变量：`export GITLAB_TOKEN=<your-token>`，本地 Token + `curl` 不依赖 MCP，适用面最广。
2. **备选**：若已启用 GitLab MCP，可由 Agent 通过 MCP 拉取 MR 元数据，无需自行填分支。
3. **再退**：按提示手动输入 `source_branch` 与 `target_branch`。

### Q: MR 变更量很大，审查质量下降？

**原因**：MR 包含大量文件/行数，超出建议的审查范围。

**优化建议**：
- 系统会自动提示并优先审查核心业务文件
- 可请求分批审查："请只审查 `src/services/` 目录下的变更"
- 从源头减少：推动团队拆分大 MR

### Q: MR 模式行号与当前文件对不上？

**原因**：当前不在 MR 源分支上，或本地有未提交的变更。

**解决方案**：
```bash
git checkout <source_branch>
git pull origin <source_branch>
/cr <MR链接>
```
重新审查后，文件位置可直接点击跳转。

## 配置问题

### Q: 如何添加新的规范文档（如移动端规范）？

1. 在 `references/` 目录添加新文档：
   ```bash
   # 例如添加iOS规范
   vim .cursor/skills/aicr-local/references/ios_standard.md
   ```

2. 在 `SKILL.md` 的步骤3中更新加载逻辑

3. 在 `review_guidance.md` 中补充对应的审查说明

## 审查结果问题

### Q: 为什么没有检测到某个明显的问题？

**可能原因**：
1. 问题不在暂存区的变更中
2. 规范文档未覆盖该检查项
3. 上下文收集未包含相关代码

**改进方法**：
- 确认问题代码已 `git add`
- 更新规范文档补充检查项
- 在对话中明确提及需要关注的点

### Q: 审查结果与实际不符？

**排查步骤**：
1. 检查暂存区内容：`git diff --cached`
2. 确认规范文档是最新的
3. 查看是否有spec文档被错误识别
4. 检查项目规则（`.cursor/rules/`）是否冲突

### Q: 如何让审查更严格/更宽松？

**调整方法**：
1. 编辑 `assets/prompt_template.yml` 中的 `system_prompt`
2. 在规范文档中添加或删除检查项
3. 修改 `references/review_guidance.md` 调整审查重点

**注意**：极简输出原则不变，只调整检查标准。

## Spec相关问题

### Q: 为什么没有识别到相关的spec文档？

**检查清单**：
1. Spec文件是否在 `openspec/specs/` 目录下？
2. 暂存区是否包含spec文件变更？
3. 是否使用 @ 引用了spec？
4. 最近5次提交是否涉及该spec？

**手动指定**：在对话中明确说明：
```
请参考 @openspec/specs/user-auth/spec.md 审查当前变更
```

### Q: Spec文档过长导致审查变慢？

系统会自动摘要spec内容，保留核心Requirements和Scenarios。

**优化建议**：
- 保持spec文档精简，避免冗余
- 使用多个小spec而不是一个大spec
- 在对话中明确指出关注的Requirement

## 工作区上下文问题

### Q: 为什么没有发现某个函数的其他调用位置？

**可能原因**：
1. 函数名搜索范围受限
2. 调用位置在被忽略的目录中（如node_modules）
3. 使用了动态调用方式

**改进方法**：
- 在对话中明确提及："请检查XX函数的所有调用位置"
- 手动使用Grep搜索确认

### Q: 上下文收集是否会影响审查速度？

会有一定影响，但系统做了优化：
- 优先收集直接相关的内容
- 自动限制搜索范围
- 按需加载，避免过载

**如果仍然较慢**：可以在对话中说明"仅审查变更本身，不收集工作区上下文"。

## 技术限制

### Q: 哪些代码类型不支持？

**完全支持**：
- 前端：TypeScript, JavaScript, Vue, React
- 后端：Go, Python, Java, Rust

**部分支持**（无内置规范，使用业内标准）：
- iOS: Swift, Objective-C
- Android: Kotlin, Java
- HarmonyOS: ArkTS

**不支持**：
- 二进制文件
- 加密/混淆代码
- 生成的代码（如protobuf生成的文件）

### Q: 最大能审查多少文件？

**建议限制**：
- 单次审查 ≤ 10个文件
- 总变更行数 ≤ 500行

**超出限制时**：
- 系统会提示分批审查
- 可能省略部分上下文收集
- 建议拆分为多个小的提交

## 反馈和改进

### Q: 如何报告问题或提出改进建议？

1. 在项目issue中反馈
2. 更新 `SKILL.md` 或 `references/` 文档
3. 调整 `prompt_template.yml` 优化提示词

### Q: 如何查看skill版本？

查看 `SKILL.md` frontmatter 中的 `metadata.version` 字段。

当前版本：**v1.1.0**

---

**提示**：大部分问题可以通过查看 `SKILL.md` 主文档和 `references/` 目录下的参考文档解决。
