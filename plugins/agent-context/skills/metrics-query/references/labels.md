# 已知 Label 约定

来源：`gitlab.yc345.tv/backend/utils/v2/metrics`（应用侧 `yc_*`）。  
平台还可能附加 `app`、`namespace` 等 relabel；以实际 `metrics_query` 返回的 series labels 为准。

## `yc_request_totals` / `yc_request_duration_seconds`

| Label | 含义 |
|-------|------|
| `protocol` | `http` 或 `grpc`（Kratos `transport.KindHTTP` / `KindGRPC` 的 `String()`） |
| `route` | 请求路由 / operation |
| `status` | HTTP 状态码（字符串） |
| `logStoreId` | 日志存储 id（环境变量 `LOG_STORE_ID`） |

区分 HTTP / gRPC：**同一指标名** + `protocol` 过滤，不要换指标名。

## `yc_mq_request_totals` / `yc_mq_request_duration_seconds`

| Label | 含义 |
|-------|------|
| `protocol` | `rocketmq` / `kafka` 等 |
| `operation` | 发布 / 消费 |
| `route` | topic |
| `status` | 正常约 `200`，错误为非 200 |
| `logStoreId` | 同上 |

## `yc_redis_request_totals` / `yc_redis_bandwidth`

| 指标 | Labels |
|------|--------|
| `yc_redis_request_totals` | `route` |
| `yc_redis_bandwidth` | `route`, `type`（读/写等） |
| `yc_redis_request_slow_query_totals` | （无额外 label 或视版本） |

连接池系列（`yc_redis_pool_*`）以返回 labels 为准，查询前可用小 `limit` 探查。

## Gorm `gorm_dbstats_*`

多为 Gauge/Counter 池状态；常见按 DB 实例或 `app` 区分。高基数时按已有 label 聚合。

## Runtime `go_*` / `process_*`

常用过滤：`app`、`namespace`（与 service-doctor / observability 习惯一致）。

## 探查未知 label

1. `metrics_list` 确认指标名存在。  
2. `metrics_query`：`count by (__name__) ({__name__="yc_request_totals",app="<app>"})` 或带小 `limit` 的瞬时查询，从返回 series 读 label 键。  
3. 勿在未知时猜测 `kind` / `method` 等未注册名。
