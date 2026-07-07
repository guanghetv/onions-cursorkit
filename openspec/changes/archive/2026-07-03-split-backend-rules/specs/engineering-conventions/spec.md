## ADDED Requirements

### Requirement: 项目分层规范
新 Go 服务 SHALL 使用 `kratoscli` 生成项目骨架，遵循标准分层结构：`/api`（proto 接口）、`/cmd`（启动）、`/internal/biz`（核心逻辑）、`/internal/service`（参数校验 + 格式转换）、`/internal/server`（gRPC/HTTP server）、`/internal/data`（数据库/Redis 操作）。

#### Scenario: 业务逻辑写在 data 层
- **WHEN** 数据库查询逻辑直接包含业务计算和规则判断
- **THEN** 应提示将业务逻辑移至 `biz` 层，`data` 层只负责数据访问

#### Scenario: 在 biz 层直接操作数据库
- **WHEN** `biz` 层代码直接调用 `db.Query(...)` 而非通过 `data` 层接口
- **THEN** 应提示通过 `data` 层 interface 访问数据库

---

### Requirement: 统一日志中间件
新 Go 服务 SHALL 使用洋葱统一日志中间件（`go-logger`）或 apisix 日志插件；通过 `kratoscli` 生成的项目默认已集成；不得自定义日志格式破坏统一索引字段。

#### Scenario: 自定义日志格式
- **WHEN** 服务使用自定义 logger 而非洋葱统一日志库
- **THEN** 应提示接入 `go-logger` 统一日志中间件

---

### Requirement: 链路追踪接入 OpenTelemetry
洋葱服务 SHALL 使用 OpenTelemetry 作为链路追踪协议；新服务 SHALL 接入 opentelemetry 链路；`go-logger` SHALL 升级到最新版本以打通链路日志；`tracing` 包 SHALL 升级到最新版本；不得引入其他链路追踪协议。

#### Scenario: 使用非 OpenTelemetry 的追踪库
- **WHEN** 代码中引入 `jaeger-client`、`zipkin` 等非 OpenTelemetry 追踪库
- **THEN** 应提示改用 OpenTelemetry SDK

---

### Requirement: 新技术引入必须审批
引入新技术/框架/工具前 SHALL 先查阅现有统一工具库是否有解决方案；确无现有方案时 SHALL 通过飞书审批流「新技术/方向立项申请」，审批通过后方可引入。

#### Scenario: 未审批直接引入新依赖
- **WHEN** PR 中引入了未在团队工具库中的新第三方库
- **THEN** 应提示是否已通过审批流，或现有工具库中是否有替代方案

---

### Requirement: 使用 gitlab-ci 进行 CI/CD
除非技术栈另有约定，服务 SHALL 使用 gitlab-ci；`kratoscli` 生成的项目默认集成 gitlab-ci，SHALL 不移除；YAPI token SHALL 单独申请配置。

#### Scenario: 项目缺少 .gitlab-ci.yaml
- **WHEN** 新服务仓库中无 `.gitlab-ci.yaml`
- **THEN** 应提示使用 `kratoscli` 生成或参考 Gitlab-CI 模版添加

---

### Requirement: 版本锁定规范
技术栈版本 SHALL 遵循以下强制约定：
- Go 大版本：`1.19`
- gRPC：`v1.63.2`
- Nacos：`v1.1.4`
- PostgreSQL：`12`
- Redis：`5.0`
- Kratos：`v2.7.3`
- RocketMQ：`4.x`
- Kafka：`2.2.2`
- protoc-gen-go：`v1.28.1`、protoc-gen-go-grpc：`v1.2.0`

版本升级 SHALL 提需求给对应技术栈负责人，不得自行升级。

#### Scenario: 自行升级框架版本
- **WHEN** PR 中将 Kratos 版本从 `v2.7.3` 升级为更高版本
- **THEN** 应提示通过架构团队确认后统一升级

---

### Requirement: Go 模块语义版本控制
技术栈项目 SHALL 采用语义版本控制规则（Semantic Versioning），遵循《Go 模块的语义版本控制规则》。

#### Scenario: 模块版本号不符合语义版本规范
- **WHEN** 模块版本号格式不符合 `vMAJOR.MINOR.PATCH`
- **THEN** 应提示遵循语义版本规范
