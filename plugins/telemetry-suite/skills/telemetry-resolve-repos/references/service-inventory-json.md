# 服务清单 JSON 契约

文件名推荐：`service-inventory.json`

## 顶层字段

- `filter`: 当前过滤语义描述
- `dedupe_by`: 去重键说明
- `programming_language_field`: 本次实际命中的飞书语言字段名；若为空表示未命中
- `runtime_environment_field`: 本次实际命中的飞书运行环境字段名；若为空表示未命中
- `service_total_before_filter`: 原始记录数
- `service_total_after_filter`: 过滤后记录数
- `records`: 服务记录数组

## 记录字段

每条记录至少包含：

- `service_name`
- `namespace`
- `business_owner`
- `programming_language`
- `runtime_environment`
- `contains_production_env`
- `service_type`
- `service_status`
- `metrics_status`
- `tracing_status`
- `redis_metrics_status`
- `pg_metrics_status`
- `source_base_token`
- `source_table_id`
- `source_view_id`

## 过滤规则

生成时按以下规则过滤：

- `service_type == 后端`
- `runtime_environment` 包含 `正式环境`
- `service_status` 不属于 `待下线`、`已下线`
- `business_owner` 不属于这些值：
  - `测试技术支撑`
  - `运维`
  - `工程效率`
  - `未知`
  - `技术战共创`
  - `数据中台`
  - `APP组`

## 去重规则

默认按 `service_name + namespace` 去重。

## 编程语言字段

- 优先从飞书 Base 读取 `编程语言`
- 若不存在，按 `开发语言`、`语言` 顺序回退探测
- 读取后写入 `programming_language`
- 即使为空，也不参与过滤，只作为后续仓库解析与审计的 hint

## 运行环境字段

- 默认从飞书 Base 读取 `运行环境`
- 读取后写入 `runtime_environment`
- 并派生 `contains_production_env`：
  - 包含 `正式环境` -> `是`
  - 其余 -> `否`
- 第一阶段严格只保留 `contains_production_env = 是` 的记录

## 三态规则

四个勾选字段统一保留三态：

- `true`
- `false`
- `null`

## 边界说明

这里的：

- `metrics_status`
- `tracing_status`
- `redis_metrics_status`
- `pg_metrics_status`

只代表飞书服务信息表里的当前勾选状态。

它们适合做：

- 原始台账保留
- 后续比对“代码已接入但飞书未勾选”或“飞书已勾选但代码未落实”

它们不适合直接代表：

- 当前仓库按什么 `接入模板` 改造
- `Redis/Pg` 对这个仓库是否真正适用
- Node/Go/TaskWorker/FrontendStatic 的代码接入差异

这些代码层适用性，应该在第二阶段基于 `编程语言 + 推测框架 + 仓库形态` 继续派生，而不是在第一阶段直接写死。
