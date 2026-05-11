---
name: tls-route-traffic-compare
description: 对比任意两个服务在火山 TLS 中按 route/method 聚合的生产流量，支持 route 归一化、assisted 聚合候选分析、CSV 导出和飞书 Base 写入。
---

# /tls-route-traffic-compare

TLS 路由流量对比统一入口。激活后，优先读取并遵循 `skills/tls-route-traffic-compare/SKILL.md`，不要让用户手工记忆脚本路径或底层 skill 名称。

## 必须做的事

1. 读取并遵循 `skills/tls-route-traffic-compare/SKILL.md`。
2. 确认或补齐环境、A 服务、B 服务、时间范围和输出目标。
3. 当用户只给 service 而没有 namespace 时，只能展示 topic 候选并等待确认。
4. 写入飞书 Base 前必须先预览总行数、样例行、assisted 规则影响和最终字段结构。
5. 如果 candidate report 非空，按 skill 要求启动只读 subagent 分析候选簇；脚本只应用显式规则。
6. 所有火山 AK/SK 必须从环境变量读取，不要要求用户粘贴密钥。

## 典型输入

```text
prod teacherschool/teacher vs teacherschool/teacher-school 最近24小时 写入飞书 Base
```

## 必要输入

- `env`：默认支持 `prod`、`stage`
- `aService`：A 侧 `namespace/service`
- `bService`：B 侧 `namespace/service`
- `timeRange`：例如 `15m`、`24h`、最近 24 小时
- `outputTarget`：预览、CSV、飞书 Base

## 不要做的事

- 不要绕过 skill 自行发明另一套 TLS 查询流程。
- 不要在未预览和未确认时清空或写入飞书 Base。
- 不要把 candidate report 的模型判断隐式写入脚本；必须整理成显式 rules JSON 后再传给脚本。
- 不要把 `path`、`uri` 自动当作 `route` 字段兜底。
