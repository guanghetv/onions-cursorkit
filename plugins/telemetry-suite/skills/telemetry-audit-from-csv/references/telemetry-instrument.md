---
name: telemetry-instrument
description: 自动为当前项目应用链路追踪和指标上报组件，实现相关可观测数据的上报。在用户要求接入链路追踪、指标、Prometheus、OpenTelemetry、可观测性，或按飞书《OpenTelemetry 接入指南（研发篇）》/《Prometheus 指标接入指南（研发篇）》改造代码时使用。
license: MIT
compatibility:
metadata:
  author: zhoufeng
  version: "1.0"
  generatedBy: "1.1.1"
---

# 链路追踪与指标接入

本技能依据以下飞书文档实现代码改造：
- **链路追踪**：《【可观测性】OpenTelemetry 接入指南（研发篇）》— `fetch-doc` 使用 `https://guanghe.feishu.cn/wiki/MhOHwNcWKi5soik13BHcRhENn0c`
- **指标上报**：《【可观测性】Prometheus 指标接入指南（研发篇）》— `fetch-doc` 使用 `https://guanghe.feishu.cn/wiki/ZGR5wHyMoiMEpoknHJUc0ixLnXc`

## 使用前

1. **确认需求**：用户明确要接入链路追踪和/或指标（Prometheus），或引用上述飞书文档。
2. **获取文档（可选）**：若需完整步骤、Node/APISIX 等，可先调用 `fetch-doc` 拉取对应文档再执行。

## 接入流程概览

1. **研发侧**：按下方规范改代码（依赖、初始化、中间件顺序、客户端、日志；指标侧增加 observer、Gorm/Redis 注册等）。
2. **配置侧**：
   - **链路追踪**：在「服务信息」多维表格勾选该服务的「**链路追踪接入**」，并在上线窗口期发布（会重启服务）。
   - **指标上报**：在「服务信息」→「Kubernetes容器服务」Tab 勾选该服务的「**Metrics指标采集**」，会在「Kubernetes链路追踪、Metrics、Nacos等接入」Tab 生成「指标采集」记录；同样在窗口期发布（会重启服务）。

---

# Golang 接入

## 1. 依赖

在项目根目录执行（按需保留已有依赖）：

```bash
go get gitlab.yc345.tv/backend/go-logger
go get gitlab.yc345.tv/security-and-payment/tracing
go get gitlab.yc345.tv/backend/utils/v2
# 若项目使用 yc 或 onionms，一并升级
# go get gitlab.yc345.tv/backend/yc
# go get gitlab.yc345.tv/backend/onionms/v2
```

## 2. 初始化 Trace 客户端

在 **main 包**、**应用启动最前面**（在创建 http/grpc server 之前）完成初始化。

- **服务名规则**：`应用部署名称.命名空间`，例如 `community.7to12`、`go-order.7to12`。
- 必须 `defer tracingcommon.Shotdown()`。

```go
import (
    tracingcommon "gitlab.yc345.tv/security-and-payment/tracing/common"
)

func main() {
    if err := tracingcommon.Init(tracingcommon.SetupConfig{
        ServiceName: "<应用名>.<命名空间>",
        Version:     Version, // 与 -ldflags "-X main.Version=..." 一致
        Ratio:       1,      // 全采样
    }); err != nil {
        panic(err)
    }
    defer tracingcommon.Shotdown()
    // ... 其余初始化、NewServer、app.Run()
}
```

## 3. 服务端中间件顺序（必须遵守）

**顺序**：`链路中间件` → `指标中间件` → `日志中间件` → `Recovery 中间件` → 其他业务中间件。  
这样日志里才能带上 trace_id，与链路关联。

### Kratos HTTP

```go
import (
    "github.com/go-kratos/kratos/v2/middleware/recovery"
    "github.com/go-kratos/kratos/v2/middleware/tracing"
    "github.com/go-kratos/kratos/v2/transport/http"
    logmiddleware "gitlab.yc345.tv/backend/go-logger/logger/middleware"
    "gitlab.yc345.tv/backend/utils/v2/metrics"
)

http.Middleware(
    tracing.Server(),
    metrics.KratosMiddleware(),
    logmiddleware.KratosMiddleware(&logmiddleware.LogOption{}),
    recovery.Recovery(),
    // ... 其他中间件
)
```

### Kratos gRPC

```go
grpc.Middleware(
    tracing.Server(),
    metrics.KratosMiddleware(),
    logmiddleware.KratosGRPCMiddleware(&logmiddleware.LogOption{}),
    recovery.Recovery(),
    // ... 其他中间件
)
```

### Gin

