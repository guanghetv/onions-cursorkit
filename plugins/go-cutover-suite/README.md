# go-cutover-suite

面向 Go 接口切换场景的插件化工作流套件，包含批次调度、单路由切换编排、服务端调用方切换、网关暴露路由追踪、前端测试入口定位，以及 APISIX Admin API 并行路由发现。

## 包含的 Skills

- `go-cutover-batch`: 批量组织和顺序执行多条 cutover 任务
- `go-cutover-orchestrator`: 单条路由切换总编排
- `backend-service-switch`: 服务端调用方切换
- `sourcegraph-route-locator`: 跨仓定位候选调用方
- `gateway-route-tracer`: 网关与代理链路追踪
- `frontend-entry-finder`: 前端/客户端测试入口定位
- `apisix-admin-route-finder`: APISIX Admin API 路由发现

## 包含的 Commands

- `/go-cutover`: 单条路由切换统一入口，转入 `go-cutover-orchestrator`
- `/go-cutover-batch`: 批量切换统一入口，转入 `go-cutover-batch`

## 目录结构

```text
plugins/go-cutover-suite/
├── .cursor-plugin/plugin.json
├── README.md
├── commands/
│   ├── go-cutover.md
│   └── go-cutover-batch.md
└── skills/
    ├── go-cutover-batch/
    ├── go-cutover-orchestrator/
    ├── backend-service-switch/
    ├── sourcegraph-route-locator/
    ├── gateway-route-tracer/
    ├── frontend-entry-finder/
    └── apisix-admin-route-finder/
```

## 迁移约定

- 本插件以本机 `~/.cursor/skills` 中维护的版本为母本迁入。
- 旧的 OpenClaw 平行入口不再作为权威来源。
- 插件内文档与脚本不再依赖 `~/.cursor/skills/...` 绝对路径，统一使用插件内相对布局描述。

## 外部依赖

- `SOURCEGRAPH_URL`
- `GITLAB_URL`
- `SOURCEGRAPH_TOKEN`
- `GITLAB_TOKEN`
- `APISIX_ADMIN_KEY`

`sourcegraph-token` 目前仍作为外部独立能力使用，不打包进本插件。批处理脚本会优先按以下顺序查找 token 刷新脚本：

1. 环境变量 `SOURCEGRAPH_TOKEN_SCRIPT`
2. 插件内未来可能存在的 `skills/sourcegraph-token/scripts/get_token.py`
3. 本机默认位置 `~/.cursor/skills/sourcegraph-token/scripts/get_token.py`

## APISIX 策略

- 如果本次任务显式提供了 `apisixAdminURL` 或 `apisixAdminURLs`，插件会把这些 APISIX endpoints 当成与代码网关平级的外部暴露证据源。
- `gateway-route-tracer` 需要同时汇总代码网关证据和 APISIX 证据，而不是只在代码网关 dead-end 后才补查 APISIX。
- `frontend-entry-finder` 需要消费“代码网关结果 + APISIX 结果”的并集来推导前端功能入口。
- 如果本次任务没有提供任何 APISIX endpoints，则保持仅按代码网关追踪的旧行为。

## 使用说明

- 对话内执行：
  - 单条任务优先用 `/go-cutover`
  - 批量任务优先用 `/go-cutover-batch`
  - 也可以直接触发底层 `go-cutover-batch` 或 `go-cutover-orchestrator`
- 脚本执行：使用各 skill 目录下的 `scripts/*`
- 批次 JSON 模板与本地配置模板：见 `skills/go-cutover-batch/references/`
- 当任务显式提供 APISIX endpoints 时，前端入口定位前必须先完成所有已提供 APISIX sources 的检查与合并。

## 说明

这个插件当前不包含 rules，先以 `commands + skills` 套件形态交付，优先保证统一入口和迁移后的路径可移植。
