# fe-specflow-yapi-stage1-e2e

验证 fe-specflow **阶段 1** 在真实飞书 PRD + YApi 链接下，能完成多源采集、YApi MCP 只读拉取，并将契约写入 `proposal.md`（经 `design-to-opsx`）。不包含 T1 后 `backend-yapi-*.md` 落盘。

## ADDED Requirements

### Requirement: 飞书 PRD 拉取与 YApi 链接提取

在 `/fe-sdd` 阶段 1，当用户提供飞书 wiki 链接时，Agent MUST 使用 feishu-mcp 拉取正文，并从正文中提取全部 YApi 链接或可识别的 `interfaceID`。

#### Scenario: 飞书链接拉取成功并提取 YApi

- **WHEN** 用户提供飞书文档 `https://guanghe.feishu.cn/wiki/HG2dwDqnuim3wGkosbWcSoSjn7g`
- **AND** `user-feishu-mcp` 的 `fetch-doc` 可用
- **THEN** Agent 获取文档标题与 Markdown 正文
- **AND** 从正文中识别 YApi 链接 `https://yapi-test.yc345.tv/project/2784/interface/api/137397`
- **AND** 在需求合并笔记中标注出处 `飞书 → YApi`

#### Scenario: 飞书 MCP 不可用

- **WHEN** 用户仅提供飞书链接
- **AND** feishu-mcp 未启用或鉴权失败
- **THEN** Agent 向用户说明无法读取飞书（安装/启用 MCP、token、权限等）
- **AND** 建议粘贴正文或本地文件后继续
- **AND** MUST NOT 静默跳过飞书来源

### Requirement: 涉及接口改动时 YApi MCP 只读对齐

当需求涉及接口对接且飞书正文含 YApi 链接时，Agent MUST 在阶段 1 对每条链接调用 `get_interface_detail`，并将结果用于 API 契约草案；阶段 1 MUST NOT 写入 `openspec/changes/`（落盘前）。

#### Scenario: 飞书含 YApi 且 MCP 成功

- **WHEN** 飞书拉取成功且正文含 YApi 链接
- **AND** `YAPI_BASE_URL` 与 `YAPI_GLOBAL_TOKEN`（或 MCP 参数）可用
- **THEN** Agent 调用 `get_interface_detail`（interfaceURL 或 interfaceID `137397`）
- **AND** 整理 path、method、query、response 供 brainstorming
- **AND** 在 `design-to-opsx` 前不创建 `openspec/changes/**` 文件

#### Scenario: YApi MCP 不可用

- **WHEN** 飞书正文含 YApi 链接
- **AND** MCP 未启用、环境变量缺失、鉴权失败或接口不存在
- **THEN** Agent 向用户给出明确原因与修复建议
- **AND** MUST NOT 静默假定契约已与 YApi 一致

### Requirement: design-to-opsx 落盘契约与引用

Brainstorming 与用户确认后，Agent MUST 通过 `design-to-opsx` 创建变更目录，并在 `proposal.md` 的 References 与 API 契约节记录飞书链接、YApi 链接及与 MCP 一致的字段摘要。

#### Scenario: 落盘 proposal 含 References 与夹具契约

- **WHEN** 用户确认设计方案并放行落盘（如「执行」「可以落盘」）
- **THEN** 存在 `openspec/changes/test-fe-specflow-yapi/proposal.md`
- **AND** `References` 含飞书 wiki 与 YApi 接口 URL
- **AND** API 契约描述 `GET /invoice/admin/user/orderIds` 及 `orderIds` 响应结构
- **AND** 标注 `contract_source: yapi-mcp` 或等价说明

### Requirement: 回归任务可复跑 /fe-sdd

变更目录 MUST 包含 `tasks.md`，其中列出可手工勾选的验证项，以及在新会话中对**同一飞书链接**复跑 `/fe-sdd` 的回归步骤说明。

#### Scenario: tasks 含回归步骤

- **WHEN** `test-fe-specflow-yapi` 变更已落盘
- **THEN** `tasks.md` 存在且包含「回归：同飞书链接再跑 /fe-sdd」类任务
- **AND** 回归预期与首次会话一致（再次拉取 YApi、契约字段一致）
