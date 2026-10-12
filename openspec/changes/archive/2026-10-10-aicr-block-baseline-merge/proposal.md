# aicr-block-baseline-merge

## 背景

- 开发分支若含有测试环境基线尚未进入 `master` 的提交，会把未上线代码带进发版链路。
- Cursor 规则只在 Agent 执行 git 命令时拒绝。`/cr` 仍可能把这种开发分支审成通过。

## 目标

- MR 模式在业务审查之前检查源分支祖先。确认混入且未撤销时 🔴，不得写入 `cr_completed` 的 `status=pass`。
- 暂存区模式只看最近 5 条提交说明里有没有 merge 基线，避免每次审查都做祖先判断。

## 变更

- 在 `plugins/common/skills/aicr-local/SKILL.md` 步骤 1 增加基线检查，位于业务审查之前。
- 暂存区模式：`git log -5 --first-parent --format=%s HEAD`。subject 匹配 `Merge branch '<基线>'` 或 `Merge remote-tracking branch 'origin/<基线>'`（基线为 `dev`、`develop`、`test`，名字后紧跟引号）时 🔴。以 `Revert` 开头的 subject 不算命中；这 5 条里已有对应 `Revert "Merge ..."` 则该命中通过。不 fetch，不做祖先判断。早于这 5 条的 merge 不阻断。
- MR 模式：`subject` 为 `origin/<source_branch>`。
- MR 模式逐个 fetch `master`、`dev`、`develop`、`test`。基线名不存在则跳过。`fetch` 失败或 `origin/master` 不存在时，跳过检查并继续审查，不得因此 🔴。
- 跳过只看被审分支名。暂存区模式看当前分支；MR 模式看 `source_branch`。人在基线上审查功能分支 MR 时不跳过。
- MR 模式只把基线第一父历史上、且不在 `origin/master` 上的提交当作基线独有提交。这些提交里有 `subject` 的祖先才算混入。功能分支仅仅被合进基线时不命中。
- 混入之后，若第一父历史上没有对应的 merge，视为从基线切出，🔴。
- 若有这种 merge，其后第一父历史上出现 `This reverts commit <该 merge 的完整 SHA>`，且没有更新的未撤销同类 merge，则通过。没找到时 MR 模式 🔴，不用工作区 diff 豁免。

## 影响范围

- 页面/模块: `plugins/common/skills/aicr-local/SKILL.md`
- 数据/API: 无
- 兼容性: 源分支仍含未撤销的测试环境基线时，MR 模式的 `/cr` 不能 pass。暂存区模式只拦最近 5 条里的 merge 说明。

## 不做范围

- 不拦截 cherry-pick、按路径取出基线文件
- 不改 `baseline-branch-hygiene` 规则，不改发版 MR 硬闸
- 不把 fetch 失败、引用缺失或命令失败当成污染
- 暂存区模式不判断从基线切出，也不追 5 条以前的 merge

## 验证计划

- 暂存区最近 5 条含 `Merge branch 'develop'` 且无对应 Revert：🔴
- 这 5 条里已有对应 `Revert "Merge branch 'develop'..."`：通过
- merge 说明早于最近 5 条：暂存区模式不阻断
- 从 `master` 切出的分支，MR 模式：通过
- 功能分支被合进 `develop`，自身没有带出基线提交：MR 模式通过
- MR 上 `git merge develop` 且未撤销：🔴
- 没有 `origin/master` 或 fetch 失败：MR 模式跳过，不阻断
- `git revert -m 1` 的提交说明含 `This reverts commit <merge>`：MR 模式通过
- MR 从 `develop` 切出且没有 merge：🔴
- 暂存区模式当前分支就是 `develop`：跳过
- 人在 `develop` 上审查功能分支 MR：不跳过，检查 `origin/<source_branch>`
- MR 模式工作区不在源分支：仍检查 `origin/<source_branch>`
