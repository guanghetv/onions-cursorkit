# Topic 命名与 `topic_id`

## 必须用 ID

`logs_query` 的 `topic_id` 是 TLS **主题 ID**（平台 UUID 形态字符串），**不是**控制台显示名。

正确做法：

1. 在目标 `env` 上调用 `logs_list_topics`
2. 在返回的 topic 列表里按名称匹配工作负载
3. **抄写**列表里的 id 字段到 `logs_query`

禁止：

- 臆造或手写「看起来像」的 UUID
- 用服务逻辑名、K8s Deployment 名直接当 `topic_id`
- 跨 env 复用上次抄到的 id（MCP **不**校验 topic 是否属于该 env 的 project）

## 常见命名形态

采集侧 topic **显示名**常见为：

```text
namespace-servicename
```

例如 namespace `teacherschool` 下的 service `teacher-desk`，优先构造完整候选：

```text
teacherschool-teacher-desk
```

连字符可以是 service 名的一部分，不能把 `teacher-desk` 擅自拆成 namespace `teacher` + service `desk`；逻辑 env `prod` 也不等于 namespace。

## 发现顺序

1. 用户已给 `topic_id`：直接使用，不再猜 topic 名。
2. 用户已给完整 topic 名：调用 `logs_list_topics(env, topic_name=完整名称)` 验证并抄 ID。
3. 否则先补齐 `namespace` 与 `service_name`，再用 `topic_name=namespace-service_name` 精确查。
4. 精确查无结果时，用 `fuzzy_search_key=service_name` 查候选。
5. 候选超过一个时列出名称与 ID，请用户确认；不得按子串相似度自动选择。
6. 大目录需要翻页时传 `page_number` / `page_size`，`page_size` 不超过 100。

匹配不到就扩大过滤条件、翻页或问人类，不要猜 ID。

## 与 identity 的关系

本切片 **没有** `identity.Service` → topic 自动映射。服务别名、多环境同名冲突的归一化是 follow-up。在此之前：

- 用人类给出的服务 / 命名空间线索去 list 结果里找
- 找到后只传递平台 `topic_id`

## `project_id` 不进 skill

`stage` / `prod` 的 `project_id` 在服务端 YAML；`logs_list_topics` 会按 `env` 注入。  
`logs_list_projects` 仅用于「配置里还没有该 env 的 project」时认出项目，再由人类改配置。

**不要**把 `project_id` 写进本 skill、会话记忆或 Client 配置当注册表。

## `test` 环境

`test` 会出现在 `logs_available_servers`，但 `query_ready=false`。  
对 `test` 调 `list_topics` / `query` 会 `denied` 且不访问 TLS——这是预期，不是平台故障。
