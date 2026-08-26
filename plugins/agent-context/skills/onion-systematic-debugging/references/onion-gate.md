# 洋葱门禁

本 skill 只服务 **洋葱（公司）技术栈** 事故。判定看 **这次要查的服务是不是洋葱线上/预发/测试**，不看当前 IDE 文件夹是不是 git 仓库。

在 **任何 MCP 调用之前** 执行（含 GitNexus）。未通过则结束，不要取证。

## 通过（满足任一即可继续；GitNexus 不必先有 env）

- 用户明确：洋葱 / 公司线上 / `gitlab.yc345.tv` 服务，或给出公司 K8s `namespace` + 服务名 + `env`。
- 当前或目标仓库 `go.mod` / `package.json` 依赖 `gitlab.yc345.tv/`。
- 已在用公司 MCP（`agent-context.yc345.tv` 或本机 `mcp-metrics` / `mcp-trace` / `mcp-logs` / `mcp-archery` / GitNexus）查 `yc_*`、公司 Jaeger、TLS topic 或已索引的 `gitlab.yc345.tv` 仓。
- 洋葱客户端请求洋葱后端 API（前端仓库无 `go.mod` 也可以）。

## 拒绝（满足任一即跳过）

- 个人项目、GitHub / 其他 GitLab、无 `yc345` 依赖，且问题是本地编译、单测、纯前端白屏且 **Network 无公司 API**。
- 要用 Datadog、自建 Prometheus、或 `curl` 非公司平台代替本仓库 MCP。
- 通用代码 bug、与洋葱可观测/DBA 基建无关 → 用 systematic-debugging，不用本 skill。

证据矛盾（当前仓库是开源，但用户明确要查洋葱线上某某服务）：**以事故身份为准**，继续；并在信封里写清目标服务，不要用当前开源仓的模块名去查平台。

## 跳过话术（原样输出后结束）

```text
非洋葱技术栈，跳过 onion-systematic-debugging。
原因：<无 gitlab.yc345.tv / 本地单测 / 无公司 API 请求 / …>
请用 systematic-debugging 或该项目自己的工具；禁止用公司 mcp-metrics/logs/trace/archery 与 GitNexus 查询。
```

不要输出层次取证表，不要调用运行时 MCP 或 GitNexus。
