# create-feature-branch

根据飞书项目工作项链接创建标准化 feature 分支；查询工作项信息时优先 Meegle CLI，MCP 为备选。

## ADDED Requirements

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

## MODIFIED Requirements

### Requirement: 工作区洁净与既有流程

技能 SHALL 在切换分支前检查工作区无未提交变更（例如 `git status --porcelain` 为空）；若有变更，SHALL 停止并提示用户处理。飞书链接解析、**任务查询（Meegle CLI 优先、飞书项目 MCP 备选）**、分支命名、远程存在性检查、推送与上游追踪等既有步骤 SHALL 在基线门禁满足后继续执行，且与基线要求**不冲突**。

#### Scenario: 工作区有未提交变更

- **WHEN** `git status --porcelain` 非空
- **THEN** SHALL 停止并提示用户提交、stash 或丢弃变更后再执行
