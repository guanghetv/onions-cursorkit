---
name: pull-yapi
description: 从 YApi 拉取接口契约，供 Onion SDD 在设计期只读参考或在 T1 后落盘为 backend-yapi-*.md 并做差异分析。
---

# Pull YApi

本技能用于前端需求中涉及后端 HTTP 接口契约的场景。它通过 `user-yapi-common-mcp` 读取 YApi 接口详情，并按 Onion SDD 规则把契约用于设计或落盘到当前 OpenSpec change。

## 触发

- 用户提供 YApi URL 或 interfaceID。
- 飞书卡片/需求文档中包含 YApi 链接，且本需求涉及接口新增、修改或废弃。
- 用户说“拉一下 YApi”“只拉 YApi”“接口文档到了”“只落盘接口契约”。
- `re-check` 需要先拉取最新 YApi 契约。

不要默认全文搜索 YApi。只有用户明确要求“帮我搜接口”或需求文档只给接口名称且没有链接/ID 时，才可使用 `search_interface`，并在候选列表中让用户确认后再读取详情。

## 前置

- 可用 MCP：`user-yapi-common-mcp`。
- 环境变量：`YAPI_BASE_URL`、`YAPI_GLOBAL_TOKEN`。
- 能定位当前 `openspec/changes/<change-id>/`；设计期只读参考可以不要求已存在 change，但落盘必须有目标 change。

如果 MCP 或环境变量不可用：

- 设计期：让用户粘贴接口文档正文，主会话自行整理契约摘要。
- T1 后：把用户粘贴内容按本技能模板写入 `backend-yapi-*.md`，并标注 `source: user-paste-yapi`。
- 不能静默跳过；最终回复必须说明缺失能力和降级方式。

## 两种模式

### 设计期只读

适用于 discover/design 阶段。目标是辅助澄清 API/数据/错误码，不写入 OpenSpec 文件：

1. 从用户输入、飞书文档或卡片正文中提取 YApi URL / interfaceID。
2. 拉取接口详情，整理契约摘要。
3. 把字段、类型、必填、错误码和示例用于 `proposal.md` / `specs/**/spec.md` 的设计讨论。
4. 如需求涉及接口变化但没有 YApi 链接，向用户确认；在确认前可把 `contract_source: inferred` 记录为临时假设。

### T1 后落盘

适用于实现后或后端接口已确认时。目标是把 YApi 契约写入当前 change 并与 OpenSpec 差异分析：

1. 定位 `openspec/changes/<change-id>/`。
2. 拉取接口详情。
3. 写入 `backend-yapi-<slug>.md`。
4. 对比 `proposal.md`、`specs/**/spec.md` 和当前实现/测试中相关接口契约。
5. 输出一致、差异、增量、冲突；冲突未裁决前不要进入归档。

## 文件命名

写入路径固定为：

```text
openspec/changes/<change-id>/backend-yapi-<slug>.md
```

`<slug>` 优先使用接口路径和方法生成，例如 `post-order-list`；无法生成时使用 `interface-<id>`。

## 文件头

```markdown
<!-- pull-yapi metadata -->
<!-- source: yapi-mcp -->
<!-- interface_id: <id> -->
<!-- interface_url: <url 或 N/A> -->
<!-- pulled_at: <YYYY-MM-DD HH:mm> -->
<!-- WARNING: 此文件为 YApi 接口副本，字段以 YApi 线上为准 -->
```

降级到用户粘贴时：

```markdown
<!-- pull-yapi metadata -->
<!-- source: user-paste-yapi -->
<!-- interface_id: <id 或 N/A> -->
<!-- interface_url: <url 或 N/A> -->
<!-- pulled_at: <YYYY-MM-DD HH:mm> -->
<!-- WARNING: 此文件为 YApi 接口副本，字段以用户提供内容为准 -->
```

## Markdown 结构

````markdown
# YApi Contract: <接口名称>

## 基本信息

- Method: <GET/POST/...>
- Path: <path>
- Status: <status>
- Owner: <owner 或 N/A>
- Updated: <YApi 更新时间或 N/A>

## Headers

| Name | Required | Type | Description |
|------|----------|------|-------------|

## Query

| Name | Required | Type | Description |
|------|----------|------|-------------|

## Request Body

| Path | Required | Type | Description |
|------|----------|------|-------------|

## Response

| Path | Required | Type | Description |
|------|----------|------|-------------|

## 示例

```json
{}
```

## 差异分析

| 类型 | 位置 | OpenSpec / 实现 | YApi | 处理 |
|------|------|-----------------|------|------|
````

## 契约优先级

- 请求/响应字段、类型、必填、路径、方法：以 `backend-yapi-*.md` 为最高依据。
- 业务流程、状态流、权限语义：以 GitLab/后端业务 spec 或 `proposal.md` 中已确认结论为准。
- E2E 和验收口径：以 `qa-*.md` 为最高依据。
- 三者冲突时必须记录为冲突，并请用户或协作者裁决。

## 完成标准

- 设计期只读：已输出接口契约摘要和不确定点。
- T1 后落盘：`backend-yapi-*.md` 已写入当前 change。
- 差异、增量、冲突已输出；需要代码或 spec 调整的项已写入 `tasks.md` 或最终回复。
