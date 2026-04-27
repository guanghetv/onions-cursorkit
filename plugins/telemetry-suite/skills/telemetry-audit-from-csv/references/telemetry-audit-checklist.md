# Telemetry 审计 Checklist

这个文件是对本地 vendored `telemetry-instrument.md` 的审计视角提炼，供单仓 worker 在只读检查时快速判断。

使用顺序建议：

1. 先读飞书透传的 `编程语言`
2. 再参考 `framework-inference.md` 推测框架
3. 最后按这个 checklist 找对应强证据

这个 checklist 负责判断“是否缺失”，不直接等于“是否适用”。

第二阶段调度器还需要在审计结论之外，额外派生：

- `接入模板`
- `运行形态`
- `接入适用性矩阵`

例如同样是后端服务：

- Go Kratos Web 服务通常需要 `observer + tracing middleware + metrics middleware`
- Node Koa/Nest 服务通常看等价 tracing 初始化与 Prometheus 暴露，不应照搬 Go 的 `Redis/Pg` 指标注册规则
- TaskWorker 不应强行套用 Web server 中间件要求

## 一、链路追踪

优先找这些强证据：

- `tracingcommon.Init(...)`
- `defer tracingcommon.Shotdown()`
- Kratos 服务端：`tracing.Server()`
- Gin：`EnableTrace()`
- Echo：`EnableTrace()`
- Kratos 客户端：`tracing.Client()`
- Resty：`tracingresty.Middleware(...)`
- 日志：`logger.WithContext(ctx)`

### `链路追踪缺失 = 否`

满足下面任一组，通常可判定为已接入：

- 服务入口完成 `tracingcommon.Init(...)`，且服务端 HTTP/gRPC 中间件接了 tracing
- 非 Kratos 服务明确接了 Gin/Echo tracing 中间件
- 纯客户端/任务型服务没有对外 server，但入口完成 tracing 初始化，且关键出站链路接了 tracing

### `链路追踪缺失 = 是`

满足下面情况之一：

- 服务进程明显存在，但未见 tracing 初始化与服务端 tracing 中间件
- Node / Python / 其他栈明确存在服务入口，但未见等价 tracing 接入

### `链路追踪缺失 = 未知`

- 仓库不可读
- 难以确认哪个入口真正参与部署

## 二、Metrics

优先找这些强证据：

- `observer.NewServer()`
- `metrics.KratosMiddleware()`
- `metrics.GinMiddleware()`
- `metrics.EchoMiddleware()`
- 明确暴露 `/metrics`

### `Metrics缺失 = 否`

满足下面任一组，通常可判定为已接入：

- `observer.NewServer()` + HTTP/gRPC metrics middleware
- 非 Kratos 服务明确挂了 Gin/Echo metrics middleware
- 其他栈明确暴露 Prometheus 指标并有注册代码

### `Metrics缺失 = 是`

- 服务入口明确存在，但未见 observer、metrics middleware、Prometheus 指标暴露或等价证据

### `Metrics缺失 = 未知`

- 仓库不可读
- 无法确定是否为真正服务进程

## 三、Redis 指标

优先找这些强证据：

- `redis.MustRegisterMetrics(...)`
- 明确的 Redis metrics hook / instrumentation

### `Redis指标缺失 = 否`

- Redis 在运行链路里被实际使用，且找到上面的强证据
- 仓库中明确未使用 Redis，可判定为 `否`

### `Redis指标缺失 = 是`

- Redis 在运行链路里被实际使用，但只见普通建连 / client 初始化，未见 metrics 注册或 hook

### `Redis指标缺失 = 未知`

- 是否真的使用 Redis 不明确
- 仓库不可读

## 四、Pg 指标

优先找这些强证据：

- `orm.MustRegisterMetrics(...)`
- `orm.MustRegisterGormV1Metrics(...)`
- `gorm.io/plugin/prometheus`
- `client.Client.Use(prometheus.New(...))`

### `Pg指标缺失 = 否`

- PG / Gorm / sqlx / pgx 在运行链路里被实际使用，且找到上面的强证据
- 仓库中明确未使用 PG，可判定为 `否`

### `Pg指标缺失 = 是`

- PG 在运行链路里被实际使用，但只见普通建连或 ORM 初始化，未见指标注册

### `Pg指标缺失 = 未知`

- 是否真的使用 PG 不明确
- 仓库不可读

## 五、保守原则

- `disableMetric=false`、依赖已安装、封装库存在，这些都只能算弱证据
- 如果没有看到明确调用点，默认不要判成“已接入”
- `检查摘要` 保持短句即可，`备注` 再写阻塞原因或关键证据
- 审计唯一键按 `服务名称 + 命名空间`
