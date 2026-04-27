# Resolve Repos Checkpoint

## Stage Goal

这一阶段负责：

1. 读取服务清单
2. 解析 GitLab 仓库
3. 生成 `repo-resolution.csv`
4. 在人工确认点停下

默认读取 `应用总表` 后按脚本规则过滤有效服务范围，不依赖飞书视图里的人肉筛选。
同时默认要求 `运行环境` 包含 `正式环境`，非正式环境服务不进入第一阶段产物。
同时默认尝试读取飞书里的 `编程语言`（按 `编程语言 / 开发语言 / 语言` 顺序自动探测），并透传到后续产物。

## Artifact Set

默认使用：

```text
./telemetry-audit/
├── service-inventory.json
└── repo-resolution.csv
```

## Stop Condition

默认在以下时机停止：

- 已生成 `repo-resolution.csv`
- 存在 `needs_confirm`
- 存在 `not_found`
- 用户明确要求先人工确认

## Next Step

用户修订完 `repo-resolution.csv` 后，再执行：

```text
/telemetry:audit-from-csv
```
