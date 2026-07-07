# yapi-mcp-integration

fe-specflow 通过 YApi MCP 在设计期只读对齐接口字段，在 T1 后将接口详情落盘为 `backend-yapi-<slug>.md`，并与 proposal 中的 API 契约及 GitLab 叙事 spec 按约定置信度协同。

## ADDED Requirements

### Requirement: 阶段 1 YApi 只读采集

在 **阶段 1（设计探索）**，当用户提供 YApi 接口链接或 `interfaceID` 时，Agent MUST 使用 **user-yapi-common-mcp** 的 `get_interface_detail` 拉取接口详情，并将结果用于 brainstorming 与 **前端视角 API 契约** 草案。

Agent MUST NOT 在阶段 1 将 YApi 内容写入 `openspec/changes/`（变更目录尚未创建或尚未经 `design-to-opsx` 落盘）。

Agent MUST NOT 在 brainstorming 结束前因功能描述而**主动**调用 `search_interface`，除非用户显式要求按关键词搜索接口。

#### Scenario: 用户提供 YApi 链接时只读拉取

- **WHEN** 用户处于 fe-specflow 阶段 1
- **AND** 用户提供有效的 YApi 接口链接或 `interfaceID`
- **AND** `YAPI_BASE_URL` 与 `YAPI_GLOBAL_TOKEN`（或等效 MCP 参数）可用
- **THEN** Agent 调用 `get_interface_detail` 获取接口详情
- **AND** 将 path、method、请求/响应字段整理为契约摘要供 brainstorming 使用
- **AND** 不创建或修改 `openspec/changes/**` 下的文件

#### Scenario: YApi MCP 不可用时的降级

- **WHEN** 用户提供 YApi 链接或 `interfaceID`
- **AND** MCP 未启用、鉴权失败或接口不存在
- **THEN** Agent 向用户给出**明确原因**（未配置环境变量、token 无效、接口 ID 错误等）
- **AND** 建议用户粘贴 YApi 导出内容或截图后继续 brainstorming
- **AND** 不得静默跳过 YApi 来源

#### Scenario: 未提供链接时不主动搜索

- **WHEN** 用户处于阶段 1且仅描述业务功能、未提供 YApi 链接或 `interfaceID`
- **AND** 未从飞书或其它已采集来源中提取到 YApi 链接
- **THEN** Agent 不调用 `search_interface` 作为默认步骤
- **AND** API 契约可继续由 PRD 与其它来源推断，并在 proposal 中标注非 YApi 来源

#### Scenario: 飞书正文含 YApi 链接且涉及接口改动

- **WHEN** 用户提供了飞书文档链接且 feishu-mcp 拉取成功
- **AND** 本次需求**涉及接口改动**（新增、修改或废弃 API/字段等）
- **AND** 飞书正文中存在至少一条 YApi 链接或可识别的 `interfaceID`
- **THEN** Agent 从正文提取全部 YApi 链接/ID
- **AND** 对每条调用 `get_interface_detail`（pull-yapi 阶段 1 只读）
- **AND** 整理**目标态** API 契约及相对 YApi **现状**的变更说明
- **AND** 在合并笔记与 `proposal.md` References 中标注 `飞书 → YApi` 出处

#### Scenario: 涉及接口改动但飞书无 YApi 链接

- **WHEN** 需求涉及接口改动
- **AND** 飞书正文拉取成功但**无** YApi 链接/ID
- **THEN** Agent 在 brainstorming 中说明缺口并请求补链或 interfaceID
- **AND** proposal 标注 `contract_source: inferred` 直至 YApi 对齐完成
- **AND** Agent MUST NOT 静默假定已与 YApi 一致

#### Scenario: 不涉及接口改动时飞书 YApi 可选

- **WHEN** 需求**不涉及**接口改动（如纯 UI/文案）
- **THEN** Agent MAY 跳过对飞书内 YApi 链接的批量 `get_interface_detail`
- **AND** 不得因飞书含链接而强制走完整 pull-yapi 设计链路

### Requirement: pull-yapi 技能与落盘命名

fe-specflow MUST 提供 **`pull-yapi`** 技能，在 T1 完成后的**事件 A（后端契约到达）** 场景下，将 YApi 接口详情写入当前变更目录。

每个 YApi 接口 MUST 对应独立文件：`openspec/changes/<change-id>/backend-yapi-<slug>.md`，其中 `<slug>` 为可读的短标识（如接口 path 末段或业务名 kebab-case）。

