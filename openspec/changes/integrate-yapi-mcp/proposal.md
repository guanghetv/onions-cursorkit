# integrate-yapi-mcp

## Why

团队已接入 **YApi MCP**（`user-yapi-common-mcp`），可通过接口链接或 `interfaceID` 获取结构化接口详情，减少研发反复打开 YApi 核对字段。

当前 **fe-specflow** 在阶段 1 的 API 契约多依赖 PRD 与 brainstorming 推断；T1 常用 mock 占位，后端技术方案/YApi 链接往往**晚于**前端 T1。既有 **pull-yapi** 解决契约落盘与 proposal diff，但缺少将 **mock 实现** 与后续 YApi 字段**系统化对齐**的路径，联调仍易偏离真实接口。

## What Changes

在 **fe-specflow** 插件中融入 YApi MCP，与现有 **pull-spec** 并列，遵循已确认决策 **1a / 2a / 3a**。

### 新建

| 产物                                            | 说明                                                                                     |
| ----------------------------------------------- | ---------------------------------------------------------------------------------------- |
| `plugins/fe-specflow/skills/pull-yapi/SKILL.md` | **文档层**：YApi 落盘 + proposal diff，**不改业务代码**                                   |
| `plugins/fe-specflow/skills/re-check/SKILL.md`  | **实现层**：mock 与 YApi 对齐、scope 内改代码、破坏性变更确认、重跑 TDD                    |
| `openspec/changes/integrate-yapi-mcp/`          | 本变更的设计与规格（本目录）                                                             |

### 修改

| 文件                                                 | 说明                                                                                                  |
| ---------------------------------------------------- | ----------------------------------------------------------------------------------------------------- |
| `plugins/fe-specflow/skills/dev-workflow/SKILL.md`   | 阶段 1b YApi 只读；T1 推荐 mock 标记；事件 A 默认 **re-check**；无感触发；仅落盘走 pull-yapi          |
| `plugins/fe-specflow/rules/dev-workflow.mdc`         | 与 dev-workflow 同步 re-check / pull-yapi 分工                                                        |
| `plugins/fe-specflow/commands/fe-sdd.md`             | 阶段 1 多源采集补充 YApi MCP                                                                          |
| `plugins/fe-specflow/README.md`                      | 前置条件：`YAPI_BASE_URL`、`YAPI_GLOBAL_TOKEN`                                                        |
| `plugins/fe-specflow/skills/design-to-opsx/SKILL.md` | `References` 模板支持 YApi 链接列表                                                                   |
| `plugins/fe-specflow/skills/pull-spec/SKILL.md`      | 交叉引用：结构化接口契约可走 `pull-yapi`                                                              |
| `plugins/fe-specflow/skills/e2e-verify/SKILL.md`     | 静态对照时若有 `backend-yapi-*`，字段以 YApi 为准                                                     |

### 行为要点（决策固化）

1. **1a — 落盘命名**：每个 YApi 接口一个文件，`openspec/changes/<change-id>/backend-yapi-<slug>.md`。
2. **2a — 拉取时机**：仅当用户提供 **YApi 链接或 interfaceID** 时调用 `get_interface_detail`；不在 brainstorming 结束前主动 `search_interface`。
3. **3a — 置信度**：字段 / schema **以 YApi 为准**；业务场景与验收叙述以 GitLab `backend-*.md` / `qa-*.md` 为准；冲突须在 diff 或 `e2e-report.md` 中显式标注。

### 阶段划分

| 阶段               | YApi 行为                                                                                |
| ------------------ | ---------------------------------------------------------------------------------------- |
| 阶段 1（设计探索） | **只读**：MCP 结果进入 brainstorming 与 API 契约草案，**不写入** `openspec/changes/`     |
| T1 后（事件 A）    | 默认 **re-check**（内含 pull-yapi 落盘 + scope 内改代码）；仅文档 → **pull-yapi** only     |
| 无感触发           | 对话贴飞书/YApi 且唯一定位 change → 默认 re-check；明确「只落盘」→ pull-yapi only          |

## API 契约（前端期望）

本变更为 **插件工作流能力**，不引入业务 HTTP 接口。

工作流契约约定：

| 能力                 | 输入                                   | 输出                                               |
| -------------------- | -------------------------------------- | -------------------------------------------------- |
| 阶段 1 只读          | `interfaceURL` 或 `interfaceID`        | 规范化接口摘要（供 brainstorming / proposal 草案） |
| `pull-yapi`（T1 后） | 同上 + 变更目录                        | `backend-yapi-<slug>.md` + diff（不改业务代码）    |
| `re-check`           | 飞书/YApi 链接或 References + change   | 对齐表 + scope 内代码/测试更新 + TDD 重跑          |

MCP 工具：`get_interface_detail`（主路径）、`search_interface`（仅当用户显式要求按关键词搜索且确认候选 ID 后使用，非默认路径）。

环境变量：`YAPI_BASE_URL`、`YAPI_GLOBAL_TOKEN`（或调用参数 `baseURL` / `globalToken`）。

## 能力建设

### 新能力添加

- `yapi-mcp-integration`: fe-specflow 经 **pull-yapi**（文档）与 **re-check**（实现对齐）接入 YApi MCP；Commands 仍仅 `/fe-sdd`

### Modified Capabilities

- （无既有 capability 语义变更；实现后归档时可将 `yapi-mcp-integration` 合并入仓库级 spec，若团队约定单独维护 workflow spec 则另议）

## 影响

- **后端**: 无代码变更；鼓励继续在 YApi 维护字段级契约
- **前端**: fe-specflow 插件技能与文档更新；业务仓库在联调阶段可多一类 `backend-yapi-*.md` 产物
- **依赖**: Cursor 启用 `user-yapi-common-mcp`；配置 `YAPI_BASE_URL`、`YAPI_GLOBAL_TOKEN`

## 引用

- 对话设计结论：fe-specflow 接入 YApi MCP（决策 1a / 2a / 3a）
- YApi MCP 工具：`get_interface_detail`、`search_interface`（`user-yapi-common-mcp`）
- 现有编排：`plugins/fe-specflow/skills/dev-workflow/SKILL.md`、`pull-spec/SKILL.md`

## Decisions

| 决策            | 选择                 | 说明                                                   |
| --------------- | -------------------- | ------------------------------------------------------ |
| 多接口落盘      | **1a**               | 每接口独立 `backend-yapi-<slug>.md`                    |
| 阶段 1 拉取策略 | **2a+飞书**          | 直给链接/ID 必拉；**涉及接口改动**时从飞书正文强制提取 YApi 并拉取；无链不默认 search |
| 飞书内嵌 YApi   | **强制联动**         | 接口改动 + 飞书有链 → 必须 MCP 对齐；设计/更改=目标态契约+delta，YApi 写库由研发或未来写 MCP |
| 冲突置信度      | **3a**               | 字段以 YApi 为准；场景/验收以 GitLab backend / qa 为准 |
| 技能形态        | **pull-yapi + re-check** | 文档层与实现层分离；re-check REQUIRED 调用 pull-yapi   |
| 用户入口        | **仅 `/fe-sdd` Command** | re-check 靠自然语言 + dev-workflow 路由，无新 Command  |
| mock 标记       | **推荐不强制（B）**      | `@fe-specflow: yapi-placeholder` 等便于 re-check 扫描  |
| 破坏性确认      | **字段级 + 批量 N=5**    | ≥3 接口或 ≥5 文件先出表再一次性确认                    |
| scope           | **modules → git diff**   | 皆空则只报告不改代码                                   |
| 灰区讨论        | **跳过**                 | 纯插件/流程变更                                        |
