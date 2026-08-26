# GitNexus（核心：仓库与代码逻辑）

本 skill 的主路径。多数洋葱事故定位到 **哪个仓、哪条路由、哪个 handler、调用谁** 即可收束。GitNexus **没有** `env`；不要等运行时信封齐全才检索。

过洋葱门禁之后立刻用。非洋葱禁止 `list_repos` / `query`。

## 主路径

1. **`list_repos`** — 用服务名、`gitlab.yc345.tv` 路径、前端/后端仓名对齐已索引仓。多仓时后续 **必须带 `repo`**。未命中 → 缺口，问人仓名后再查，禁止假装已定位。
2. **`query`** — 症状 + 路由 + 错误文案 + 服务名。`task_context` 写本次要搞清的逻辑（如「下单接口超时，定位 handler 与下游调用」）。
3. **`route_map`** — 已知 HTTP path：handler 与调用方（含前端消费者）。
4. **`context`** — 对 handler 和调用链关键节点逐个查调用方/被调方；关键节点必须至少一次 `include_content=true`，用于核对函数签名、分支、参数传递、外部调用或错误映射。重名用 `file_path` / `kind` / `uid`，禁止默认选择第一个候选。
5. 可选：`cypher`（先读 schema）；`tool_map`（MCP/RPC 名）；`api_impact` / `impact` 只陈述结构依赖。
6. 可选：用户明确「我刚改了本地」才 `detect_changes`。

默认探索预算：最多保留 **两条候选路径**，最多对 **四个决定症状的关键节点** 调用 `context(include_content=true)`。预算内仍无法消歧时，评估为 `need_more_code`，列出候选与缺口，并只向用户索取一项新的仓库/路由/错误文案等识别输入。用户明确要求穷举时可以扩展，但交付中必须写明扩展范围。

跨仓：`repo` 可用 `@<group>` / `@<group>/<member>`。禁止排障时 `group_sync`、`rename`。

索引 stale：写明并提醒 `npx gitnexus analyze`，不把过期图当现网实现。

## 详细证据链（强制）

GitNexus 交付不是工具调用摘要。每个代码侧事实都必须能回溯到 **某次工具调用 + 返回的具体字段**。证据按 `GN-01`、`GN-02` 编号，后文逻辑对齐和假设必须引用编号。

### 最低完整度

只要 GitNexus 命中，代码证据至少包含：

1. **仓库身份**：`repo`、仓库 path、GitNexus 返回的 indexed date / last commit（有则原样写）；据此标记索引为「新鲜度未知」「可能 stale」或「未见 stale 提示」，不得写成现网版本。
2. **入口定位**：已知 HTTP path 时给出 method + path、handler 符号、文件、middleware、消费者；某字段未返回就明确写「GitNexus 未返回」，不得补猜。
3. **关键符号源码**：handler 及至少一个决定该症状的关键节点使用 `context(include_content=true)` 核对。摘录最小必要源码事实，例如函数签名、关键条件、参数映射、外部调用、超时值、错误转换或返回结构。源码里出现 token、密码、私钥、连接串或个人信息时，必须用 `***REDACTED***` 替换敏感字面量，只保留理解控制流所需的结构。
4. **逐边调用链**：每条边单列 `A --CALLS/FETCHES/HANDLES_ROUTE/...--> B`，同时写双方符号与文件、关系类型、`confidence` / `reason`（返回中有则保留）和来源证据编号。禁止把未验证的中间步骤压成 `A → … → Z`。
5. **歧义与缺口**：重名候选、低置信边、动态分派、反射、生成代码、跨仓未索引、找不到 terminal 都要列出；存在歧义时不得用确定语气。

若只命中仓库而未命中路由/符号，仍交付仓库证据和已执行查询，结论写「未定位」，不能输出一条臆测调用链。

### 证据卡格式

每次关键调用生成一张证据卡，不粘贴整段原始响应：

```markdown
### GN-01 <事实标题>
- tool: `route_map`
- invocation: `repo=<精确值>, route=<精确值>`（只写实际传入参数）
- observed:
  - route: `<method path；method 未返回则如实说明>`
  - handler: `<symbol>` (`<kind>`, `<file>:<line/range；未返回则省略行号>`)
  - middleware/consumer: `<GitNexus 返回项；无则写未返回>`
- supports: <本证据直接支持的单一事实>
- limits: <静态索引、stale、低 confidence、字段缺失或歧义>
```

`query` 证据卡还必须保留实际 `query`、`task_context`、`goal` 和命中的 process 名/排名；`context` 卡必须保留目标的 `uid`（有则写）、精确文件、incoming/outgoing 分类以及最小源码摘录。源码摘录必须来自 `include_content=true` 返回，不得凭符号名还原代码；摘录前必须检查并替换凭证、私钥和个人信息等敏感字面量。

### 调用链格式

