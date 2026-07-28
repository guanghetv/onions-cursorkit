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

技能 SHALL 在切换分支前检查工作区无未提交变更（例如 `git status --porcelain` 为空）；若有变更，SHALL 停止并提示用户处理。飞书链接解析、**任务查询（Meegle CLI 优先、飞书项目 MCP 备选）**、分支命名、远程存在性检查、推送与上游追踪等既有步骤 SHALL 在基线门禁满足后继续执行，且与基线要求**不冲突**。

#### Scenario: 工作区有未提交变更

- **WHEN** `git status --porcelain` 非空
- **THEN** SHALL 停止并提示用户提交、stash 或丢弃变更后再执行

### Requirement: 飞书工作项查询优先使用 Meegle CLI

系统 MUST 在解析出主工作项 ID 后，优先通过 Meegle CLI（`@lark-project/meegle` / `meegle`）查询任务名称与规划迭代；仅当 CLI 不可用、未授权或查询失败时，才回退到飞书项目 MCP 的 `get_workitem_brief`。

#### Scenario: CLI 可用时走 CLI

- **WHEN** 用户提供有效飞书项目 detail 链接，且本机 Meegle CLI 已安装并可授权调用
- **THEN** Agent MUST 使用 `meegle workitem get`（或等价 CLI 命令）查询第一个工作项的名称与规划迭代，且 MUST NOT 在 CLI 已成功时仍先调用 MCP

#### Scenario: CLI 失败时回退 MCP

- **WHEN** Meegle CLI 未安装、授权失败或 `workitem get` 返回错误
- **THEN** Agent MUST 回退到飞书项目 MCP（`FeishuProjectMcp` / `feishu-project-mcp`）的 `get_workitem_brief` 完成同等字段查询；若 MCP 亦失败，MUST 按既有错误提示停止，不得编造任务名或迭代

### Requirement: 查询通道不改变核心建分支流程

系统 MUST 保持工作区洁净检查、默认基线 `master` 门禁、分支命名 `feat/<迭代>-<名称>-m-<ID...>`、远程存在性检查、推送与上游追踪等既有行为不变；仅调整工作项信息的查询通道优先级。

#### Scenario: 命名与基线规则不因查询通道改变

- **WHEN** 通过 CLI 或 MCP 任一通道成功取得名称与迭代
- **THEN** 分支名格式与基线门禁 MUST 与变更前一致（默认从最新 `master` 创建；迭代缺失时仍可用 `unknown`）

#### Scenario: 多链接仍只查第一个任务详情

- **WHEN** 用户一次提供多个飞书 detail 链接
- **THEN** 系统 MUST 仍只查询第一个工作项的名称与迭代，并将其余 ID 仅按 `-m-<ID>` 顺序拼入分支名

