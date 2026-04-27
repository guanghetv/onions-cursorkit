# 单仓 Worker 契约

这个文件定义 `telemetry:audit-from-csv` 内部单仓 worker 的职责与返回格式。

## Goal

对单个已确认仓库做只读 telemetry 审计，并返回一条可直接写入 `telemetry-audit-results.csv` 的标准结果。

## Input

worker 至少接收这些输入：

- `服务名称`
- `命名空间`
- `业务归属`
- `编程语言`
- `仓库地址`
- `仓库名`
- `本地仓库路径`
- `分支`

可选补充：

- `telemetry_instrument_reference`
- `repo_resolution_row`

默认前提：

- 这一层只处理 `编程语言 = Go / Node` 的仓库
- `Python / 其他 / 空语言` 默认由调度器直接写成 `跳过`，不进入 worker

## Readonly Rules

- 只读检查，不改代码
- 不创建分支、不提交、不提 MR
- 不重搜 GitLab
- 不读整份批量 CSV，只关心当前仓库

## Check Focus

worker 必须优先参考本地 vendored 规范：

- `references/framework-inference.md`
- `references/telemetry-instrument.md`
- `references/telemetry-audit-checklist.md`

在正式判断 telemetry 缺失前，先做一步：

- 先读取飞书透传下来的 `编程语言`
- 根据入口文件、依赖、中间件和目录结构，输出 `推测框架`
- 同时输出 `推测置信度`
- 用一句短中文写 `推测依据`

重点判断这 4 个维度：

- `Metrics缺失`
- `链路追踪缺失`
- `Redis指标缺失`
- `Pg指标缺失`

允许输出：

- `是`
- `否`
- `未知`

## Output Contract

worker 最终必须返回一条结构化结果，字段与 `telemetry-audit-results.csv` 一致：

- `服务名称`
- `命名空间`
- `业务归属`
- `编程语言`
- `仓库地址`
- `仓库名`
- `本地仓库路径`
- `分支`
- `推测框架`
- `推测置信度`
- `推测依据`
- `仓库准备状态`
- `审计结论`
- `Metrics缺失`
- `链路追踪缺失`
- `Redis指标缺失`
- `Pg指标缺失`
- `检查摘要`
- `备注`

## 审计结论映射

- 任一维度为 `是` -> `发现问题`
- 四个维度全为 `否` -> `通过`
- 依赖缺失、仓库不可读、判断无法完成 -> `阻塞`
- 本轮明确跳过 -> `跳过`

## Return Format

建议 worker 返回严格 JSON 对象，避免调度器做自然语言解析。

### `推测框架`

只允许输出 `framework-inference.md` 里定义的固定枚举：

- `Kratos`
- `Gin`
- `Echo`
- `Koa`
- `Nest`
- `SpringBoot`
- `FrontendStatic`
- `TaskWorker`
- `Unknown`

### `推测置信度`

只允许输出：

- `高`
- `中`
- `低`

### `推测依据`

- 一句短中文
- 说明关键证据即可，例如入口文件、依赖名、中间件或目录结构
- 不要写成长段解释

### 语言优先级

- `编程语言` 来源于飞书 Base，作为主参考
- 若仓库结构与飞书语言冲突，优先保留飞书语言，不要在结果里覆盖它
- 冲突信息写到 `推测依据` 或 `备注`，例如“飞书标注 Go，但仓内主入口更像前端静态仓”
- 如果 `编程语言` 不是 `Go / Node`，默认不应该进入本 worker

### `Unknown` 兜底

- 无法稳定识别框架时，输出 `推测框架 = Unknown`
- 不要因为识别不到框架就停止审计
- 继续按通用规则判断四个缺失维度，并在 `备注` 中说明不确定性来源

例如：

```json
{
  "服务名称": "study-plan",
  "命名空间": "7to12",
  "业务归属": "学习工具",
  "编程语言": "Go",
  "仓库地址": "https://gitlab.yc345.tv/backend/study-plan",
  "仓库名": "study-plan",
  "本地仓库路径": "/abs/path/to/repo",
  "分支": "master",
  "推测框架": "Kratos",
  "推测置信度": "高",
  "推测依据": "go.mod 与 internal/server/http.go、grpc.go 明确显示是 Kratos 服务",
  "仓库准备状态": "就绪",
  "审计结论": "发现问题",
  "Metrics缺失": "是",
  "链路追踪缺失": "否",
  "Redis指标缺失": "未知",
  "Pg指标缺失": "否",
  "检查摘要": "Metrics=是；链路追踪=否；Redis=未知；Pg=否",
  "备注": "未发现 Metrics 接入；Redis 使用情况不明确"
}
```
