# aicr-baseline-merge Specification

## Purpose
TBD - created by archiving change aicr-block-baseline-merge. Update Purpose after archive.
## Requirements
### Requirement: 审查前检查开发分支是否混入测试环境基线

系统 MUST 在业务审查之前检查。测试环境基线为 `dev`、`develop`、`test`。`master` 不是基线。跳过只看被审分支名：暂存区模式 MUST 在当前分支名是这些基线之一时跳过；MR 模式 MUST 在 `source_branch` 是这些基线之一时跳过。工作区当前分支是基线、MR 源分支不是基线时，MUST NOT 跳过。

暂存区模式 MUST 只看当前分支最近 5 条第一父提交的 subject，命令为 `git log -5 --first-parent --format=%s HEAD`。MUST NOT 为此 fetch，MUST NOT 做祖先或 patch-id 判断。subject 同时满足以下条件时判定命中：

- 不以 `Revert` 开头
- 匹配 `Merge branch '<基线>'` 或 `Merge remote-tracking branch 'origin/<基线>'`
- 基线名后紧跟结束引号，避免把 `develop-hotfix` 这类名字当成 `develop`

这 5 条里若另有 subject 以 `Revert "Merge branch '<同一基线>'` 或 `Revert "Merge remote-tracking branch 'origin/<同一基线>'` 开头，则该命中通过。仍有未这样撤销的命中时，报告 MUST 包含 🔴，结论 MUST NOT 为通过，MUST NOT 写入 `status=pass` 的 `cr_completed`。`git log` 失败时 MUST 跳过，MUST NOT 因此 🔴。早于这 5 条的 merge，暂存区模式 MUST NOT 阻断。

MR 模式的 `subject` MUST 是 `origin/<source_branch>`，MUST NOT 用工作区 `HEAD` 代替。系统 MUST 逐个 fetch `master` 与基线。不存在的基线名 MUST 跳过。`fetch` 失败、`origin/master` 不存在时，MUST 跳过本检查并继续业务审查，MUST NOT 因此输出 🔴 或拒绝 pass。

对每个现存基线 `B`，系统 MUST 只把 `git rev-list --first-parent origin/B --not origin/master` 的提交当作基线独有提交。这些提交都不是 `subject` 的祖先时，该基线通过。

有此类提交是 `subject` 的祖先时，系统 MUST 在 `subject` 的第一父历史上查找第二父属于这些提交的 merge。找不到时 MUST 视为从基线切出并判定污染。找到 merge `M` 时，若 `M..subject` 的第一父历史上存在正文包含 `This reverts commit <M>` 的提交，且其后没有新的未撤销同类 merge，该基线通过。没找到该撤销提交时 MUST 判定污染，MUST NOT 用工作区 diff 豁免。

MR 确认污染时，审查报告 MUST 包含 🔴，并写明基线名。结论 MUST NOT 为通过，MUST NOT 写入 `status=pass` 的 `cr_completed`。

#### Scenario: 暂存区最近 5 条出现 merge 基线

- **WHEN** 暂存区模式，当前分支最近 5 条第一父 subject 含 `Merge branch 'develop'`（或 `dev`、`test`，以及 `origin/<基线>` 的 remote-tracking 形式），且这 5 条里没有对应的 `Revert "Merge ..."`
- **THEN** 报告输出 🔴，不得 pass

#### Scenario: 暂存区最近 5 条已 revert 该 merge

- **WHEN** 上述 merge subject 与对应的 `Revert "Merge branch '<基线>'..."` 都在最近 5 条里
- **THEN** 该项检查通过，`/cr` 继续业务审查

#### Scenario: merge 基线早于最近 5 条

- **WHEN** 暂存区模式，`Merge branch 'develop'` 不在最近 5 条第一父 subject 中
- **THEN** 暂存区模式不因此 🔴

#### Scenario: 从 master 切出的干净功能分支

- **WHEN** MR 的源分支不包含 `dev`、`develop`、`test` 第一父历史上尚未进入 `master` 的提交
- **THEN** 该项检查通过，`/cr` 继续业务审查

#### Scenario: 功能分支被合进测试环境基线

- **WHEN** 功能分支自己的提交已进入 `develop`，但 `develop` 第一父历史上尚未进入 `master` 的提交都不是该功能分支的祖先
- **THEN** MR 模式该项检查通过

#### Scenario: MR 上 merge 了测试环境基线且未撤销

- **WHEN** MR 源分支 merge 过 `develop`（或 `dev`、`test`），基线独有提交是其祖先，其后没有 `This reverts commit <该 merge>`
- **THEN** 报告输出 🔴，不得 pass

#### Scenario: MR 上 merge 已 revert

- **WHEN** MR 源分支从 `master` 切出并 merge 过基线，其后第一父历史上有提交正文包含 `This reverts commit <该 merge>`
- **THEN** 该项检查通过，`/cr` 继续业务审查

#### Scenario: MR 从测试环境基线切出

- **WHEN** MR 源分支从 `develop` 切出，基线独有提交是其祖先，且第一父历史上没有对应的 merge
- **THEN** 报告输出 🔴，不得 pass

#### Scenario: 引用无法确认

- **WHEN** MR 模式中 `origin/master` 不存在，或 fetch 失败
- **THEN** 跳过该项，不输出 🔴，继续业务审查

#### Scenario: 当前就在测试环境基线上做暂存区审查

- **WHEN** 暂存区模式，当前分支名是 `dev`、`develop` 或 `test`
- **THEN** 跳过该项检查

#### Scenario: 人在基线上审查功能分支 MR

- **WHEN** `/cr` 带 MR 链接，工作区当前分支是 `develop`，MR 的 `source_branch` 是功能分支
- **THEN** 不得跳过，检查 `origin/<source_branch>`

#### Scenario: MR 审查时人不在源分支

- **WHEN** `/cr` 带 MR 链接，且工作区当前分支不是 MR 的 `source_branch`
- **THEN** 检查 `origin/<source_branch>`，不检查工作区 `HEAD`

