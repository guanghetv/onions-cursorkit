# agent-context

洋葱排障与可观测性 skills，正文单一源为 [agent-context](https://gitlab.yc345.tv/backend/agent-context) 仓库的 `skills/`。本插件把已落地 skill 与 slash command 发布到 Cursor 市场 **onions-plugins**。

## 包含的 Skills

- `onion-systematic-debugging`：洋葱全链路排查。GitNexus 定位仓库与代码；metrics / trace / logs / Archery 仅按需且必须单一 `env`
- `metrics-query`：`mcp-metrics` 意图地图与三刀取数
- `logs-query`：`mcp-logs` TLS 四刀取证
- `archery-query`：`mcp-archery` 只读取证与受控工单确认

`trace-query` 尚未落地；查链路时按已注册的 `mcp-trace` 五刀调用。

## 包含的 Commands

- `/onion-systematic-debugging`：显式启动全链路排查，转入 `onion-systematic-debugging`

## 目录结构

```text
plugins/agent-context/
├── .cursor-plugin/plugin.json
├── README.md
├── mcp.json
├── commands/
│   └── onion-systematic-debugging.md
└── skills/
    ├── archery-query/
    ├── logs-query/
    ├── metrics-query/
    └── onion-systematic-debugging/
```

## 外部依赖

- **必需（场景 skill 主路径）**：GitNexus MCP（`list_repos` / `query` / `context` / `route_map`），且目标仓已索引
- **按需（运行时）**：插件 `mcp.json` 中的 `mcp-metrics`、`mcp-trace`、`mcp-logs`、`mcp-archery`
- **Archery**：预发/生产需要账号 headers；测试环境 `mode=direct` 的部分能力不要求 headers。请在 Cursor MCP 配置中填入真实凭证，不要把明文密码提交进仓库

## 使用说明

安装本插件后，在对话中输入：

```text
/onion-systematic-debugging 服务 teacher-desk 的 /api/lesson 接口返回空数据，请定位仓库和代码调用链
```

单域查询可直接触发 `metrics-query`、`logs-query`、`archery-query`。

勿绕过 MCP 直打 VictoriaMetrics / Jaeger / Archery / 火山 TLS。服务器与 skill 均不输出现网根因结论。