```go
import (
    "github.com/gin-gonic/gin"
    traceinggin "gitlab.yc345.tv/security-and-payment/tracing/gin"
    "gitlab.yc345.tv/backend/utils/v2/metrics"
    logmiddleware "gitlab.yc345.tv/backend/go-logger/logger/middleware"
)

router.Use(traceinggin.EnableTrace())
router.Use(metrics.GinMiddleware())
router.Use(logmiddleware.GinMiddleware(&logmiddleware.LogOption{}))
// ... 其他
```

### Echo

```go
import (
    "github.com/labstack/echo/v4"
    traceingecho "gitlab.yc345.tv/security-and-payment/tracing/echo"
    "gitlab.yc345.tv/backend/utils/v2/metrics"
    logmiddleware "gitlab.yc345.tv/backend/go-logger/logger/middleware"
)

router.Use(traceingecho.EnableTrace()...)
router.Use(metrics.EchoMiddleware())
router.Use(logmiddleware.EchoMiddleware(&logmiddleware.LogOption{}))
// ... 其他
```

## 4. Kratos 客户端（HTTP/gRPC）

- 使用 **`tracing.Client()`**，不要用 `tracing.Server()`。
- 客户端未加链路中间件时，只能依赖服务端打点。

```go
import (
    "github.com/go-kratos/kratos/v2/middleware/tracing"
    "github.com/go-kratos/kratos/v2/transport/grpc"
    "github.com/go-kratos/kratos/v2/transport/http"
)

// HTTP 客户端
conn, err := http.NewClient(ctx, http.WithMiddleware(tracing.Client()))

// gRPC 客户端
conn, err := grpc.DialInsecure(ctx, grpc.WithMiddleware(tracing.Client()))
```

## 5. Resty 客户端

- 用 `tracingresty.Middleware(resty.New())` 包装。
- 发请求时必须 `SetContext(ctx)`，才能把当前 span 注入请求头。

```go
import (
    tracingresty "gitlab.yc345.tv/security-and-payment/tracing/resty"
    "github.com/go-resty/resty/v2"
)

var Client = tracingresty.Middleware(resty.New())

func ClientWithContext(ctx context.Context) *resty.Request {
    return Client.R().SetContext(ctx)
}
// 使用：resp, err := ClientWithContext(ctx).Get(url)
```

## 6. 获取 trace_id

```go
import tracingcommon "gitlab.yc345.tv/security-and-payment/tracing/common"

traceID := tracingcommon.TraceID(ctx)
```

## 7. 日志与 trace_id 串联

- 使用 **go-logger >= v1.2.8**，通过 `WithContext(ctx)` 将链路上下文写入日志。
- 打日志时务必传 `ctx`：`logger.WithContext(ctx).Infof(...)`，便于在日志系统用 trace_id 查全链路。

---

# 指标上报配置（Prometheus）

依据飞书《【可观测性】Prometheus 指标接入指南（研发篇）》。接入后可通过 **9091** 端口查看：`http://ip:9091/metrics`（Runtime、HTTP/gRPC 指标）、`http://ip:9091/debug/pprof/`（pprof）。

## 指标依赖

```bash
go get gitlab.yc345.tv/backend/utils/v2
```

## GoRuntime【必须】

接入 `gitlab.yc345.tv/backend/utils/v2/observer`，暴露 9091 端口的 metrics 与 pprof。

**Kratos**：将 observer 作为 Server 注册进 App。

```go
import (
    "github.com/go-kratos/kratos/v2"
    "gitlab.yc345.tv/backend/utils/v2/observer"
)

func newApp(..., hs *http.Server, gs *grpc.Server) *kratos.App {
    observerSrv := observer.NewServer()
    return kratos.New(
        kratos.Server(hs, gs, observerSrv), // 与 http、grpc 一并传入
        // ...
    )
}
```

**Gin / Echo（非 Kratos）**：单独启动 observer 服务，与 HTTP 并列运行（如用 `errgroup` 同时 `observeSrv.Start(ctx)` 和 `httpSrv.ListenAndServe()`），并在退出时 `observeSrv.Stop(ctx)`。

## 服务端指标中间件【必须】

与链路一节一致，在 HTTP/gRPC 上必须挂载指标中间件（顺序：tracing → **metrics** → log → recovery）：

- **Kratos**：`metrics.KratosMiddleware()`（见上文「服务端中间件顺序」）
- **Gin**：`metrics.GinMiddleware()`
- **Echo**：`metrics.EchoMiddleware()`

## Gorm 指标【必须】

使用 utils/v2 的 orm 创建 DB 后，注册 Gorm 指标（便于看 DB 请求延迟、QPS 等）。

