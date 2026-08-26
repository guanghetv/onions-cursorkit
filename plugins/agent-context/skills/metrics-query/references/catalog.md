# 洋葱标准指标目录（快照，辅助）

查询主路径用 [intent-map.md](intent-map.md)。本文件供按名称翻查；非每次必读。

- 来源：[飞书多维表格](https://guanghe.feishu.cn/base/V4RhbYoCsa3Q45sW3Sicln8unEm?table=tblMn0xrY1sCuglk&view=vewcknbWZQ)
- 同步：2026-08-12（view `vewcknbWZQ`，59 条）
- 说明：仓库内 SSOT 供 Agent 查阅；表格变更后请回写本文件。类型字段保留源表拼写 `Guage`。

## Server

| 指标名称 | 类型 | 告警 | 描述 |
|----------|------|------|------|
| yc_request_totals | Counter | 是 | 服务端请求速率 |
| yc_request_duration_seconds | Histogram | 是 | 服务端请求延迟 |

## MQ

| 指标名称 | 类型 | 告警 | 描述 |
|----------|------|------|------|
| yc_mq_request_totals | Counter | 是 | 消息队列生产/消费速率 |
| yc_mq_request_duration_seconds | Histogram | 是 | 消息队列生产/消费延迟 |

## Redis

| 指标名称 | 类型 | 告警 | 描述 |
|----------|------|------|------|
| yc_redis_pool_conn_idle_current | Guage | 否 | 连接池当前空闲连接数 |
| yc_redis_pool_conn_total_current | Guage | 否 | 连接池当前连接总数 |
| yc_redis_pool_conn_stale_total | Counter | 否 | 连接池删除的失效连接数 |
| yc_redis_pool_hit_total | Counter | 否 | 连接池获取到连接次数 |
| yc_redis_pool_miss_total | Counter | 是 | 连接池未命中总次数（无空闲连接可借） |
| yc_redis_pool_timeout_total | Counter | 是 | 连接池获取连接超时次数 |
| yc_redis_request_totals | Counter | 否 | redis 操作请求速率 |
| yc_redis_bandwidth | Counter | 否 | redis 操作读写带宽 |
| AggregatedP99QueryLatency | Guage | 是 | Proxy→Server 请求耗时 P99 |
| AggregatedConnUtil_aggregated_proxy_VCM_Redis | Guage | 是 | 已用连接数 / 实例总连接数 |

## Gorm

| 指标名称 | 类型 | 告警 | 描述 |
|----------|------|------|------|
| gorm_dbstats_idle | Guage | 否 | 连接池当前空闲连接数 |
| gorm_dbstats_in_use | Guage | 否 | 连接池当前正在使用连接数 |
| gorm_dbstats_max_idle_closed | Guage | 否 | 由于空闲计数而关闭的连接总数 |
| gorm_dbstats_max_idletime_closed | Guage | 否 | 由于空闲时间而关闭的连接总数 |
| gorm_dbstats_max_lifetime_closed | Guage | 否 | 由于最大连接生命周期限制而关闭的连接总数 |
| gorm_dbstats_max_open_connections | Guage | 否 | 连接池最大打开连接数 |
| gorm_dbstats_open_connections | Guage | 否 | 连接池打开连接数 |
| gorm_dbstats_wait_count | Counter | 是 | 等待可用连接的总次数 |
| gorm_dbstats_wait_duration | Counter | 是 | 等待可用连接的总时间（纳秒） |

## Runtime

| 指标名称 | 类型 | 告警 | 描述 |
|----------|------|------|------|
| process_cpu_seconds_total | Counter | 否 | 程序使用的 CPU 时间总量 |
| process_max_fds | Guage | 否 | 系统打开的最大文件描述符数量 |
| process_open_fds | Guage | 否 | 系统打开的文件描述符数量 |
| process_resident_memory_bytes | Guage | 否 | 常驻内存大小 |
| process_start_time_seconds | Guage | 否 | 程序启动时间（秒） |
| process_virtual_memory_bytes | Guage | 否 | 虚拟内存大小 |
| process_virtual_memory_max_bytes | Guage | 否 | 最大虚拟内存 |
| go_gc_duration_seconds | Summary | 否 | 每次垃圾回收的持续时间（秒） |
| go_goroutines | Guage | 否 | 当前协程数量 |
| go_info | Guage | 否 | SDK 版本信息 |
| go_memstats_alloc_bytes | Guage | 否 | 使用中的内存总量 |
| go_memstats_alloc_bytes_total | Counter | 否 | 分配的内存总量（累计） |
| go_memstats_frees_total | Counter | 否 | 释放的内存对象的总次数 |
| go_memstats_gc_sys_bytes | Guage | 否 | 垃圾回收分配的内存总量 |
| go_memstats_heap_alloc_bytes | Guage | 否 | 堆上分配并正在使用的内存总量 |
| go_memstats_heap_idle_bytes | Guage | 否 | 堆上已分配但未使用的内存总量 |
| go_memstats_heap_inuse_bytes | Guage | 否 | 正在使用的堆内存总量 |
| go_memstats_heap_objects | Guage | 否 | 当前堆上对象总数 |
| go_memstats_heap_released_bytes | Guage | 否 | 堆中释放并返回给操作系统的内存总量 |
| go_memstats_heap_sys_bytes | Guage | 否 | 堆内存占用（含未使用） |
| go_memstats_last_gc_time_seconds | Guage | 否 | 最后一次 GC 时间 |
| go_memstats_lookups_total | Counter | 否 | 内存对象查找总次数 |
| go_memstats_mallocs_total | Counter | 否 | 内存分配总次数 |
| go_memstats_mcache_inuse_bytes | Guage | 否 | mcache 正在使用的内存 |
| go_memstats_mcache_sys_bytes | Guage | 否 | mcache 总内存 |
| go_memstats_mspan_inuse_bytes | Guage | 否 | mspan 正在使用的内存 |
| go_memstats_mspan_sys_bytes | Guage | 否 | 分配给 mspan 的总内存 |
| go_memstats_next_gc_bytes | Guage | 否 | 下一次 GC 触发时的堆大小目标 |
| go_memstats_stack_inuse_bytes | Guage | 否 | 正在使用的栈内存总量 |
| go_memstats_stack_sys_bytes | Guage | 否 | 分配给所有 goroutine 栈的总内存 |
| go_memstats_sys_bytes | Guage | 否 | 从系统分配的总内存量 |
| go_threads | Guage | 否 | 当前线程数量 |

## PostgreSQL

| 指标名称 | 类型 | 告警 | 描述 |
|----------|------|------|------|
| SlowQueries_engine_monitor_VCM_RDS_PostgreSQL | Guage | 是 | 每秒慢查询个数（超过 log_min_duration_statement） |
| ConnectionUsedUtil_engine_monitor_VCM_RDS_PostgreSQL | Guage | 是 | 连接数占用最大连接数的比例 |
| ErrorQueries_engine_monitor_VCM_RDS_PostgreSQL | Guage | 是 | 每秒错误查询个数 |
| DeadLocksCount_engine_monitor_VCM_RDS_PostgreSQL | Guage | 是 | 以 database 为单位的死锁数量 |
