# Report Contract

所有 Markdown 报告文档必须统一使用中文：

- 中文标题
- 中文字段名
- 中文说明文字
- 中文总结和风险提示

JSON 产物保持机器可读，可以继续使用英文键名。

每次路由切换任务的报告目录：

```text
~/work/_ai_reports/go-cutover/<timestamp>/
```

必需文件：

- `summary.md`
- `route-locator.md`
- `backend-changes.md`
- `gateway-trace.md`
- `frontend-entrypoints.md`
- `artifacts/route-locator.json`
- `artifacts/backend-changes.json`
- `artifacts/gateway-trace.json`
- `artifacts/frontend-entrypoints.json`
- `artifacts/execution.json`

## `summary.md`

内容要求：

- 重构前路由
- 重构后路由
- 请求方法
- 分支名
- 老服务名称
- 新服务名称
- 老服务线索
- 新服务线索
- 本地工作目录
- 已修改的服务端仓库
- Merge Request 状态与链接
- 最终对外暴露路由
- 所有已检查网关来源及其状态
- 已确认的前端入口
- 阻塞项与后续关注点
- 异常简述

## `route-locator.md`

内容要求：

- 老服务参考仓库候选
- 网关或代理仓库候选
- 其他后端调用方候选
- 前端或客户端项目候选
- 每个候选与 `oldServiceName` / `newServiceName` 的关系
- 保留该候选的原因和置信度

## `backend-changes.md`

内容要求：

- 仓库名
- 分支名
- 远端分支状态
- 仓库角色，例如 `gateway`、`backend-caller`
- 老服务名称
- 新服务名称
- 老服务线索
- 新服务线索
- 改动文件
- 新旧接口对比结论
- 老调用到新调用的映射
- commit 信息
- push 状态
- Merge Request 状态
- Merge Request 链接
- 验证命令和结果
- 回归风险

## `gateway-trace.md`

内容要求：

- 从内部调用到对外路由的链路
- 每一步对应的仓库和文件
- 断点、歧义点或未确认点
- 如果存在多个网关来源，必须分别列出每个来源的结果，不得只保留第一个命中
- 如果使用了 APISIX Admin API，要明确写出：
  - 查询入口
  - 网关来源标识
  - 使用的匹配线索
  - 结果是 `confirmed-by-apisix` 还是 `speculative-by-apisix-route-family`

## `frontend-entrypoints.md`

使用本插件内 `skills/frontend-entry-finder/references/entrypoint-report-format.md` 中定义的结构。
每个前端入口候选都必须来自本地仓库证据。
如果项目是本次 clone 下来的，要明确写出来。
报告必须以中文的“功能流程简述”开头。
这段内容必须一步一步说明用户如何走到会触发接口的页面或动作。

## JSON Artifacts

每个 JSON 产物都应保持机器可读，并包含：

- `oldRoute`
- `newRoute`
- `method`
- `generatedAt`
- `items`

`artifacts/execution.json` should also include:

- `branch`
- `oldServiceName`
- `newServiceName`
- `oldServiceHint`
- `newServiceHint`
- `workspaceRoot`
- `envChecks`
- `reposTouched`
- `reposCloned`
- `remoteBranches`
- `commitsCreated`
- `pushesCompleted`
- `mergeRequests`
- `status`
- `apisixUsed`
- `gatewaySources`

当 `status` 不是 `already_cut_over`、`no_code_change`、`noop` 这类“无代码改动成功态”时，还必须满足：

- `commitsCreated` 非空，能证明本次任务已创建 commit
- `pushesCompleted` 非空，能证明本次任务已完成 push
- `mergeRequests` 包含每个改动仓库的 Merge Request 结果，至少要有：
  - `repo`
  - `targetBranch`，默认应为 `dev`
  - `status`，例如 `created`、`exists`、`blocked`、`creation_link_only`
  - `url`，优先填写已创建 MR 的直达链接；若自动创建失败，则填写可直达的创建链接
