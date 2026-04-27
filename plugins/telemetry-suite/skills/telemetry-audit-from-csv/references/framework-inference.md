# Telemetry 框架推测规则

这个文件定义 `telemetry:audit-from-csv` 单仓 worker 的“先推测框架，再审计”规则。

## 输出字段

worker 在正式判断四个 telemetry 维度前，先产出这三个字段：

- `推测框架`
- `推测置信度`
- `推测依据`

同时优先读取飞书透传下来的：

- `编程语言`

## 固定枚举

### `推测框架`

只允许输出以下枚举：

- `Kratos`
- `Gin`
- `Echo`
- `Koa`
- `Nest`
- `SpringBoot`
- `FrontendStatic`
- `TaskWorker`
- `Unknown`

### `推测置信度`

只允许输出：

- `高`
- `中`
- `低`

## 总体原则

1. 先看真实入口文件，再看依赖与目录结构，不要只凭依赖名下结论。
2. `编程语言` 来源于飞书 Base，作为主参考，不要在结果里被仓库推测覆盖。
3. 多个证据冲突时，优先相信“真实运行入口 + 中间件挂载”。
4. 如果飞书语言与仓库结构冲突，在 `推测依据` 中明确写出冲突。
5. 没有足够证据时输出 `Unknown`，不要硬猜。
6. `推测依据` 保持一句短中文，说明关键证据，不要写成长段分析。
7. 推测框架只是帮助选择审计视角，不替代四个缺失维度本身的判断。

## 语言提示

- `编程语言 = Go` 时，优先在 `Kratos / Gin / Echo / TaskWorker` 这些路径里找证据
- `编程语言 = Node` 时，优先在 `Koa / Nest / FrontendStatic / TaskWorker` 这些路径里找证据
- `编程语言 = Java` 时，优先检查 `SpringBoot`
- `编程语言` 为空时，正常回退到仓库结构推断

## 置信度映射

### `高`

满足任一类：

- 入口文件 + 依赖 + 中间件/启动方式三者一致
- 代码中存在明确框架签名，且能定位到实际运行入口

### `中`

满足任一类：

- 依赖和目录结构明显，但入口文件不够直接
- 有两个以上弱证据指向同一框架，但缺少完整启动链路

### `低`

满足任一类：

- 只能从少量依赖名或文件名推断
- 仓库多语言混合、示例代码较多、主入口不清晰

## 识别证据

### `Kratos`

强证据：

- `github.com/go-kratos/kratos`
- `http.NewServer(...)` / `grpc.NewServer(...)`
- `kratos.New(...)`

常见辅助证据：

- `internal/server/http.go`
- `internal/server/grpc.go`
- `wire_gen.go`

### `Gin`

强证据：

- `github.com/gin-gonic/gin`
- `gin.New()` / `gin.Default()`
- `router.Use(...)`

常见辅助证据：

- `handlers/`
- `router/router.go`

### `Echo`

强证据：

- `github.com/labstack/echo/v4`
- `echo.New()`
- `e.Use(...)`

### `Koa`

强证据：

- `new Koa()`
- `koa-router` / `@koa/router`
- `app.use(...)`

### `Nest`

强证据：

- `@nestjs/core`
- `NestFactory.create(...)`
- `AppModule`

### `SpringBoot`

强证据：

- `@SpringBootApplication`
- `spring-boot-starter-web`
- `SpringApplication.run(...)`

### `FrontendStatic`

强证据：

- `vite` / `react` / `vue` / `webpack` 等前端构建链明显
- Docker/Nginx 只托管静态产物
- 未见后端服务入口、任务入口或 server middleware

说明：

- 这种仓库默认不是本次 telemetry 规范的主目标
- 除非仓库里同时包含明确的后端服务子目录，否则优先判为 `FrontendStatic`

### `TaskWorker`

强证据：

- 明确存在 `consumer` / `cron` / `job` / `worker` / `queue` 入口
- 没有对外 HTTP server，但有长期运行任务进程

说明：

- `TaskWorker` 不是“没有框架”，而是“入口形态不是 Web server”
- 如果能明确看出底层还是 Kratos/Gin/Echo，也优先输出底层框架；只有确实看不出 Web 框架、但能确认是任务型进程时，才输出 `TaskWorker`

