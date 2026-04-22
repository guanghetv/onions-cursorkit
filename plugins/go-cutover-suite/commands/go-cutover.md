---
name: go-cutover
description: 单条 Go 路由切换入口。收集 old/new route、method、branch 与服务标识后，进入 go-cutover-orchestrator 执行全链路 cutover。
---

# /go-cutover

单条 Go 路由切换统一入口。激活后，优先进入 `go-cutover-orchestrator`，而不是让用户手工记忆底层 skill 名称。

## 必须做的事

1. 读取并遵循 `skills/go-cutover-orchestrator/SKILL.md`。
2. 先确认或补齐 `oldRoute`、`newRoute`、`method`、`branch`、`oldServiceName`、`newServiceName`、`oldNamespace`、`newNamespace`、`workspaceRoot`。
3. 若 `oldServiceHint` 或 `newServiceHint` 缺失，但 service name 与 namespace 已齐全，则按 skill 约定自动推导。
4. 若 `gatewayRepos`、`apisixAdminURL`、`apisixAdminURLs`、`apisixAdminKeyEnvVar` 未提供，按 orchestrator 里的默认策略继续。
5. 输入足够后，直接按 `go-cutover-orchestrator` 的流程执行，不要再要求用户重新切换到 skill 名调用。

## 何时使用

- 用户要切一条具体接口到 Go 服务
- 用户说“切调用”“路由切换”“把老接口切到 go”“梳理测试入口”
- 用户已经给出了单个 old/new route，想直接开始执行

## 不要做的事

- 不要把它当成批处理入口
- 不要绕过 `go-cutover-orchestrator` 自行发明另一套流程
- 不要在普通非阻塞歧义上频繁停下来等待用户确认