```markdown
1. [GN-02] `POST /api/v1/example` --HANDLES_ROUTE--> `Submit` (`internal/http/submit.go`)
2. [GN-03] `Submit` --CALLS--> `Usecase.Create` (`internal/biz/example.go`)
3. [GN-04] `Usecase.Create` --CALLS--> `Repo.Save` (`internal/data/example.go`)
```

每一步随后补一句「代码里观察到什么」，并引用直接支持它的证据卡。若边只由 process 排名提示、尚未被 `context` / `route_map` 核实，标为「候选边」，不能混入已核实链。

### 事实、推断和运行时必须分栏

- **代码事实**：GitNexus 明确返回的 route、symbol、file、relation、source content。
- **静态推断**：基于代码事实的条件性解释，必须引用 `GN-*`，使用「若执行到该分支」「代码结构显示」。
- **运行时事实**：只能来自已钉死单一 `env` 的运行时 MCP；GitNexus 证据卡不得写「线上已调用」「本次请求经过」「prod 正在运行该 commit」。

不允许只写「GitNexus 显示调用了某服务」。必须展示入口、逐边关系、关键源码事实、工具调用参数和局限。

## 证据后评估（强制）

`GN-*` 证据卡与逐边调用链写完后，**必须**给出代码侧置信度与初步结论，再决定是否停在 GitNexus 阶段。没有评估不得直接加载运行时，也不得空交付。

评估只覆盖 **静态代码**。禁止把初步结论写成该 `env` 现网已发生，禁止使用「根因是」。

### 置信度

只取 `high` / `medium` / `low`。按表取最低一档，不得凭感觉上调。

| 档 | 必须同时满足 |
|----|----------------|
| `high` | 仓已对齐；入口（路由/handler 或等价符号）已核实；关键节点有 `include_content=true` 源码摘录；症状能对上一段具体代码事实（超时值、错误映射、过滤条件、空返回分支、下游调用等）；已核实链无未解释歧义；无「可能 stale」且关键边非低 confidence |
| `medium` | 仓与入口已对齐，但缺一个关键节点核实、存在竞争分支、索引可能 stale，或症状只对上调用结构尚未对上决定性语句 |
| `low` | 仅命中仓、路由/符号未定位、重名未消歧、关键边全是候选边、无源码摘录，或症状与已观测代码对不上 |

缺最低完整度任一项时，置信度不得标 `high`。标 `high` 必须列出支撑它的 `GN-*` 编号。

### 初步结论

固定四行，写在证据与逻辑对齐之后：

```markdown
## 代码侧评估
- 置信度: `high` | `medium` | `low`（取最低档的原因：…）
- 初步结论: 代码结构显示 … [GN-xx][GN-yy]。若请求走到该路径，与症状相符的点是 …。
- 未证实: 该 env 现网是否发生、流量/错误量、某条请求的实际耗时或返回。
- 收束: `stop`（代码已足够）| `need_runtime`（要验证现网）| `need_more_code`（继续 GitNexus 或问仓/路由）
```

口径：

- **`high` + `stop`**：多数场景到此交付；除非用户明确要现网量/某条请求/库表，否则不加载运行时。
- **`medium`**：可以交付初步结论，但必须写清缺哪张证据；下一步只选一个：补 `context`/`route_map`，或钉 `env` 验证现网。
- **`low`**：初步结论只能是「未定位」或并列候选（最多两个，均引用 `GN-*`）；禁止单点断言。下一步优先补代码证据，不要用运行时猜测代码。

「初步结论」是对已引用证据的压缩判断，不是新事实。结论里出现的符号、文件、超时值、分支条件必须能在某张 `GN-*` 卡的 `observed` 里找到。

## 何时才加载运行时

代码侧评估为 `high` + `stop` 后，**默认停**。仅在评估为 `need_runtime`，或用户要验证现网时，钉 `env` 再开运行时 MCP（见 [intake.md](intake.md)、[symptom-routes.md](symptom-routes.md)）：

- 要确认该逻辑在 **某环境** 是否正在发生（量、错误、延迟）
- 要一条具体请求（`trace_id` / 日志）
- 要核对存储里的实际数据（Archery 只读）
- 用户明确要求看 prod/stage 指标或日志

未钉 `env` 禁止 metrics/trace/logs/archery。钉死后仍 **只开需要的域**，禁止四域扫一遍。

## 交付口径

| GitNexus（主） | 运行时（按需） |
|----------------|----------------|
| `GN-*` 证据卡、逐边调用链、关键源码事实、代码侧置信度与初步结论 | 哪个 `env`、哪个时间窗实际观测 |
| 未索引 ≠ 线上没接口 | `no_data` ≠ 服务健康 |

代码节写「代码里这样走」并给出代码侧初步结论，每句话引用 `GN-*`；不要写成「所以线上根因是某函数」。
