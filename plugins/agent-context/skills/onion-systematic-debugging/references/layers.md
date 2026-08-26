# 请求路径：代码对齐为主，运行时按需

默认先问：这条路径在 **哪个仓、哪段代码** 上。运行时进/出只在按需加载后填写。

```text
客户端(App/Web)          → GitNexus 前端仓 / route_map 消费者
  → 接入(网关，无独立 MCP)
    → 本服务 HTTP/gRPC     → GitNexus 后端仓 / route_map handler / context
      → 下游 RPC / MQ      → 调用链 context；现网耗时才上 trace
        → Redis / PG / Mongo → 代码里的访问点；核对数据才上 archery
```

| 层 | 默认（GitNexus） | 按需运行时 |
|----|------------------|------------|
| 客户端 | 前端仓符号、是否发出请求（用户 Network + 代码） | 无 RUM |
| 接入 | 代码里的网关/SDK 调用 | 无独立 MCP |
| 本服务 | handler、中间件、业务函数 | metrics / logs / trace |
| 下游 | `context` 出站调用 | 慢/错时 trace |
| 数据层 | 代码中的 SQL/Redis/Mongo 调用点 | 仅当要核实时 archery |
| 发布 | 无（`mcp-change` 未落地） | 只能问人 |

运行时一旦开了，遵守单 `env`、绝对时间窗；进/出证据与代码节分开写，禁止用静态调用链冒充现网。