文件头部 MUST 包含与 pull-spec 对齐的 metadata 注释（`source`、`interface_id`、`interface_url`、`pulled_at` 及外部副本警告）。

正文 MUST 使用固定 Markdown 结构（Method、Path、Headers、Query、Body、Response、错误码/业务码等），不得仅裸贴未整理的 JSON。

#### Scenario: T1 后单接口落盘

- **WHEN** 用户触发「YApi 接口到了」或等价语义并提供链接或 `interfaceID`
- **AND** 当前仓库存在且仅选定一个含 `proposal.md` 的变更目录（或多目录时用户已指定 change-id）
- **THEN** Agent 遵循 `pull-yapi` 调用 MCP 并写入 `backend-yapi-<slug>.md`
- **AND** 写入路径与 `proposal.md` 同级
- **AND** 写入后列出目录确认文件存在

#### Scenario: 多接口各自落盘

- **WHEN** 用户提供多个 YApi 链接或 `interfaceID`
- **THEN** Agent 为每个接口分别写入独立的 `backend-yapi-<slug>.md`
- **AND** 各 slug 在同一 change-id 下不得冲突

#### Scenario: 无变更目录时拒绝写入

- **WHEN** 用户请求 pull-yapi
- **AND** 当前仓库不存在任何 `openspec/changes/*/proposal.md`
- **THEN** Agent 拒绝写入
- **AND** 提示须先完成阶段 1 与 `design-to-opsx` 创建变更

### Requirement: 与 proposal API 契约的差异分析

`pull-yapi` 落盘完成后，Agent MUST 读取 `proposal.md` 中的 **API 契约（前端期望）** 段落，与 `backend-yapi-*.md` 对比，输出：

- **一致**：字段与类型吻合
- **差异**：字段名、类型、必填、错误码等不一致
- **增量**：YApi 有而 proposal 未覆盖的内容

若存在差异，Agent SHOULD 建议更新 mock 数据或前端 spec Scenario。

#### Scenario: 联调前发现契约差异

- **WHEN** `backend-yapi-*.md` 已落盘
- **AND** `proposal.md` 含 API 契约段落
- **THEN** Agent 输出 structured diff（一致 / 差异 / 增量）
- **AND** 字段级不一致以 YApi 落盘内容为纠偏依据（决策 3a）

### Requirement: 多源置信度与冲突标注

当 YApi 落盘内容、GitLab `backend-*.md` 与 `qa-*.md` 对同一接口描述不一致时：

- **字段名、类型、请求/响应 schema**：以 **`backend-yapi-*.md`（YApi）** 为准进行联调与 mock 修正。
- **业务场景、流程叙述、验收口径**：以 **`qa-*.md` 为 E2E 最高**；GitLab `backend-*.md` 补场景；与 YApi 字段冲突时 MUST 在 diff 或 `e2e-report.md` 中**显式标注**。

#### Scenario: YApi 与 qa spec 字段冲突

- **WHEN** `qa-*.md` 某 Scenario 期望的响应字段与 `backend-yapi-*.md` 不一致
- **THEN** E2E 验收仍以 qa 为口径
- **AND** 报告中须包含「与 YApi 字段冲突」醒目说明
- **AND** 不得静默采用 YApi 覆盖 qa 验收结论

### Requirement: 编排文档与门禁同步

`dev-workflow`、`fe-sdd` 命令、`dev-workflow.mdc` Rule 与 `README.md` MUST 描述 YApi 作为可选/可组合需求来源及事件 A 的 `pull-yapi` 入口。

`design-to-opsx` 的 `References` 模板 MUST 支持记录 YApi 接口链接列表。

`pull-spec` 与 `e2e-verify` MUST 交叉引用 YApi 落盘路径与置信度规则，避免 Agent 仅识别 GitLab backend spec。

#### Scenario: fe-sdd 阶段 1 声明 YApi 来源

- **WHEN** 用户通过 `/fe-sdd` 启动设计探索
- **THEN** 阶段 1 多源采集说明中包含 YApi MCP（用户给链接/ID 时只读）
- **AND** 在用户放行前仍禁止写入 `openspec/changes/**`（门禁不变）

### Requirement: search_interface 的受限使用

仅当用户**显式要求**按接口名/路径关键词在 YApi 中搜索且 MCP 返回候选列表时，Agent MAY 调用 `search_interface`。

