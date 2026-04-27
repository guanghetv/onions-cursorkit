# Stage3 Subagent 调度模型

这个文件定义 `telemetry:instrument-from-csv` 在真正执行时，调度器与单仓 subagent worker 的职责边界。

## 目标

把第三阶段稳定收敛成：

1. 调度器负责批量视角的筛选、计划、并发控制和总表写回
2. 单仓执行由真正的 subagent worker 完成
3. 单仓失败只阻塞当前仓，不拖住整批
4. 总 CSV 永远由调度器串行写入，避免并发覆盖
5. 默认持续 drain，直到没有可执行候选为止

## 调度器职责

调度器负责：

- 读取 `telemetry-audit-results.csv`
- 过滤候选行
- 生成 `instrument-manifest.json`
- 生成计划文档
- 为每个候选仓运行 `prepare-repo`
- 控制 worker 并发数
- 接收 worker 返回 JSON
- 把单仓结果落到 `instrument-worker-results/`
- 串行执行 `merge-json` 回填总表
- 汇总整次 drain 执行结果

调度器不负责：

- 自己直接改业务仓代码
- 自己直接跑单仓验证并判定“已提 MR”
- 并发写 `telemetry-audit-results.csv`

## 单仓 Subagent Worker 职责

单仓 worker 负责：

- 只处理一个候选服务
- 只在该服务的 `本地仓库路径` 内工作
- 读取当前行和单仓计划文档
- 按 `适用且缺失` 改代码
- 对 `待确认` 项只写计划/备注，默认不自动落代码
- 跑最小必要验证
- commit / push
- create 或 reuse MR
- 返回严格 JSON 结果

单仓 worker 不负责：

- 修改总 CSV
- 重新筛整批候选
- 同时处理多个仓库

## 推荐执行顺序

1. `plan` 生成 manifest、计划文档、统一分支名和建议 worker 并发
2. 调度器只取当前 wave 的 `dispatch_items`
3. 对目标项运行 `prepare-repo`
4. 只有 `prepare-repo` 成功且 `本地仓库路径` 真实存在时，才允许把该目标项加入 worker 队列
5. 为每个已准备成功的目标项启动一个 `generalPurpose` subagent
6. subagent 返回严格 JSON
7. 调度器把该 JSON 写到 `instrument-worker-results/<service>__<namespace>.json`
8. 调度器调用 `merge-json` 回填总表
9. 调度器重新执行 `plan`
10. 直到 `candidate_count = 0` 才结束

## Prepare Repo 门禁

`prepare-repo` 是 worker 派发前的硬门禁：

- 如果 `prepare-repo` 返回非零退出码，调度器必须把该服务写成 `执行状态 = 阻塞`，备注保留真实的 prepare 错误输出。
- 如果 `prepare-repo` 成功返回，但 `本地仓库路径` 不存在或不是 Git 仓库，调度器必须把该服务写成 `执行状态 = 阻塞`，备注写明本地仓校验失败。
- 上述两种情况都不能继续启动单仓 worker。
- 不允许用 worker 的 cwd 启动失败（例如 `No such file or directory: .../writable-repos/...`）覆盖原始 prepare 失败原因。
- 当前 wave 中 prepare 失败的仓只阻塞自身，其余 prepare 成功的仓继续派发。

## 并发建议

- 默认并发 `2-4`
- 永远不要让多个 worker 同时写 `telemetry-audit-results.csv`
- 如果某批仓库依赖安装或验证特别重，可以先降到 `1-2`

## 失败处理

- 单仓技术失败：返回 `执行状态 = 阻塞`
- 验证失败但代码已改完：返回 `验证状态 = 验证失败`，不要伪造 `验证通过`
- 已存在打开中的 MR：优先复用，并在 `执行备注` 说明
- 若 MR 创建失败但代码已推送，返回 `执行状态 = 阻塞`，由后续人工处理，不要在下一轮重复派发
- MR 创建应依次尝试 GitLab API、Git push option、`glab` fallback；如果 `glab` 已安装登录但返回 `403 insufficient_scope`，备注应写权限不足，而不是“未安装 glab”

## 返回格式

worker 最终返回建议为严格 JSON 对象，至少包含：

- `服务名称`
- `命名空间`
- `统一分支名`
- `计划文档路径`
- `执行状态`
- `验证状态`
- `Commit哈希`
- `MR地址`
- `执行备注`

## Worker 输出解析门禁

调度器接收 worker 输出时，不应只做一次 `json.loads(raw_result)`：

- 如果使用 Cursor `agent -p --output-format json` 作为 worker，先解析 CLI 外层 JSON，再读取外层的 `result` 字段。
- `result` 字段可能混入进度文字，例如“正在读取计划文档...”，调度器必须从其中抽取最后一个包含 `服务名称 / 命名空间 / 执行状态` 的 JSON 对象。
- 支持两种常见形式：裸 JSON 对象，以及 Markdown 代码块 ```json ... ```。
- 机械层可使用 `instrument_from_csv.py parse-worker-output --input-file <raw-output-file>` 进行抽取。
- 只有在完全找不到可用 JSON 对象时，才允许标记为 `执行状态 = 阻塞`，备注写明“无法解析 worker 输出”。
- 不允许把“worker 已返回可用 JSON，但前面带了自然语言进度”误判成真实执行阻塞。
