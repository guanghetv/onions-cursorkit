# Audit From CSV Checkpoint

## Stage Goal

这一阶段负责：

1. 读取已确认的 `repo-resolution.csv`
2. 由调度器筛选 `Go / Node` 可执行仓库
3. 对 `Python / 其他 / 空语言` 直接写入 `跳过`
4. 小并发调度单仓 subagent worker 做只读检查
5. 在审计结果之上派生 `接入模板 / 运行形态 / 适用性矩阵`
6. 生成可直接筛选的 `telemetry-audit-results.csv`
7. 汇总检查结果

单仓 worker 默认只处理 `编程语言 = Go / Node` 的服务，并先读取飞书透传的 `编程语言`，再参考 `framework-inference.md` 推测框架，并结合本地 vendored 的 `telemetry-instrument.md` 与审计 checklist 做只读检查，而不是口头约定。

## Artifact Set

默认使用：

```text
./telemetry-audit/
├── repo-resolution.csv
└── telemetry-audit-results.csv
```

## Reuse Rules

- 有 `repo-resolution.csv` 时，默认复用仓库确认结果
- 有 `telemetry-audit-results.csv` 时，默认跳过已有最终结果的服务
- 但如果旧结果缺少当前契约要求的 `编程语言`、框架推测字段、接入模板、适用性矩阵或执行跟踪列，应该视为结果不完整，允许重跑并补齐
- 只有用户明确要求刷新，才重跑对应阶段

## Scheduler Responsibilities

调度器负责：

- 读取 `repo-resolution.csv`
- 过滤 `自动匹配` / `人工确认仓库地址` 非空的行
- 过滤 `编程语言 = Go / Node` 的执行范围
- 为 `Python / 其他 / 空语言` 直接生成 `跳过` 结果
- 控制小并发 worker 数
- 准备本地 repo cache
- 基于 `编程语言 + 推测框架 + 审计结果` 派生 `接入模板 / 运行形态 / 适用性矩阵`
- 串行写入 `telemetry-audit-results.csv`
- 保留已有 `负责人 / MR地址 / Commit哈希` 等执行跟踪字段
- 汇总最终统计

调度器不负责：

- 直接用硬编码脚本判断仓库内容
- 重新搜索 GitLab
- 修改代码或提 MR

## Worker Responsibilities

单仓 worker 负责：

- 进入单个本地仓库
- 仅处理已通过语言门禁的 `Go / Node` 仓库
- 参考 telemetry 规范做只读检查
- 返回一条标准化结果

单仓 worker 不负责：

- 读取整份 `repo-resolution.csv`
- 决定批次并发
- 直接写总 CSV

## Stop Condition

遇到以下情况要停止并说明原因：

- `repo-resolution.csv` 不存在
- CSV 中没有任何已确认仓库
- 单仓检查依赖缺失，导致全部或大面积 `阻塞`
- worker 结果不符合单行契约，无法安全落盘
