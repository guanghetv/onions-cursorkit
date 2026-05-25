# test-fe-specflow-yapi

## Why

飞书 PRD [这是一个测试Yapi的需求](https://guanghe.feishu.cn/wiki/HG2dwDqnuim3wGkosbWcSoSjn7g) 用于验证 **fe-specflow** 在 **阶段 1（/fe-sdd）** 能否完成：飞书拉取 → 正文提取 YApi → `get_interface_detail` → brainstorming API 契约 → OpenSpec 落盘。

本变更与 **`integrate-yapi-mcp`** 分工：

| 变更 | 目的 |
|------|------|
| `integrate-yapi-mcp` | 插件能力实现（`pull-yapi`、`dev-workflow` 等） |
| `test-fe-specflow-yapi` | 对上述能力的 **端到端流程验收记录**（可复现检查项 + `/fe-sdd` 回归） |

## What Changes

| 产物 | 说明 |
|------|------|
| `openspec/changes/test-fe-specflow-yapi/proposal.md` | 本文件：验证范围、夹具契约、References |
| `openspec/changes/test-fe-specflow-yapi/specs/fe-specflow-yapi-stage1-e2e/spec.md` | 阶段 1 链路的 WHEN/THEN Scenario |
| `openspec/changes/test-fe-specflow-yapi/tasks.md` | 手工勾选检查项 + 同飞书链接 `/fe-sdd` 回归步骤 |

**不在本变更范围**：业务前端代码、T1 后 `backend-yapi-*.md` 落盘（属事件 A / `integrate-yapi-mcp`）。

## API 契约（前端期望）

本变更为 **流程验证**，不实现业务页面。下列为 **YApi 测试夹具**（`contract_source: yapi-mcp`，2026-05-20 会话已对齐）。

### QueryUserAllowOrderIds

- **YApi**: https://yapi-test.yc345.tv/project/2784/interface/api/137397（飞书正文 → interfaceID `137397`）
- **变更类型**: 不变（仅验证 fe-specflow 读取与落盘，不要求改接口）
- **Method / Path**: `GET` `/invoice/admin/user/orderIds`
- **Query**: `userId`（optional）
- **Response**: `{ orderIds: string[] }`
- **说明**: 飞书 PRD 中的「新增地址请求逻辑」视为测试笔误；契约以 YApi MCP 为准。

## Capabilities

### New Capabilities

- `fe-specflow-yapi-stage1-e2e`: 阶段 1 飞书 + YApi 只读链路的可验收 Scenario（含 MCP 失败显式提示）

### Modified Capabilities

- （无）

## Impact

- **后端**: 无代码变更
- **前端（业务仓）**: 无实现；仅 cursorkit 内 OpenSpec 文档
- **依赖**: `user-feishu-mcp`、`user-yapi-common-mcp`（`YAPI_BASE_URL`、`YAPI_GLOBAL_TOKEN`）

## References

- 需求文档: https://guanghe.feishu.cn/wiki/HG2dwDqnuim3wGkosbWcSoSjn7g
- YApi 接口: https://yapi-test.yc345.tv/project/2784/interface/api/137397

## Decisions

| 决策 | 选择 | 说明 |
|------|------|------|
| 验证范围 | 仅阶段 1 | 不测 T1 后 `backend-yapi-*.md` |
| change-id | `test-fe-specflow-yapi` | 与 `integrate-yapi-mcp` 独立 |
| 成功标准 | 落盘 + tasks + `/fe-sdd` 回归 | 见 `tasks.md` §4 |
| PRD「地址」vs YApi | 以 YApi 为准 | 流程测试夹具 |
| 灰区讨论 | 跳过 | 无 UI/交互灰区 |
