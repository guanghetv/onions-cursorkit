---
name: go-cutover-batch
description: 批量 Go 路由切换入口。进入 go-cutover-batch，组织批次级默认值与任务列表，并按顺序执行；单任务若显式提供 APISIX endpoints，则并行检查所有 APISIX 外部暴露链路。
---

# /go-cutover-batch

批量 Go 路由切换统一入口。激活后，优先进入 `go-cutover-batch`，用于组织批次参数、任务列表与顺序执行。

## 必须做的事

1. 读取并遵循 `skills/go-cutover-batch/SKILL.md`。
2. 先判断用户意图属于哪一类：
   - 创建新批次
   - 快速创建批次
   - 执行已有批次
   - 查看或解释批次输入格式
3. 组织批次级默认值：`oldServiceName`、`newServiceName`、`oldNamespace`、`newNamespace`、`SOURCEGRAPH_URL`、`GITLAB_URL`、`workspaceRoot`。
4. 组织任务级字段：`oldRoute`、`newRoute`、`method`、`branch`。
5. 如果某条任务显式提供了 `apisixAdminURL` 或 `apisixAdminURLs`，该任务在进入前端入口定位前，必须把所有已提供 APISIX endpoints 全部检查一遍，并与代码网关结果合并。
6. 如果用户是在当前对话中直接执行批量任务，按 `go-cutover-batch` 中的顺序执行规则推进，不要默认把工作转成别的命令名或并行处理。

## 何时使用

- 用户要一次切多条接口
- 用户说“创建批次”“执行批次”“批量切换接口”
- 用户要批量报告、状态跟踪、重试或汇总

## 不要做的事

- 不要把单条 cutover 硬塞进批处理流程
- 不要并行执行多个任务
- 不要因为某条任务的代码网关已经找到 outward route，就跳过该任务显式提供的 APISIX endpoints
- 不要绕过 `go-cutover-batch` 自己拼一套批次协议
