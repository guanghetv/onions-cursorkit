---
name: pull-yapi
description: >-
  Document layer only—pull YApi schema via user-yapi-common-mcp, write
  backend-yapi-<slug>.md, diff proposal API contract. Does NOT modify business code.
  Stage 1 read-only; after T1 writes under openspec/changes/. For mock-to-real code
  alignment use re-check skill. Triggered by "只拉YApi/只落盘/拉契约", YApi URL, interfaceID,
  or called by re-check. Not a slash command (only /fe-sdd exists).
---

# 拉取 YApi 接口契约（文档层）

通过 **user-yapi-common-mcp** 获取 YApi 上的**结构化接口详情**（path、method、请求/响应字段等），**落盘并对照 proposal**。**不修改**业务代码（`.vue/.ts/.js` 等）；实现层对齐走 **`re-check`**。

| 技能 | 介质 | 改代码？ | 典型内容 |
|------|------|--------|----------|
| **pull-yapi**（本技能） | YApi MCP | **否** | `backend-yapi-*.md`、proposal diff |
| **re-check** | YApi + 仓库扫描 | **是**（scope 内） | mock → 真接口、测试、proposal 契约更新 |
| **pull-spec** | GitLab / workspace / 粘贴 | 否（落盘 spec 文件） | 叙事型 backend/qa spec |

本技能有**两种使用时机**：

| 时机 | 场景 | 行为差异 |
|------|------|----------|
| **阶段 1（设计探索）** | 用户提供 **YApi 链接或 interfaceID** | **仅读取**并整理为契约摘要，供 brainstorming 与 API 契约草案；**不写入** `openspec/changes/`；链接记入后续 `proposal.md` 的 `References` |
| **T1 后（事件 A 扩展）** | 联调前需将 YApi 契约落盘对照 | **写入** `openspec/changes/<change-id>/backend-yapi-<slug>.md`，并与 `proposal.md` 中 API 契约 diff |

> **链接来源**：用户直给、**飞书正文提取**（`dev-workflow` 在「涉及接口改动」时强制）、或 `proposal.md` 的 `References`。
>
> **2a 纪律（更新）**：无链接/ID 时**不**默认 `search_interface`；**飞书场景例外**：已拉飞书且判定涉及接口改动 → **必须**从正文提取 YApi 链接并 `get_interface_detail`，不依赖用户重复粘贴。

## MCP 工具与环境

| 工具 | 用途 |
|------|------|
| `get_interface_detail` | **主路径**：参数 `interfaceURL` 和/或 `interfaceID`（二选一即可） |
| `search_interface` | **受限**：仅当用户**显式要求**按关键词在 YApi 中搜索时使用 |

环境变量（调用时可覆盖）：

- `YAPI_BASE_URL` — YApi 服务地址
- `YAPI_GLOBAL_TOKEN` — 请求头 `x-yapi-global-token`

调用前可用只读检查：

```bash
test -n "${YAPI_BASE_URL:-}" && test -n "${YAPI_GLOBAL_TOKEN:-}"
```

## 输入

用户提供以下任一形式（**可多接口**，逐个处理）：

1. **YApi 接口链接**（`interfaceURL`）
2. **interfaceID**（正整数）
3. **显式搜索**（罕见）：用户要求「在 YApi 里搜 xxx」→ `search_interface` → 用户确认候选 `interfaceID` → `get_interface_detail`

**不支持的默认行为**：用户只说「后端 spec 到了」但**未给 YApi 链接/ID** 时，本技能**不**自动发现接口——应走 **`pull-spec`**（GitLab / workspace-native）或请用户补充 YApi 信息。

## 阶段 1：只读拉取（由 dev-workflow 步骤 1b 调用）

**触发**（满足任一）：

| 来源 | 条件 |
|------|------|
| 用户直给 | 提供 `interfaceURL` 或 `interfaceID` |
| **飞书正文** | `dev-workflow` 已拉飞书且本次**涉及接口改动** → 从正文提取的全部 YApi 链接/ID |
| 恢复上下文 | `proposal.md` 的 `References` 中已有 YApi 列表且需重新对齐字段 |

**设计 / 更改（阶段 1 产出，非 YApi 平台写库）**：

- **更改**：`get_interface_detail` 得**现状** → 对照 PRD 整理 **delta** → 输出**目标态**契约摘要（供 proposal / mock）。
- **新增**：无对应 YApi 条目时输出**拟议**契约，标注 `yapi_status: pending-create`；有链接则先拉现状再判断是改还是新建。

流程：

1. 对每个链接/ID 调用 **`get_interface_detail`**（MCP server: `user-yapi-common-mcp`）。
2. 将返回内容整理为**契约摘要**（见下方「正文 Markdown 结构」），供 brainstorming 使用；若有 delta，单独列出「相对 YApi 现状的变更」。
3. **禁止**创建或修改 `openspec/changes/**`。
4. 在需求合并笔记中标注出处：**YApi / interfaceID / URL**；来自飞书时写 **`飞书 <章节> → YApi`**。

