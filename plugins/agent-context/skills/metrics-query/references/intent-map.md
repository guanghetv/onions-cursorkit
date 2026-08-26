# 意图地图（metrics-query 主地图）

查询指标时先查本表，再调 `mcp-metrics`。场景 skill 需要指标时引用本文件，勿复制。

占位符：`<app>` = 服务 app 名；`<env>` 经 `metrics_available_servers` 确认后传入 tool（不写进 PromQL）。  
默认窗口示例：`[5m]`；趋势查询用 `metrics_query` 的 `start`/`end`/`step`。

## Server（流量 / QPS / 延迟）

| 用户意图 | 指标 | 类型 | 要点 |
|----------|------|------|------|
| QPS、请求速率、流量 | `yc_request_totals` | Counter | `protocol`=`http`\|`grpc` |
| HTTP 流量 / HTTP QPS | 同上 | Counter | `protocol="http"` |
| gRPC 流量 / gRPC QPS | 同上 | Counter | `protocol="grpc"` |
| 延迟、耗时、P99/P95 | `yc_request_duration_seconds` | Histogram | 同上 `protocol` |

```promql
# 总 QPS（所有协议）
sum(rate(yc_request_totals{app="<app>"}[5m]))

# HTTP QPS
sum(rate(yc_request_totals{app="<app>",protocol="http"}[5m]))

# gRPC QPS
sum(rate(yc_request_totals{app="<app>",protocol="grpc"}[5m]))

# 按路由看 Top 流量（注意基数；必要时加 limit 或进一步过滤）
topk(10, sum by (route) (rate(yc_request_totals{app="<app>",protocol="http"}[5m])))

# 错误率近似（非 2xx；按实际 status 约定调整）
sum(rate(yc_request_totals{app="<app>",status!~"2.."}[5m]))
/
sum(rate(yc_request_totals{app="<app>"}[5m]))

# P99 延迟（HTTP）
histogram_quantile(
  0.99,
  sum by (le) (rate(yc_request_duration_seconds_bucket{app="<app>",protocol="http"}[5m]))
)
```

## MQ

| 意图 | 指标 | 模板要点 |
|------|------|----------|
| MQ 吞吐 / 生产消费速率 | `yc_mq_request_totals` | `protocol`=rocketmq\|kafka；`operation`；`route`=topic |
| MQ 延迟 | `yc_mq_request_duration_seconds` | Histogram，同上 label |

```promql
sum(rate(yc_mq_request_totals{app="<app>"}[5m]))
sum by (operation, route) (rate(yc_mq_request_totals{app="<app>"}[5m]))
histogram_quantile(0.99, sum by (le) (rate(yc_mq_request_duration_seconds_bucket{app="<app>"}[5m])))
```

## Redis（应用侧客户端指标）

| 意图 | 指标 |
|------|------|
| Redis QPS / 操作速率 | `yc_redis_request_totals` |
| 读写带宽 | `yc_redis_bandwidth` |
| 连接池空闲 / 总数 | `yc_redis_pool_conn_idle_current` / `yc_redis_pool_conn_total_current` |
| 池未命中 / 获取超时 | `yc_redis_pool_miss_total` / `yc_redis_pool_timeout_total`（常告警） |

```promql
sum(rate(yc_redis_request_totals{app="<app>"}[5m]))
sum(rate(yc_redis_pool_miss_total{app="<app>"}[5m]))
yc_redis_pool_conn_idle_current{app="<app>"}
```

云厂商实例级（名称异于 `yc_*`，见 catalog）：

- `AggregatedP99QueryLatency`
- `AggregatedConnUtil_aggregated_proxy_VCM_Redis`

查询前用 `metrics_list` 的 `match`/`prefix` 确认是否在当前 env 可见；label 可能与应用侧不同。

## Gorm / DB 连接池

| 意图 | 指标 |
|------|------|
| 使用中 / 空闲 / 打开连接 | `gorm_dbstats_in_use` / `gorm_dbstats_idle` / `gorm_dbstats_open_connections` |
| 等待次数 / 等待时间 | `gorm_dbstats_wait_count` / `gorm_dbstats_wait_duration`（常告警） |
| 最大打开连接 | `gorm_dbstats_max_open_connections` |

```promql
gorm_dbstats_in_use{app="<app>"}
gorm_dbstats_open_connections{app="<app>"}
sum(rate(gorm_dbstats_wait_count{app="<app>"}[5m]))
```

## Runtime

| 意图 | 指标 |
|------|------|
| Goroutine | `go_goroutines` |
| 堆内存 / 常驻内存 | `go_memstats_heap_inuse_bytes` / `process_resident_memory_bytes` |
| CPU | `process_cpu_seconds_total`（用 `rate`） |
| 是否接入基础指标 | `go_info`（有序列 ≈ 基础指标已上报） |

```promql
go_goroutines{app="<app>"}
go_memstats_heap_inuse_bytes{app="<app>"}
rate(process_cpu_seconds_total{app="<app>"}[5m])
go_info{app="<app>"}
```

## PostgreSQL（RDS 监控名）

| 意图 | 指标 |
|------|------|
| 慢查询个数 | `SlowQueries_engine_monitor_VCM_RDS_PostgreSQL` |
| 连接使用率 | `ConnectionUsedUtil_engine_monitor_VCM_RDS_PostgreSQL` |
| 错误查询 | `ErrorQueries_engine_monitor_VCM_RDS_PostgreSQL` |
| 死锁 | `DeadLocksCount_engine_monitor_VCM_RDS_PostgreSQL` |

先 `metrics_list` 确认名称；选择器常按实例而非 `app`，**不要**硬套 Server 的 `app` 模板。

## 调用顺序速记

```
意图 → intent-map 选指标
  → metrics_list(prefix) 可选确认
  → metrics_query(env, PromQL [, start,end,step] [, limit])
  → 解读 status → 交付物
```