```go
import "gitlab.yc345.tv/backend/utils/v2/orm"

// 使用 orm.NewDBWithStruct 时
client, err := orm.NewDBWithStruct(conf)
// ...
orm.MustRegisterMetrics(client.Client, orm.WithDBName("服务名称"))

// 已有 *gorm.DB 时（v2）
orm.MustRegisterMetrics(db, orm.WithDBName("服务名称"))

// gorm v1
orm.MustRegisterGormV1Metrics(client, orm.WithDBName("服务名称"))
```

## Redis 指标【必须】

使用 utils/v2 的 redis 客户端时，注册 Redis 指标。

```go
import "gitlab.yc345.tv/backend/utils/v2/client/redis"

client := redis.NewClient(&redis.Config{...})
redis.MustRegisterMetrics(client.Instance(), redis.WithDBName("服务名称"))
```

## Node 指标【必须】

使用 `prom-client` 声明 Counter/Histogram，注册到 Registry；编写中间件在请求前后打点，并暴露 `GET /metrics` 返回 `register.metrics()`。接入方式：`pushMetrics.Register()` 后 `app.use(pushMetrics.httpMetricMiddlewareWrapper())`。详见飞书文档。

## 查看指标与大盘

- **测试环境**：https://prometheus-test.yc345.tv/graph  
- **正式环境（夜莺）**：https://n9e.yc345.tv/metric/explorer（员工账号需向巡检团队申请）  
- **Kratos 大盘**（接口延迟、QPS、错误率）：https://n9e.yc345.tv/dashboards/3  
- **Go Runtime 大盘**（内存、CPU、协程、线程）：https://n9e.yc345.tv/dashboards/1  

**APISIX** 指标接入见飞书《【APISIX/可观测性】APISIX接入Prometheus服务指标》等文档。

---

# 链路透传检查（改造后自检）

1. **Gin**：全程使用 `ginCtx.Request.Context()` 作为 context 向下透传，直到传给 resty 等客户端。
2. **Resty**：收到 ctx 后必须 `Client.R().SetContext(ctx)`。
3. **运维**：K8s deployment 需加 sidecar 注入：`sidecar.opentelemetry.io/inject: "true"`（见运维篇文档）。
4. **新 context**：异步或新开 context 时需继承链路。不要用 `context.Background()`；可用 `tracingcommon.ExtractFromCtx(ctx)`（tracing >= v1.1.8）仅复制链路信息。
5. **MQ 等**：见飞书《【Utils】MQ中间件使用指南》。
6. **日志**：确认 go-logger 已升级，并在需要处使用 `WithContext(ctx)`。

---

# 其他栈（简要）

- **Node（Koa/Egg）**：安装 `@guanghe/tracing`，在 koa/egg 等依赖**之前** require 并 `tracing.init({ serviceName, version })`。详见飞书文档。
- **APISIX**：需在 config 中启用 `opentelemetry` 插件并配置 collector、batch_span_processor 等，版本 >= v1.4.9。详见飞书文档。

需要完整 Node/APISIX 步骤时，请先用 feishu-mcp 的 `fetch-doc` 获取上述飞书文档全文再按文档改。

---

# 执行清单

改造时按顺序确认：

**链路追踪**
- [ ] 已添加/升级 go-logger、tracing、utils/v2 等依赖
- [ ] main 中已调用 `tracingcommon.Init` 且 `defer tracingcommon.Shotdown()`
- [ ] ServiceName 为 `应用名.命名空间`
- [ ] HTTP/gRPC 服务端中间件顺序：tracing → metrics → log → recovery → 其他
- [ ] 若有 Kratos/HTTP/gRPC 客户端，已加 `tracing.Client()`
- [ ] 若有 Resty，已用 tracingresty 包装且请求时 `SetContext(ctx)`
- [ ] 打日志处使用 `logger.WithContext(ctx)`
- [ ] 提醒用户在「服务信息」中勾选**链路追踪接入**并在窗口期发布

**指标上报**
- [ ] 已接入 `utils/v2/observer`（Kratos 将 `observer.NewServer()` 传入 `kratos.Server()`；Gin/Echo 单独起 observer 服务）
- [ ] HTTP/gRPC 已挂载 `metrics.KratosMiddleware()`（或 Gin/Echo 对应中间件）
- [ ] 若使用 Gorm，已调用 `orm.MustRegisterMetrics(..., orm.WithDBName("服务名称"))`
- [ ] 若使用 Redis（utils/v2/client/redis），已调用 `redis.MustRegisterMetrics(..., redis.WithDBName("服务名称"))`
- [ ] 提醒用户在「服务信息」中勾选**Metrics指标采集**并在窗口期发布
