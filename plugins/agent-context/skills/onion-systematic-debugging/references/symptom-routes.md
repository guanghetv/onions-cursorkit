# 症状分流（代码优先，运行时按需）

**默认第一刀是 GitNexus**（无 env）：对齐仓 → 路由/handler → 调用链。见 [gitnexus.md](gitnexus.md)。

运行时 MCP **不要**默认开、更不要四域并行。仅当代码不够或用户要现网数据时，先钉死唯一 `env`，再按下表 **只开一域**。

查指标遵循 `metrics-query`；查日志遵循 `logs-query`；查库遵循 `archery-query`。

| 用户说法 | 代码侧（默认先做） | 按需运行时（须已钉 env） |
|----------|--------------------|--------------------------|
| 慢 / 超时 | `query` + `context` 看下游调用、锁、远程 | 需要量/P99 时 metrics；需要对某次请求时 trace |
| 5xx / 业务错误 | `query` 错误文案/抛错点；`context` 调用链 | 需要对现网是否在报时 logs 或 `trace_search(has_error=true)` |
| 空/错数据 | `route_map` + 序列化/查询函数 `context` | 要核对库内数据时 archery 只读 |
| 仅前端异常、后端 200 | 前端仓 `route_map` 消费者 vs 后端 handler | 契约仍对不齐再 logs 对 `request_id` |
| 偶发 | 代码里重试/超时/降级路径 | 必须 `trace_id` / `request_id` 再查 trace/logs |

未出端（前端拦截、无 Network）→ 先 GitNexus 前端仓；不要用后端 QPS 结案。

不要一上来 `archery_query`。不要工单 submit/audit。不要跳过 GitNexus 直接扫运行时。
