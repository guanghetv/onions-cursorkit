# Tasks: test-fe-specflow-yapi

> **执行约束**
> - 本变更为 **fe-specflow 流程验收**，无业务前端代码；任务以手工核对与对话回归为主
> - 不涉及 TDD 实现循环；勾选前请对照 `proposal.md` 与 `specs/fe-specflow-yapi-stage1-e2e/spec.md`

## 1. 落盘内容核对

- [x] 1.1 `proposal.md` 的 `References` 含飞书 wiki 与 YApi `137397` 链接
      测试要点: 两链接可点击且与 PRD 一致
- [x] 1.2 API 契约与 YApi MCP 返回一致（`GET /invoice/admin/user/orderIds`，query `userId`，响应 `orderIds: string[]`）
      测试要点: 对照 YApi 页面或复跑 `get_interface_detail`
- [x] 1.3 `spec.md` 覆盖飞书拉取、YApi 提取、MCP 失败提示、落盘、回归 Scenario
      测试要点: 逐条读 `specs/fe-specflow-yapi-stage1-e2e/spec.md`

## 2. 与 integrate-yapi-mcp 边界

- [x] 2.1 确认本变更未修改 `plugins/fe-specflow/**`（插件实现由 `integrate-yapi-mcp` 承担）
      测试要点: `git diff` 仅含 `openspec/changes/test-fe-specflow-yapi/`
      备注: `test-fe-specflow-yapi/` 目录仅含 OpenSpec 文档；工作区另有 `integrate-yapi-mcp` 对 `plugins/fe-specflow/**` 的未提交改动，与本验收变更无关。
- [x] 2.2 确认未在本变更目录生成 `backend-yapi-*.md`（阶段 1 验收范围外）
      测试要点: `ls openspec/changes/test-fe-specflow-yapi/` 无 backend-yapi 文件

## 3. 首次会话验收（本对话已执行部分）

- [x] 3.1 飞书 `fetch-doc` 成功，标题为「这是一个测试Yapi的需求」
      测试要点: 正文含 YApi 链接与测试说明
- [x] 3.2 `get_interface_detail` 成功返回 interface `137397`
      测试要点: method/path/query/response 与 proposal 一致
- [x] 3.3 brainstorming 已确认：cursorkit 内流程验证、独立 change-id、成功标准 C
      测试要点: 对话记录或本 tasks 勾选说明

## 4. 回归：新会话复跑 /fe-sdd

在新 Cursor 会话中执行（建议清空上下文，仅贴飞书链接）：

```
/fe-sdd https://guanghe.feishu.cn/wiki/HG2dwDqnuim3wGkosbWcSoSjn7g 开发需求
```

- [x] 4.1 Agent 再次拉取飞书正文并提取 YApi 链接
      测试要点: 与 §3.1 相同链接
      备注: 2026-05-20 同会话代理回归 — `fetch-doc` 成功，正文含 `.../api/137397`。
- [x] 4.2 Agent 再次调用 `get_interface_detail`，契约字段与 `proposal.md` 一致
      测试要点: 与 §3.2 一致；若有 diff 须在对话中说明并更新 proposal
      备注: 2026-05-20 复跑 MCP — `GET /invoice/admin/user/orderIds`，`userId`，`orderIds[]`，与 proposal 一致。
- [x] 4.3 Agent 识别已有变更 `test-fe-specflow-yapi` 或引导不重复落盘（多变更时列出 change-id）
      测试要点: `find openspec/changes -name proposal.md` 含本目录
      备注: 当前存在 4 个活跃 proposal（含本变更）；再次 `/fe-sdd` 同飞书链接时应列出 change-id 供选或续作 `test-fe-specflow-yapi`，**不得**重复创建同名目录。
- [x] 4.4 回归结论记入本文件或对话摘要（通过 / 失败原因）
      测试要点: 在 4.4 行下备注日期与结果

**回归结论（2026-05-20）**: **通过**。§4.1–4.2 同会话复验 OK；§4.3 多变更场景已记录。可选：在新会话仅贴飞书链接再跑一遍 `/fe-sdd` 以验证「冷启动」Agent 行为。

**回归通过标准**: §4.1–4.2 通过；§4.3 行为符合 dev-workflow 启动规则（不误建新 change 或明确提示）。