### 失败处理（必须明确提示，禁止静默跳过）

| 情况 | 处理 |
|------|------|
| MCP 未安装 / 未启用 | 说明无法调用 YApi MCP，请启用 `user-yapi-common-mcp`，或粘贴 YApi 导出/截图 |
| `YAPI_BASE_URL` / `YAPI_GLOBAL_TOKEN` 未配置 | 说明需配置环境变量或在 MCP 调用中传入 `baseURL` / `globalToken` |
| 鉴权失败（401/403） | 说明 token 无效或权限不足，请更新 token |
| 接口不存在 / ID 错误 | 说明 interfaceID 或链接无效，请用户核对 |
| 用户粘贴 YApi 导出 JSON/文本 | 作为降级输入，同样整理为契约摘要，标注 `source: user-paste` |

## T1 后：定位变更目录

写入前**必须**先确定目标变更目录（与 pull-spec 相同）：

```bash
find openspec/changes -maxdepth 2 -name proposal.md 2>/dev/null
```

| 场景 | 处理方式 |
|------|---------|
| 仅 1 个变更目录 | 自动选定 |
| 多个变更目录 | 列出所有 change-id，请用户选择 |
| 用户触发语中包含 change-id | 直接使用 |
| 无变更目录 | **拒绝执行**，提示先完成阶段 1 与 `design-to-opsx` |

定位后锁定路径：`openspec/changes/<change-id>/`。

## T1 后：拉取与落盘

### 步骤 1：调用 MCP

对每个接口调用 `get_interface_detail`（`interfaceURL` / `interfaceID`）。

若用户显式要求搜索：

1. 调用 `search_interface`（`rawQuery` / `tokens`）
2. 展示候选（最多 5 条）
3. **用户确认** `interfaceID` 后，再调用 `get_interface_detail`
4. **禁止**未经确认将某一候选写入落盘文件

### 步骤 2：生成 slug 与文件名

- 文件名：`backend-yapi-<slug>.md`（**1a**：每接口一个文件）
- `<slug>`：从 path 末段或接口 title 生成 kebab-case（如 `/api/v1/refund/list` → `refund-list`）；多接口时 slug **不得冲突**，冲突时加 method 前缀或 interfaceID 后缀

### 步骤 3：写入文件

**文件头部**（自动注入）：

```markdown
<!-- pull-yapi metadata -->
<!-- source: yapi-mcp -->
<!-- interface_id: <id> -->
<!-- interface_url: <url 或 N/A> -->
<!-- pulled_at: <YYYY-MM-DD HH:mm> -->
<!-- WARNING: 此文件为 YApi 接口副本，字段以 YApi 线上为准 -->
```

**正文 Markdown 结构**（将 MCP 返回转为以下章节，**不得**仅裸贴未整理 JSON）：

```markdown
# <接口名称或 path>

## 基本信息
- Method: ...
- Path: ...
- 备注: ...

## Headers
...

## Query
...

## Request Body
...

## Response
### 成功响应
...
### 错误码 / 业务码
...

## 示例（如有）
...
```

**路径约束**：

- **必须**写入 `openspec/changes/<change-id>/`，与 `proposal.md` 同级
- 写入前验证目录存在 `proposal.md`
- 写入后 `ls openspec/changes/<change-id>/` 确认

### 步骤 4：差异分析

拉取完成后自动执行（逻辑与 **pull-spec 步骤 5** 一致）：

1. 读取 `proposal.md` 中 **## API 契约（前端期望）** 段落
2. 读取本次写入的 `backend-yapi-*.md`
3. 输出：
   - **一致**：字段与类型吻合
   - **差异**：字段名、类型、必填、错误码等不同
   - **增量**：YApi 有而 proposal 未覆盖的内容
4. 存在差异时：建议更新 mock 数据或前端 spec Scenario；**字段级纠偏以 YApi 为准**（决策 3a）

### 多源置信度（3a）

| 内容类型 | 权威来源 |
|----------|----------|
| 请求/响应 **字段与类型** | `backend-yapi-*.md`（YApi） |
| 业务流程、场景叙述 | GitLab `backend-*.md`（pull-spec） |
| E2E **验收口径** | `qa-*.md`（最高）；与 YApi 字段冲突须在 diff / `e2e-report.md` **显式标注** |

## 触发语示例

- 「**只拉** YApi / **只落盘** / 拉一下契约 `<链接>`」
- 「从 YApi 拉一下 interface `<id>`」（用户明确不要改代码时）
- 「后端接口在 YApi」+ 链接/ID（若要对齐 mock 实现，应走 **re-check**）

**默认联调对齐**（改代码）由 **re-check** 处理，触发语如「YApi 接口到了」「对齐 YApi」「re-check」——re-check 内部会 REQUIRED 调用本技能落盘。

## 归档注意

归档时须随变更目录保留所有 `backend-yapi-*.md` 文件（与 `backend-*.md`、`qa-*.md` 同级保留）。