### `Unknown`

适用场景：

- 仓库不可读
- 示例代码与真实代码混杂
- 多个入口互相冲突，无法判断哪个真正部署
- 只有零散依赖，没有可确认的启动方式

## 冲突处理

### Web 框架 vs 任务入口

- 若同时存在 `main.go` Web server 和 `cmd/consumer/main.go` 这类任务入口，优先输出主 Web 框架，如 `Kratos` / `Gin` / `Echo`
- 只有任务入口明显存在，且未见 Web server，再输出 `TaskWorker`

### 前端仓 vs 后端子目录

- 若仓库主目录是前端，但有独立后端可部署子目录，按真正参与部署的后端入口判断
- 若只有静态产物托管链路，则输出 `FrontendStatic`

### 多框架混杂

- 优先输出真正承载入口流量的框架
- `推测依据` 明确写出为何忽略其他子目录，例如“主入口为 Gin，另有 scripts/ 示例目录不计入”

### 飞书语言 vs 仓库结构

- 飞书语言作为主参考保留在结果里
- `推测框架` 可以与飞书语言产生冲突，但必须在 `推测依据` 中说明
- 不要新增第二个“仓库推测语言”字段，避免形成两套真值

## 框架到审计视角映射

### `Kratos`

- 优先找 `tracing.Server()`、`metrics.KratosMiddleware()`、`observer.NewServer()`
- 同时检查是否存在 `tracing.Client()`

### `Gin`

- 优先找 `EnableTrace()`、`metrics.GinMiddleware()`、独立启动的 observer

### `Echo`

- 优先找 `EnableTrace()`、`metrics.EchoMiddleware()`、独立启动的 observer

### `Koa` / `Nest` / `SpringBoot`

- 优先找等价 tracing 初始化、Prometheus 暴露、`/metrics`、框架内中间件或拦截器接入
- 如果只有普通日志中间件，不算 telemetry 已接入

### `FrontendStatic`

- 一般不应强行套用后端 server middleware 规则
- 若确认为纯前端静态仓，通常更适合判定为非目标仓或在 `备注` 中说明不适用于当前 telemetry 规范

### `TaskWorker`

- 不要求对外 HTTP server
- 重点看入口初始化、出站 tracing、任务执行链路里的 Redis/Pg 使用情况

### `Unknown`

- 保守审计
- 对无法判断的维度优先输出 `未知`
- 在 `备注` 里说明不确定性来源

## 框架到接入模板映射

第二阶段除了输出 `推测框架`，还要进一步把结果映射到后续接入阶段要消费的 `接入模板` 与 `运行形态`。

推荐映射：

- `Go + Kratos` -> `接入模板 = Go-Kratos-Web`，`运行形态 = WebServer`
- `Go + Gin` -> `接入模板 = Go-Gin-Web`，`运行形态 = WebServer`
- `Go + Echo` -> `接入模板 = Go-Echo-Web`，`运行形态 = WebServer`
- `Go + TaskWorker` -> `接入模板 = Go-TaskWorker`，`运行形态 = TaskWorker`
- `Node + Koa` -> `接入模板 = Node-Koa-Web`，`运行形态 = WebServer`
- `Node + Nest` -> `接入模板 = Node-Nest-Web`，`运行形态 = WebServer`
- `Node + FrontendStatic` -> `接入模板 = Node-FrontendStatic`，`运行形态 = FrontendStatic`
- `SpringBoot` -> `接入模板 = Java-SpringBoot-Web`，`运行形态 = WebServer`
- 无法稳定归类时，保守写成 `Go-Unknown / Node-Unknown / Java-Unknown / Unknown`

## 适用性提醒

`推测框架` 只决定“更像哪类仓库”，不等于所有接入项都适用。

后续调度器还需要结合语言与模板，继续派生：

- `Observer适用性`
- `服务端Tracing适用性`
- `服务端Metrics适用性`
- `Redis指标适用性`
- `Pg指标适用性`

例如：

- `Node-Koa-Web` 通常不应该再套用 Go 的 `observer`、`redis.MustRegisterMetrics`、`orm.MustRegisterMetrics`
- `Go-TaskWorker` 不应强行要求 Web server metrics middleware
- `FrontendStatic` 通常不应进入当前后端 telemetry 接入模板
