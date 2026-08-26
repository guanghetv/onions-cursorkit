---
name: archery-query
description: >-
  DBA 数据库证据与 Archery 工单专用 skill（与 mcp-archery 一对一）：确认 env、explore、只读查询、SQL review、预检提交与两阶段审批。
  Use when querying Postgres/Redis/Mongo, reviewing SQL, or submitting/auditing Archery workflows through mcp-archery.
metadata:
  requires_mcp:
    - mcp-archery
  min_tools:
    - archery_available_envs
    - archery_explore
    - archery_query
    - archery_sql_review
    - archery_workflow_submit
    - archery_workflow_audit
---

# Archery Query（DBA 查询）

## 定位

`mcp-archery` 的配套 skill：**六刀流程 + 凭证约定 + 五态解读**。

**做**：选 env、探索元数据、只读查询、SQL/命令 review、预检后提交工单、两阶段审批、陈述观测。
**不做**：根因结论、工单 execute/cancel、绕过 MCP 直连库脚本作为正式路径。

## 工作流程

1. **确认 env** — `archery_available_envs`（看 `mode` / `llm_gate` / `engines`）；勿猜。
2. **探索** — `archery_explore`（`action=list_instances|list_databases|list_tables|describe_table`）：
   - **预发/生产（`mode=archery`）**
     - 账号经 MCP client headers：`X-Archery-Username` / `X-Archery-Password`（**不要**写进工具参数）；**必填**
     - **不要**传 Archery baseUrl（服务端配置）
     - 用 `instance_name` / `db_name` / `schema_name` / `table_name` 定位
     - PG：`list_tables` / `describe_table` 未传 `schema_name` 时服务端默认 `public`
   - **测试（`mode=direct`）**
     - 先 `list_instances` 取目录逻辑名（形如 `[postgres]host:port`）
     - 后续必须带 `instance_name`（及 `db_name`）；**不要**传 `host`/`port`/`db_type` 当连接串
     - 账号**只看服务端** `instances_file` 目录；**不受** Archery headers 影响（含无密码 Redis）
     - `list_instances` **不要求** headers
3. **语句字段** — 三引擎统一用 `statement`：
   - Postgres：SQL
   - Redis：命令（如 `GET key` / `INFO keyspace`）
   - Mongo：**必须是 JSON object**，例如 `{"find":"orders","filter":{}}`；行数使用 tool 的 `limit` 参数，禁止 `db.x.find()` shell
   - Mongo Archery query 支持 `find` / `aggregate`；workflow 支持 `update` / `delete` / `insert`。服务端严格转换为 Archery Mongo Shell。非法 JSON、尾随内容、未知 command、未知 JSON 字段会在出网前 `denied`。query collection 仅允许 `[A-Za-z0-9_.]`；workflow collection 额外允许 `-`
   - Mongo direct 当前仅实现 `find`；`aggregate` / `listCollections` 尚未接入，调用会返回 `needs_confirmation`
4. **`db_type`**
   - `direct`：由目录条目决定，一般无需再传
   - `archery`：非 Postgres 时请显式传 `db_type`（`redis` / `mongo`）；缺省按 postgres 护栏处理
5. **Review** — `archery_sql_review`：只采证据、**不执行**业务查询。
   - `llm_gate=true`：会调 LLM，返回 `passed` / `issues` / `suggestions`
   - `llm_gate=false`：仍采 EXPLAIN 等证据，**不调** LLM（`passed` 默认可为 true）
6. **查询** — `archery_query`（默认 `limit=10`）：
   - `llm_gate=true`：必须先过 LLM；`passed=false` → `denied`，**勿当成功重试绕过**
   - `llm_gate=false`：只过只读护栏后执行
   - 响应经脱敏；看 `meta.redacted_fields`；勿把 `***` 当真实值。`_id` / `userId` / `user_id` / `paymentCredentials` / `payment_credentials` 不会仅因字段名被全局遮蔽，但字段值仍受手机号、邮箱、Bearer 等按值规则约束
7. **提交工单** — `archery_workflow_submit`，仅 `mode=archery`：
   - 明确提供 env、instance、database、statement、工单名、需求链接、组和备份选项
   - 服务端始终先跑 Archery `sqlcheck`，并始终调用 LLM（与 query 的 `llm_gate` 无关）
   - **Redis / Mongo workflow 不要期望 Archery explain**：服务端不会对这些写命令做 explain/query 采证，只把 `sqlcheck` 交给 LLM
   - 其它可适用引擎能采则采 EXPLAIN / 表结构 / 索引；采不到不算明确风险
   - `sqlcheck` 报错或 `is_critical`，或 LLM `passed=false` → `denied`：展示风险点，禁止换参数或带令牌绕过
   - `needs_confirmation` 且带 `confirmation_token` 时（Redis / Mongo workflow、无 EXPLAIN、LLM 故障等），先把证据缺口告知用户；仅在用户明确确认后，以完全相同的工单参数重调
   - `ok` 时返回并展示 `workflow_url`（EXPLAIN 完整且 LLM 通过时可能跳过二次确认直接建单）
8. **审批工单** — `archery_workflow_audit`，仅 `mode=archery`：
   - 输入 env 与 Archery 工单链接（须为当前 env 的 `https://…/detail/<id>/`）；仅 `workflow_manreviewing` 可预览
   - 首次调用只能预览，不得携带伪造 token 或自动一键通过；`audit_remark` 在 preview 与 confirm 必须一致（省略则服务端使用同一默认 remark）
   - 向用户展示工单摘要并获得明确确认后，原样携带返回的 `confirmation_token` 与同一 remark 再调一次
   - 状态漂移、用户变化、令牌过期、remark 变化或 URL 非当前 env host 时停止，不得绕过
   - 只支持审核通过；禁止调用或声称执行了 execute
9. **按五态处置** — 见下表；交付不写根因。

## 判定原则

| status | 含义 |
|--------|------|
| `ok` | 可引用 `data` |
| `no_data` | 合法但空结果 |
| `not_integrated` | 后端/引擎未接入 |
| `denied` | 护栏拒绝、缺参、env 禁止、或 LLM `passed=false` |
| `needs_confirmation` | 写操作等待明确确认，或 Archery/DB/LLM 故障、超时、结果不确定 |

## 禁止事项

- 禁止绕过 MCP 用 `curl`/本地驱动作为正式取证路径。
- 禁止在交付中写根因结论。
- 禁止把密码写入日志或复述给用户。
- 禁止在 `mode=direct` 下用 headers 账号覆盖目录账号，或传裸 `host`/`port` 连接。
- 禁止自动完成 `archery_workflow_audit` 的 Preview + Confirm；两次调用之间必须获得用户明确确认。
- 禁止执行工单 execute/cancel，或对结果不确定的 submit/audit 自动重试。

## 交付物

1. env / mode / db_type / 资源定位（`instance_name`、库表）  
2. `statement` 与是否过 `llm_gate` / 工单预检
3. `status` + 观测要点（或 issues/suggestions）
4. 工单操作成功时给出 `workflow_url`；等待确认时说明下一步而不代替用户确认
5. 不写根因结论
