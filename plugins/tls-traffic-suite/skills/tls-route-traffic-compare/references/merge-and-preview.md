# 合并与预览

## 合并规则

将 A/B 两侧查询结果先做 route 归一化，再按 `normalized_route + method` 做 full join：

```text
key = normalized_route + "\t" + lower(method)
```

默认归一化规则：

- 去掉 `/teacher-school` 服务前缀，例如 `/teacher-school/admin-room/base` -> `/admin-room/base`。
- 将单段变量统一为 `{param}`，例如 `:id`、`:studentId`、`{id}`、`{studentId}` -> `{param}`。
- 可选 assisted 归一化会在用户确认后应用显式规则，例如 `/rooms/refs/*/search` -> `/rooms/refs/{param}/search`。

面向用户的默认输出列使用实际服务名：

```text
路由地址 | method | <A服务名>流量 | <B服务名>流量 | <A服务名>有流量 | <B服务名>有流量
```

例如：

```text
路由地址 | method | teacherschool/teacher流量 | teacherschool/teacher-school流量 | teacherschool/teacher有流量 | teacherschool/teacher-school有流量
```

如果某一侧没有该 `normalized_route + method`，对应流量填 `0`，对应 `有流量` 为 `false`。如果同一侧多个原始 route 归一到同一个 key，该侧流量会累加，`路由地址` 输出归一化后的 route。

## 风险提示

归一化可能把多个原始 route 合并到同一输出行。默认规则只处理完整路径段变量和明确的 `/teacher-school` 前缀，不对普通文本段做模糊匹配。若结果看起来异常，应回到 TLS 原始聚合结果检查 raw route。

assisted 归一化用于处理 TLS 中已经落成真实值的字面量路由，例如 `/rooms/refs/703A/search`。它不是脚本里的模型推理：脚本只生成 candidate report 并应用明确传入的规则；Cursor 主 Agent 和只读 subagent 在运行期分析候选质量。

写入 CSV 或飞书 Base 前，assisted preview 必须展示：

- 建议规则，例如 `/rooms/refs/*/search` -> `/rooms/refs/{param}/search`。
- raw route 映射，例如 `/rooms/refs/703A/search`、`/rooms/refs/Fafafa54/search`。
- 涉及的 method。
- 应用后 A/B 流量如何累加。
- 风险等级，特别是是否可能误伤固定语义路由。

高风险规则必须等用户确认后再应用。低风险规则也要在写入飞书前展示影响范围；用户未确认时保持确定性归一化输出。

## 预览规则

写入飞书 Base 前必须先预览：

- 总行数
- 前若干条样例行
- A-only / B-only 的数量（如脚本提供）
- 实际服务名流量列与 `有流量` boolean 列

用户确认前，不要执行任何持久化写入。

## CSV 规则

CSV 使用 UTF-8，列名保持：

```text
路由地址,method,<A服务名>流量,<B服务名>流量,<A服务名>有流量,<B服务名>有流量
```

CSV 中 boolean 值输出为小写 `true` / `false`。
