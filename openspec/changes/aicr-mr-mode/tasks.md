## 1. 步骤 1：重写为「获取变更」

- [x] 1.1 修改步骤 1 标题为"获取变更"，将现有暂存区逻辑包裹为"无 MR 链接时"分支
- [x] 1.2 新增"有 MR 链接时"分支：解析 GitLab MR 链接（提取 host、project_path、iid）
- [x] 1.3 实现分支名获取逻辑：优先 GitLab API（`GET /api/v4/projects/:id/merge_requests/:iid`），失败时提示用户提供 source_branch / target_branch
- [x] 1.4 实现 diff 获取：`git fetch origin <source_branch>` + `git diff origin/<target>...origin/<source>`，产出 diffs_text 和 file_paths
- [x] 1.5 实现权限失败处理：git fetch exit code ≠ 0 时输出 `🔴 无法获取 MR 源分支，请检查 git 凭证或仓库访问权限` 并终止
- [x] 1.6 实现仓库匹配检查：比对 `git remote get-url origin` 与 MR 链接的 project_path，不匹配时输出 `⚠️` 警告但继续执行
- [x] 1.7 实现非法链接提示：无法解析时输出"无法识别的 MR 链接格式"并给出示例

## 2. 步骤 4–7：增加 MR 模式差异

- [x] 2.1 步骤 4–5 末尾增加「当 input_mode=mr 时」短条：不搜工作区 openspec/specs、不查 git log；仅 diff 内 spec 或用户 @；无则跳过
- [x] 2.2 步骤 6 末尾增加注明：MR 模式下项目规则取自当前工作区，可能与 MR 分支不一致
- [x] 2.3 步骤 7 末尾增加注明：MR 模式下影响范围分析基于当前工作区，结论仅供参考
- [x] 2.4 在步骤 4–7 区域增加一张 staged vs mr 对比小表

## 3. 入口与描述更新

- [x] 3.1 frontmatter description 增加"或 GitLab MR 链接"
- [x] 3.2 「何时使用此技能」增加 `/cr <MR链接>` 触发说明，删除对 aicr-mr 的引用
- [x] 3.3 「前置条件」拆为两条：暂存区模式（git add）/ MR 模式（本地有该项目且 Cursor 打开）

## 4. 使用步骤与辅助章节

- [x] 4.1 「使用步骤」增加 MR 模式示例（贴 MR 链接 → 审查报告）
- [x] 4.2 「常见问题」增加：MR 模式行号对应 MR 源分支；权限问题排查
- [x] 4.3 「三维度审查逻辑 > 业务需求审查 > 如何识别 spec」增加一行：MR 模式下仅 diff 内 spec 或用户 @
- [x] 4.4 「版本历史」增加：支持 `/cr <GitLab MR 链接>` MR 模式

## 5. 清理

- [x] 5.1 删除 `.cursor/skills/aicr-mr/` 目录（不再需要独立技能）
- [x] 5.2 确认步骤 2、3、8、9、10 用词统一为"变更文件 / file_paths / diffs_text"，不硬编码"暂存区"

## 6. 安全与正确性修复

- [x] 6.1 Token 检测命令 `echo` 改为 `test -n`，避免 Token 明文泄露到终端
- [x] 6.2 `git fetch` 同时拉取 source_branch 和 target_branch，确保 diff 基准点最新
- [x] 6.3 MR Spec 提取改用 `git show origin/<source_branch>:<spec_path>` 获取完整文件（替代从 diff hunks 提取）
- [x] 6.4 frontmatter version 同步为 `"1.1.0"`
- [x] 6.5 仓库不匹配警告追加"若后续 fetch 失败，请在 MR 所在仓库目录中重新执行"
- [x] 6.6 用户手动提供分支名后补充交互衔接说明（"继续执行下方第 4) 步获取 diff"）

## 7. 新增源分支检测能力（`on_source_branch`）

- [x] 7.1 步骤 1 MR 模式新增第 5) 步：检测 `git branch --show-current` == source_branch 且 `git status --porcelain` 为空，设置 `on_source_branch` 标志
- [x] 7.2 步骤 7 MR 注明改为根据 `on_source_branch` 区分：true 时影响范围可靠、false 时仅供参考
- [x] 7.3 对比表更新：影响范围列改为"on_source_branch=true 时可靠；否则仅供参考"
- [x] 7.4 报告格式新增「MR 模式文件位置行为」：on_source_branch=true 时可点击跳转、false 时末尾追加提示
- [x] 7.5 FAQ 更新：MR 模式行号说明改为根据 on_source_branch 区分
- [x] 7.6 使用步骤 MR 模式更新：说明点击跳转行为
- [x] 7.7 版本历史更新
