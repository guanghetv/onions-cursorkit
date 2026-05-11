---
name: tls-route-traffic-compare
version: 1.0.0
description: "对比任意两个服务在火山 TLS 中按 route/method 聚合的生产流量，并生成带实际服务名和流量布尔值的六列结果。Use when comparing service traffic during route migration, 灰度切流, Go 重构, endpoint migration, or when the user mentions 火山 TLS route traffic compare."
metadata:
  requires:
    bins: ["python3"]
---

# TLS Route Traffic Compare

用于对比两个服务在火山 TLS 中的路由流量。典型输入：

```text
prod teacherschool/teacher-school vs xxxx/new-service 最近24小时
```

## 前置条件

- 火山凭证必须来自环境变量：`VOLCENGINE_ACCESS_KEY_ID`、`VOLCENGINE_SECRET_ACCESS_KEY`、`VOLCENGINE_REGION`。
- 不要在聊天、终端输出、文档、飞书 Base 中打印 AK/SK。
- topic 命名规则：`{namespace}-{service}`。
- 默认环境映射：`prod -> prod-vke`、`stage -> stage-vke`。
- 默认 TLS SQL：

```sql
status:>=200 | SELECT route,method,count(*) pv GROUP BY route,method ORDER BY pv DESC LIMIT 999
```

## 工作流

1. 解析用户输入，拿到环境、A/B 的 `namespace/service`、时间范围和输出目标。
2. 使用 `scripts/tls_route_traffic.py discover-topic` 验证 topic。
3. 使用 `scripts/tls_route_traffic.py query` 查询 A/B 服务流量。
4. 使用 `scripts/tls_route_traffic.py compare` 先归一化 route，再做 `normalized route + method` full join。
5. 如果用户要求更智能聚合，或预览中出现大量疑似同模板的字面量 route，先生成 assisted candidate report。
6. candidate report 非空时，启动只读 subagent 实时分析候选簇，得到建议规则和风险说明。
7. 先预览总行数、样例行、assisted 规则影响和 raw route 映射；用户确认前不要写飞书 Base。
8. 如需写飞书 Base，先使用已安装的 `lark-shared` / `lark-base` 能力或 `lark-cli base +...` reference，再按 Base 字段结构写入。

## 路由归一化

合并前默认会对 route 做迁移对比归一化：

- 去掉 `/teacher-school` 服务前缀，例如 `/teacher-school/admin-room/base` 归一为 `/admin-room/base`。
- 将单段变量统一为 `{param}`，例如 `:id`、`:studentId`、`{id}`、`{studentId}` 都归一为 `{param}`。
- 如果同一侧多个原始 route 归一到同一个 `normalized route + method`，流量会累加。

最终 `路由地址` 列输出归一化后的 route。

## Assisted 归一化

当 TLS route 中出现真实字面量参数时，例如：

```text
/rooms/refs/703A/search
/rooms/refs/G411626201508261231/search
/rooms/refs/ex2026028Fafafa62/search
```

不要全局把所有字面量段都当变量。应先使用 candidate report 找出保守候选：

```bash
python3 scripts/tls_route_traffic.py compare \
  --a a.json \
  --b b.json \
  --candidate-report
```

如果 candidate report 非空，主 Agent 应启动只读 subagent，传入：

- candidate groups 和 raw route 样本。
- 当前确定性规则：剥离 `/teacher-school`、`:id` / `{id}` -> `{param}`。
- 误伤示例：`/users/me`、`/schools/password`、`/new-level/tasks` 不应被盲目变量化。
- 输出契约：最终写 `路由地址`、`method`、`<A服务名>流量`、`<B服务名>流量`、`<A服务名>有流量`、`<B服务名>有流量` 六列。
- 用户目标：判断迁移前后流量是否对齐，不是生成新的路由表。

subagent 输出只作为建议。主 Agent 需要把可采纳建议整理成显式规则 JSON，例如：

```json
[
  {
    "pattern": "/rooms/refs/*/search",
    "replacement": "/rooms/refs/{param}/search",
    "risk": "low",
    "examples": ["/rooms/refs/703A/search"]
  }
]
```

再用显式规则重新 compare：

```bash
python3 scripts/tls_route_traffic.py compare \
  --a a.json \
  --b b.json \
  --assisted-rules assisted-rules.json \
  --a-name teacherschool/teacher \
  --b-name teacherschool/teacher-school
```

Python 脚本只生成候选并应用显式规则，不直接启动 subagent，也不把模型推理隐式写入输出。

## 命令

检查环境变量：

```bash
python3 scripts/tls_route_traffic.py validate-env
```

发现 topic：

```bash
python3 scripts/tls_route_traffic.py discover-topic \
  --env prod \
  --service teacherschool/teacher-school
```

查询单个 topic：

```bash
python3 scripts/tls_route_traffic.py query \
  --topic-id <topic-id> \
  --time-range 24h
```

合并 A/B 查询结果并预览：

```bash
python3 scripts/tls_route_traffic.py compare \
  --a a.json \
  --b b.json \
  --a-name teacherschool/teacher \
  --b-name teacherschool/teacher-school
```

生成 assisted candidate report：

```bash
python3 scripts/tls_route_traffic.py compare \
  --a a.json \
  --b b.json \
  --candidate-report
```

导出 CSV：

```bash
python3 scripts/tls_route_traffic.py compare \
  --a a.json \
  --b b.json \
  --a-name teacherschool/teacher \
  --b-name teacherschool/teacher-school \
  --csv \
  --output route-traffic.csv
```

## 输出列

默认面向用户输出六列，流量列使用实际服务名：

```text
路由地址
method
<A服务名>流量
<B服务名>流量
<A服务名>有流量
<B服务名>有流量
```

例如 A 为 `teacherschool/teacher`，B 为 `teacherschool/teacher-school` 时：

```text
路由地址
method
teacherschool/teacher流量
teacherschool/teacher-school流量
teacherschool/teacher有流量
teacherschool/teacher-school有流量
```

`<服务名>有流量` 是 boolean 值，规则为对应流量 `> 0`。缺失一侧流量时填 `0`，对应 boolean 为 `false`。`method` 统一转小写。`路由地址` 使用归一化后的 route。

如果希望列名更短，可使用 `--a-display-name` 和 `--b-display-name` 覆盖展示名。未传 `--a-name` / `--b-name` 或 display name 时，脚本保留旧四列输出用于兼容历史调用。

## 失败处理

- topic 找不到：停止并提示检查环境、namespace 或 service。
- 缺少 `status`、`route`、`method` 字段：停止，不要自动用 `path` 或 `uri` 推断 route。
- TLS 查询超时：建议缩短时间范围。
- Base 未确认写入：只预览或导出 CSV，不创建、不清空、不更新记录。

## 参考资料

- 输入格式：[`references/input-format.md`](references/input-format.md)
- TLS 查询：[`references/tls-query.md`](references/tls-query.md)
- 合并与预览：[`references/merge-and-preview.md`](references/merge-and-preview.md)
- 飞书 Base 输出：[`references/base-output.md`](references/base-output.md)
