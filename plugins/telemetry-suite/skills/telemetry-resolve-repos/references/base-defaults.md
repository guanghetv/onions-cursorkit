# Base Defaults

## Default Data Source

- Base token: `IFj7bGDJTaKxo7s7A7VcUPsqnDf`
- Table id: `tblBJH3FuUHuhrGO`
- Table name: `Kubernetes容器服务`
- Default view id: `vewOpKcL8Y`
- Default view name: `应用总表`

## Alternative Views

- `vewOpKcL8Y` - `应用总表`
- `vewhn2hwl0` - `后端应用`
- `vewL6YKFZm` - `前端应用`
- `vewXgtmApG` - `网关应用`
- `vewMTP7y9D` - `定时任务`

## Default Fields

- `服务名称`
- `命名空间`
- `服务类型`
- `业务归属`
- `运行环境`
- `编程语言`
- `状态`
- `Metrics指标采集`
- `链路追踪接入`
- `Redis连接池指标上报`
- `Pg连接池指标上报`

## Default Filter Rules

读取 `应用总表` 后，再按脚本规则过滤，不依赖人工维护的飞书视图筛选：

- 只保留 `服务类型 = 后端`
- 只保留 `运行环境` 包含 `正式环境`
- 排除 `状态 = 待下线`
- 排除 `状态 = 已下线`
- 排除这些 `业务归属`：
  - `测试技术支撑`
  - `运维`
  - `工程效率`
  - `未知`
  - `技术战共创`
  - `数据中台`
  - `APP组`

## Checkbox Semantics

这些字段是 checkbox：

- `Metrics指标采集`
- `链路追踪接入`
- `Redis连接池指标上报`
- `Pg连接池指标上报`

读取后统一保留三态：

- `true`
- `false`
- `null`

禁止把 `false` 和 `null` 合并。

## Programming Language Fallback

飞书语言字段默认按以下顺序自动探测：

1. `编程语言`
2. `开发语言`
3. `语言`

命中后透传到后续产物；若都不存在，则保留为空字符串，不阻断流程。
