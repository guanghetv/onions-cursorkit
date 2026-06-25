# 状态管理

## 状态来源

本仓库没有前端全局状态库。状态主要来自文件和工作流产物：

| 状态 | 路径 | 管理方式 |
|------|------|----------|
| 插件市场 | `.cursor-plugin/marketplace.json` | 手工维护，正式插件需注册 |
| 插件 manifest | `plugins/*/.cursor-plugin/plugin.json` | 插件内维护 |
| OpenSpec 变更 | `openspec/changes/**` | OpenSpec CLI + Agent 写 Markdown |
| Trellis 任务 | `.trellis/tasks/**/task.json` | `.trellis/scripts/task.py` |
| Trellis journal | `.trellis/workspace/<developer>/journal-*.md` | `.trellis/scripts/add_session.py` |
| 轻量试点状态 | 如 `.onion-sdd/current.json` 模板 | 插件命令约定维护 |

## OpenSpec 状态

OpenSpec 变更目录是需求/设计/验证状态的主要载体。命令或 skill 如果需要恢复状态，应优先读取：

- `proposal.md`
- `tasks.md`
- `specs/**/spec.md`
- `backend-*.md`
- `qa-*.md`
- `e2e-report.md`

不要把 OpenSpec 产物写到变更目录之外。

## Trellis 状态

Trellis 状态由脚本管理，不要手动编辑 runtime 指针：

- 查看上下文：`python3 ./.trellis/scripts/get_context.py`
- 设置当前任务：`python3 ./.trellis/scripts/task.py start <task>`
- 完成当前任务：`python3 ./.trellis/scripts/task.py finish`
- 归档任务：`python3 ./.trellis/scripts/task.py archive <task>`

如果只是插件自身状态，优先设计插件目录内的模板或说明；不要让插件命令直接依赖 Trellis runtime，除非任务明确是 Trellis 集成。

## Metrics 与记录

度量字段可以放入状态 JSON 或验证报告，但 Phase 0 这类试点不应依赖外部指标平台。示例见 `plugins/onion-sdd/templates/current.example.json`。

## 常见错误

- 直接手改 `.trellis/.runtime/`。
- 将运行时状态写入 README 而没有模板或字段说明。
- 在未归档 OpenSpec 变更时跳过 `tasks.md` / `e2e-report.md` 的检查。
