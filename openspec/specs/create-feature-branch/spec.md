## Purpose

定义 **create-feature-branch** 技能（`.cursor/skills/create-feature-branch/`）在从飞书工作项创建 feature 分支时的基线门禁、例外与工作区约束，便于审计与与其它文档对照。

## Requirements

### Requirement: 默认基线分支上创建 feature 分支

技能 SHALL 在创建并推送新的 feature 分支前，使当前 HEAD 指向 **`master`** 分支的最新提交。SHALL **不**自动将基线切换为 `main` 或其它分支。SHALL 使用 `git fetch` 与 `git pull origin master`（或等价方式）更新 `master`，**禁止**在未完成基线更新前执行 `git checkout -b` 或 `git switch -c` 创建 feature 分支。

#### Scenario: 当前在 develop 上执行技能

- **WHEN** 用户触发技能且当前分支为 `develop`（或其它非 `master` 分支），且用户未明确指定基线
- **THEN** 执行者必须先检出 `master` 并拉取最新代码，再创建 feature 分支
- **AND** **禁止**在仍为 `develop` 时执行 `git checkout -b <feature>`

#### Scenario: 禁止自动使用 main

- **WHEN** 用户未明确指定以 `main` 为基线
- **THEN** **禁止**自动执行 `git checkout main` 或等价操作作为默认基线

#### Scenario: 仓库无 master 分支

- **WHEN** `git checkout master` 失败（无本地或远程 `master`）
- **THEN** SHALL 停止并提示用户（例如对齐仓库分支，或见「非默认基线的显式例外」显式指定基线）
- **AND** **禁止**在未获用户明确指示时自动改用 `main`

---

### Requirement: 创建 feature 前的门禁验证

在执行 `git checkout -b` / `git switch -c` **之前**，执行者 SHALL 验证当前分支名（例如 `git branch --show-current`）。在用户未明确指定基线时，SHALL 为 `master`；若用户明确指定了基线分支名，SHALL 与该名称一致。若验证失败，SHALL 停止创建分支并回到基线检出与更新步骤。

#### Scenario: 验证通过（默认路径）

- **WHEN** 用户未指定其它基线且 `git branch --show-current` 输出为 `master`
- **THEN** 允许继续创建 feature 分支

#### Scenario: 验证失败

- **WHEN** 当前分支不是 `master`（且未满足例外）
- **THEN** **禁止**创建 feature 分支；必须先检出 `master` 并拉取

---

### Requirement: 非默认基线的显式例外

仅当用户**明确写出**以某分支作为基线创建 feature 分支时，执行者 MAY 检出该分支并 `git pull origin <该分支>` 后创建 feature 分支。在此情况下，SHALL 在回复中说明实际使用的基线分支名。用户 MAY 显式指定 `main`、`develop` 或其它分支名。

#### Scenario: 用户指定 develop 为基线

- **WHEN** 用户明确表述「以 develop 为基线」或等价指定分支名
- **THEN** 允许从该分支创建 feature 分支
- **AND** 回复中 SHALL 标明基线分支名

#### Scenario: 用户指定 main 为基线

- **WHEN** 用户明确表述以 `main` 为基线（例如仓库仅有 `main` 且无 `master`）
- **THEN** 允许从 `main` 创建 feature 分支
- **AND** 回复中 SHALL 标明基线分支名为 `main`

---

### Requirement: 工作区洁净与既有流程

技能 SHALL 在切换分支前检查工作区无未提交变更（例如 `git status --porcelain` 为空）；若有变更，SHALL 停止并提示用户处理。飞书链接解析、任务查询、分支命名、远程存在性检查、推送与上游追踪等既有步骤 SHALL 在基线门禁满足后继续执行，且与本变更中的基线要求**不冲突**。

#### Scenario: 工作区有未提交变更

- **WHEN** `git status --porcelain` 非空
- **THEN** SHALL 停止并提示用户提交、stash 或丢弃变更后再执行