用户 MUST 从候选中确认 `interfaceID` 后，Agent 方可对该 ID 调用 `get_interface_detail` 并继续只读或落盘流程。

#### Scenario: 用户要求搜索接口

- **WHEN** 用户说「在 YApi 里搜一下 xxx 接口」
- **THEN** Agent 可调用 `search_interface`
- **AND** 展示候选（最多 5 条）并请用户确认 interfaceID
- **AND** 未经确认不得将某一候选当作已定接口写入落盘文件

### Requirement: pull-yapi 为文档层且不改业务代码

`pull-yapi` MUST 仅负责 MCP 拉取、落盘 `backend-yapi-*.md` 与 proposal diff。

Agent MUST NOT 在仅执行 `pull-yapi` 时修改 `.vue/.ts/.tsx/.jsx/.js` 等业务实现文件。

#### Scenario: 用户只要落盘契约

- **WHEN** 用户明确「只拉 YApi」「只落盘」「不要改代码」
- **THEN** Agent 仅遵循 `pull-yapi`
- **AND** 不调用 `re-check` 修改实现

### Requirement: re-check 技能与实现层对齐

fe-specflow MUST 提供 **`re-check`** 技能，作为 YApi 到达后**默认**联调对齐路径（无单独 slash command）。

`re-check` MUST REQUIRED 调用 `pull-yapi` 完成契约落盘与 proposal diff，然后在限定 scope 内更新 mock/实现与相关测试。

插件 **Commands** MUST 仍仅包含 **`/fe-sdd`**（`commands/fe-sdd.md`）。

#### Scenario: 事件 A 默认走 re-check

- **WHEN** 用户说「YApi 接口到了」「re-check」「对齐 YApi」或粘贴 YApi/飞书链接
- **AND** 存在可定位的 `openspec/changes/<change-id>/proposal.md`
- **AND** 用户未要求仅落盘
- **THEN** Agent 遵循 `re-check` 全流程
- **AND** 先通过 `pull-yapi` 写入或更新 `backend-yapi-*.md`

#### Scenario: 无感触发粘贴链接

- **WHEN** 用户在对话中粘贴飞书或 YApi 链接
- **AND** 仓库中仅一个含 `proposal.md` 的变更目录（或用户已指定 change-id）
- **AND** 用户未声明仅落盘
- **THEN** Agent SHOULD 进入 `re-check` 而非仅 `pull-yapi`

#### Scenario: scope 皆空时只报告

- **WHEN** `re-check` 执行中
- **AND** `proposal.md` 无可用 `modules` 且相对 base 分支无相关 git diff
- **THEN** Agent 输出对齐表
- **AND** MUST NOT 自动修改业务代码

### Requirement: 破坏性变更与批量确认

`re-check` 在下列情况 MUST 先向用户展示对齐表并获确认后再改代码：

- 响应字段删除或重命名
- 必填收紧且无默认
- 字段类型变更
- HTTP method 或 path 变更
- 单次对齐涉及 **≥3** 个接口或预计修改 **≥5** 个文件（批量门禁）

新增可选字段、新增响应字段等无破坏性差异 MAY 自动对齐。

#### Scenario: 批量对齐前确认

- **WHEN** `re-check` 将修改 ≥3 个接口或 ≥5 个文件
- **THEN** Agent 先输出完整对齐表（破坏性标 🔴）
- **AND** 用户确认后再修改代码

### Requirement: mock 标记推荐不强制

T1 阶段对 mock/占位 API，Agent SHOULD 添加 `@fe-specflow: mock-source`、`yapi-placeholder`、`mock-fields` 注释（见 `re-check` 技能）。

Agent MUST NOT 因缺少标记而阻断 T1 完成。

`re-check` MUST 在无标记时按 path grep、proposal 契约、mock 特征降级匹配；多候选时 MUST 请用户选择。

#### Scenario: 无标记仍可对齐

- **WHEN** 代码无 `@fe-specflow` 标记
- **AND** scope 内存在与 YApi path 匹配的 API 封装
- **THEN** `re-check` 仍可生成对齐表并建议修改
- **AND** 匹配不确定时列入未绑定项请用户确认

### Requirement: 编排文档同步 re-check

`dev-workflow`、`dev-workflow.mdc`、`README.md` MUST 区分 **pull-yapi**（文档）与 **re-check**（实现），并说明 Commands 仅 `/fe-sdd`。

事件 A 默认触发语 MUST 路由到 `re-check`，除非用户明确要求仅落盘。
