## 1. 步骤 1：获取变更（暂存区 + MR）

- [x] 1.1 统一产出 `diffs_text`、`file_paths`、`input_mode`（`staged` | `mr`）
- [x] 1.2 暂存区分支：`git diff --cached`；空暂存区提示
- [x] 1.3 MR 分支：解析 GitLab MR URL（`host`、`project_path`、`iid`）
- [x] 1.4 仓库匹配：`git remote get-url origin` 与 MR `project_path` 不一致则 **终止审查**
- [x] 1.5 分支元数据：优先 `GITLAB_TOKEN`/`GITLAB_PRIVATE_TOKEN` + REST API；备选 GitLab MCP；再退手动输入分支名
- [x] 1.6 MR `state` 非 `opened` 时提示并等待用户确认
- [x] 1.7 `git fetch origin <source_branch> <target_branch>` + 三点 `git diff`；fetch 失败则报错终止
- [x] 1.8 `branch_state`：`source` / `target` / `other`（当前分支 + `git status --porcelain`）
- [x] 1.9 大变更量：>20 文件或 >2000 行时按 `branch_state` 分流提示/策略
- [x] 1.10 `git log --oneline origin/<target>..origin/<source>` → `commits_text`

## 2. 步骤 4–7：MR 与暂存区差异

- [x] 2.1 MR：不搜工作区 openspec、不查 `git log`；spec 来自 diff 内路径 + `git show` 或用户 @
- [x] 2.2 MR：项目规则仍读工作区 `.cursor/rules/`，注明可能与 MR 分支不一致
- [x] 2.3 MR：按 `branch_state` 使用 Grep / SemanticSearch / Read / ReadLints / `git show`
- [x] 2.4 staged vs mr 对比表（步骤 4–7）

## 3. 入口、四维度、模板与报告

- [x] 3.1 frontmatter、`/cr` 与 `/cr <MR链接>`、前置条件、使用步骤、FAQ、`troubleshooting.md`
- [x] 3.2 **四维度**审查逻辑与 `review_guidance.md` 对齐；影响范围注明 MR + `branch_state`
- [x] 3.3 `prompt_template.yml`：`mr_title`、`mr_description`、`commits_text` 条件块
- [x] 3.4 步骤 9：`mr_title` / `mr_description` / `commits_text` 与模板变量对应
- [x] 3.5 MR 模式文件位置：`branch_state=source` 可点击；`target`/`other` 末尾提示行号对应源分支
- [x] 3.6 版本 `1.1.0`、版本历史

## 4. 清理与一致

- [x] 4.1 不引入独立 aicr-mr 技能
- [x] 4.2 Token 检测使用 `test -n`，不用 `echo` 泄露 Token
